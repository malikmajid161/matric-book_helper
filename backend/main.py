import asyncio
import hmac
import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from config import settings
from rag.ingest import ingest, read_manifest, digest
from rag.retriever import Retriever
from rag.generator import Generator
from auth import profile_list, login, check_session

log = logging.getLogger('ptb')
state = {'status': 'starting', 'catalog': [], 'error': None}
pool = ThreadPoolExecutor(max_workers=1)
ai_slots = asyncio.Semaphore(2)
rate = defaultdict(deque)


def initialize():
    try:
        if settings.retrieval_mode == 'lexical':
            from rag.lexical import prepare
            catalog, retriever = prepare(settings.data_dir)
            state.update(catalog=catalog, retriever=retriever,
                         generator=Generator(settings.gemini_api_key, settings.gemini_model), status='ready')
            return
        import chromadb
        from sentence_transformers import SentenceTransformer
        import torch
        torch.set_num_threads(2)
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(settings.data_dir / 'chroma_db'))
        collection = client.get_or_create_collection('ptb_minilm_v3', metadata={'hnsw:space': 'cosine'})
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')
        catalog = ingest(settings.data_dir, collection, model)
        state.update(catalog=catalog, retriever=Retriever(collection, model, settings.max_distance),
                     generator=Generator(settings.gemini_api_key, settings.gemini_model), status='ready')
    except Exception:
        log.exception('Textbook initialization failed')
        state.update(status='failed', error='Textbook initialization failed; check server logs.')


@asynccontextmanager
async def lifespan(app):
    task = asyncio.get_running_loop().run_in_executor(pool, initialize)
    yield
    await task


app = FastAPI(title='PTB Scholar', version='1.0.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(',')],
                   allow_methods=['GET', 'POST'], allow_headers=['Content-Type', 'X-Study-Code', 'Authorization'])


def authorize(request: Request):
    check_session(request)
    if settings.study_access_code and not hmac.compare_digest(request.headers.get('X-Study-Code', ''), settings.study_access_code):
        raise HTTPException(401, 'Enter the study access code in Settings.')


def ready_book(book: str, allow_reader: bool = False):
    if state['status'] != 'ready':
        raise HTTPException(503, 'Textbooks are being prepared. Retry shortly.')
    item = next((row for row in state['catalog'] if row['id'] == book), None)
    if item is None:
        raise HTTPException(404, 'Book not found')
    if item['status'] != 'ready' and not (allow_reader and item['status'] == 'readable'):
        raise HTTPException(409, 'This textbook has not been verified and indexed yet.')
    return item


@app.get('/health')
def health():
    return {'status': state['status'], 'ai_configured': bool(settings.gemini_api_key),
            'books_ready': sum(row['status'] == 'ready' for row in state['catalog']), 'error': state['error'], 'retrieval_mode': settings.retrieval_mode}


@app.get('/profiles')
def get_profiles():
    return profile_list()


class Login(BaseModel):
    profile_id: str = Field(max_length=50)
    code: str = Field(min_length=1, max_length=128)


@app.post('/login')
def sign_in(body: Login, request: Request):
    return login(body.profile_id, body.code, request.client.host if request.client else 'unknown')


@app.get('/books', dependencies=[Depends(authorize)])
def books():
    catalog = state['catalog'] or [{**row, 'status': 'preparing', 'bytes': 0} for row in read_manifest(settings.data_dir)]
    return [{key: value for key, value in row.items() if key not in ('filename', 'error', 'source_url', 'chapters', 'offline_index')} |
            {'chapters': [{key: value for key, value in chapter.items() if key != 'pages'} for chapter in row['chapters']]} for row in catalog]


@app.get('/books/{book}/download', dependencies=[Depends(authorize)])
def download(book: str):
    item = ready_book(book, allow_reader=True)
    return FileResponse(settings.data_dir / 'books' / item['filename'], media_type='application/pdf',
                        filename=item['filename'], headers={'ETag': f'"{item["sha256"]}"'})


@app.get('/books/{book}/bundle', dependencies=[Depends(authorize)])
def bundle(book: str):
    item = ready_book(book, allow_reader=True)
    if 'md5' not in item:
        item['md5'] = digest(settings.data_dir / 'books' / item['filename'], 'md5')
    if 'offline_index' not in item:
        from rag.offline_vectors import build_index
        item['offline_index'] = build_index(item['chapters'])
    return {key: item[key] for key in ('id', 'title', 'edition', 'version', 'sha256', 'md5', 'chapters', 'offline_index')}


@app.get('/chapters/{book}', dependencies=[Depends(authorize)])
def chapters(book: str):
    return [{key: value for key, value in row.items() if key != 'pages'} for row in ready_book(book, allow_reader=True)['chapters']]


@app.get('/books/{book}/chapters/{chapter}/bundle', dependencies=[Depends(authorize)])
def chapter_bundle(book: str, chapter: int):
    from rag.chapter_packs import chapter_pack
    try:
        return chapter_pack(ready_book(book, allow_reader=True), chapter, settings.data_dir)['bundle']
    except (ValueError, KeyError) as error:
        raise HTTPException(404, str(error)) from None


@app.get('/books/{book}/chapters/{chapter}/download', dependencies=[Depends(authorize)])
def chapter_download(book: str, chapter: int):
    from rag.chapter_packs import chapter_pack
    try:
        pack = chapter_pack(ready_book(book, allow_reader=True), chapter, settings.data_dir)
    except (ValueError, KeyError) as error:
        raise HTTPException(404, str(error)) from None
    return FileResponse(pack['pdf_path'], media_type='application/pdf', filename=f'{book}-chapter-{chapter}.pdf')


@app.get('/topics/{book}/{chapter}', dependencies=[Depends(authorize)])
def topics(book: str, chapter: int):
    item = next((row for row in ready_book(book)['chapters'] if row['number'] == chapter), None)
    if item is None:
        raise HTTPException(404, 'Chapter not found')
    return item


@app.get('/search', dependencies=[Depends(authorize)])
async def search(q: str = Query(min_length=2, max_length=2000), book: str = 'physics', chapter: int | None = None):
    ready_book(book)
    return await asyncio.get_running_loop().run_in_executor(pool, state['retriever'].search, q, book, chapter)


class Ask(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    book: str
    chapter: int | None = None
    book_version: str | None = None
    mode: str = Field(default='answer', pattern='^(answer|explain|example)$')


@app.post('/ask', dependencies=[Depends(authorize)])
async def ask(body: Ask, request: Request):
    book = ready_book(body.book, allow_reader=True)
    if body.book_version and body.book_version != book['version']:
        raise HTTPException(409, 'Your saved study data has been updated. Refresh the book before asking AI.')
    if not body.question.strip():
        raise HTTPException(422, 'Question cannot be blank')
    from rag.exercises import resolve_exercise
    resolved = resolve_exercise(body.question, book, body.chapter)
    if resolved is not None and body.mode == 'answer':
        from rag.source_pages import attach_source_pages
        return attach_source_pages(resolved, book)
    if len(body.question.split()) < 3 and body.question.strip().lower() in {'help', 'solve', 'explain', 'answer', 'solution', 'soltion'}:
        return {'answer': '## Which question?\nType a topic, a complete question, or an exercise reference such as “ex 1.1 q 2”. Choose the chapter if you know it.', 'supported': False, 'sources': []}
    if book['status'] == 'readable':
        return {'answer': '## Original PDF available\nThis book is saved for reading, but its text has not been indexed yet.\n\n## Next step\nOpen the saved PDF and include the full question. Exercise references will work as their questions are checked.', 'supported': False, 'sources': []}
    # Use direct client IP. Do not trust arbitrary forwarded headers.
    address = request.client.host if request.client else 'unknown'
    now = time.monotonic()
    for key in list(rate):
        while rate[key] and rate[key][0] < now - 60:
            rate[key].popleft()
        if not rate[key]:
            del rate[key]
    if len(rate[address]) >= 12:
        raise HTTPException(429, 'Please wait one minute before asking again.', headers={'Retry-After': '60'})
    rate[address].append(now)
    async with ai_slots:
        sources = await asyncio.get_running_loop().run_in_executor(pool, state['retriever'].search,
                                                                  body.question, body.book, body.chapter)
        try:
            images = None
            if book.get('text_origin') == 'machine_transcribed' and sources:
                from rag.page_evidence import page_images
                sources, images = await asyncio.get_running_loop().run_in_executor(
                    pool, page_images, settings.data_dir / 'books' / book['filename'], sources)
            result = await state['generator'].answer(body.question, sources, body.mode, images=images)
            from rag.source_pages import attach_source_pages
            return attach_source_pages(result, book)
        except RuntimeError as error:
            raise HTTPException(503, str(error)) from None
        except Exception:
            log.warning('AI generation or citation validation failed')
            raise HTTPException(502, 'AI could not produce a verified response. Please retry.') from None
