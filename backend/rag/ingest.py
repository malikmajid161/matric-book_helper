"""Verified, page-preserving ingestion. Manifest chapter pages are 1-based PDF pages."""
import hashlib
import json
import re
from pathlib import Path

PIPELINE_VERSION = '5'


def digest(path: Path, algorithm='sha256') -> str:
    with path.open('rb') as file:
        return hashlib.file_digest(file, algorithm).hexdigest()


def read_manifest(data_dir: Path) -> list[dict]:
    books = json.loads((data_dir / 'books' / 'manifest.json').read_text(encoding='utf-8'))
    for book in books:
        if book.get('study_sha256'):
            path = data_dir / 'books' / (book['id'] + '.study.json')
            if not path.is_file() or digest(path) != book['study_sha256']:
                raise ValueError('Reviewed study data checksum does not match')
            study = json.loads(path.read_text(encoding='utf-8'))
            if study.get('pdf_sha256') != book['sha256']:
                raise ValueError('Study data is for a different PDF')
            for chapter in book['chapters']:
                chapter.update(study.get('chapters', {}).get(str(chapter['number']), {}))
    return books


def validate_book(book: dict, path: Path):
    if not re.fullmatch(r'[a-z][a-z0-9-]*', book['id']) or Path(book['filename']).name != book['filename']:
        raise ValueError('Invalid book identifier or filename')
    if not book.get('sha256') or digest(path) != book['sha256']:
        raise ValueError('PDF checksum is missing or does not match the verified manifest')
    if (not book.get('chapters') and not book.get('reader_only')) or book['edition'] == 'Pending verification':
        raise ValueError('Edition and chapter boundaries need verification')
    if book.get('ocr_sha256'):
        sidecar = path.with_suffix('.pages.json')
        if not sidecar.is_file() or digest(sidecar) != book['ocr_sha256']:
            raise ValueError('Reviewed OCR sidecar checksum does not match')


def token_chunks(text: str, tokenizer, size=220, overlap=30):
    # MiniLM truncates at 256 tokens. Smaller chunks preserve all embedded text.
    tokens = tokenizer.encode(text, add_special_tokens=False)
    for start in range(0, len(tokens), size - overlap):
        yield tokenizer.decode(tokens[start:start + size], skip_special_tokens=True)
        if start + size >= len(tokens):
            break


def extract_book(book: dict, path: Path, tokenizer):
    import fitz
    records, chapters = [], []
    sidecar = path.with_suffix('.pages.json')
    ocr = json.loads(sidecar.read_text(encoding='utf-8')) if book.get('ocr_sha256') else {}
    with fitz.open(path) as pdf:
        bounds = sorted(book['chapters'], key=lambda chapter: chapter['start_page'])
        if len({c['number'] for c in bounds}) != len(bounds):
            raise ValueError('Chapter numbers must be unique')
        for pos, chapter in enumerate(bounds):
            start = chapter['start_page']
            end = chapter.get('end_page', bounds[pos + 1]['start_page'] - 1 if pos + 1 < len(bounds) else len(pdf))
            if start < 1 or end < start or end > len(pdf):
                raise ValueError('Invalid chapter PDF page boundaries')
            pages = []
            for number in range(start, end + 1):
                if book.get('reviewed_pages_only') and str(number) not in ocr:
                    continue
                text = ocr.get(str(number), pdf[number - 1].get_text(sort=True)).strip()
                text = re.sub(r'(?im)^\s*(Web\s+Version\s+of\s+PECTAA.*|Not\s+for\s+Sale)\s*$', '', text).strip()
                if len(text) < 40:
                    if book.get('text_origin') == 'machine_transcribed':
                        continue
                    raise ValueError(f'PDF page {number} has insufficient text; OCR/review required')
                pages.append({'page_number': number, 'text': text})
                for index, chunk in enumerate(token_chunks(text, tokenizer)):
                    records.append({'id': f"{book['id']}:{number}:{index}", 'text': chunk,
                                    'book': book['id'], 'chapter_number': chapter['number'],
                                    'chapter_title': chapter['title'], 'page_number': number,
                                    'text_origin': book.get('text_origin', 'native')})
            # Topics/exercises are curated manifest entries, never guessed from a scan.
            topics = chapter.get('topics', [])
            exercises = chapter.get('exercises', [])
            for item in topics + exercises:
                if not start <= item['page_number'] <= end:
                    raise ValueError('Topic/exercise lies outside its chapter')
            chapters.append({**chapter, 'end_page': end, 'topics': topics,
                             'exercises': exercises, 'pages': pages,
                             'reviewed_page_count': len(pages)})
    return records, chapters


def ingest(data_dir: Path, collection, model):
    catalog = []
    for book in read_manifest(data_dir):
        path = data_dir / 'books' / book['filename']
        item = {**book, 'status': 'missing', 'chapters': [], 'bytes': 0}
        if path.is_file():
            try:
                validate_book(book, path)
                if book.get('reader_only'):
                    collection.delete(where={'book': book['id']})
                    version = hashlib.sha256((book['sha256'] + json.dumps(book, sort_keys=True)).encode()).hexdigest()
                    item.update(status='readable', bytes=path.stat().st_size, version=version,
                                chapters=[{**chapter, 'topics': [], 'exercises': [], 'pages': []} for chapter in book.get('chapters', [])])
                    catalog.append(item)
                    continue
                records, chapters = extract_book(book, path, model.tokenizer)
                version = hashlib.sha256((book['sha256'] + PIPELINE_VERSION + json.dumps(book, sort_keys=True)).encode()).hexdigest()
                existing = collection.get(where={'book': book['id']}, limit=1)
                if not existing['ids'] or existing['metadatas'][0].get('version') != version:
                    collection.delete(where={'book': book['id']})
                    for offset in range(0, len(records), 32):
                        batch = records[offset:offset + 32]
                        embeddings = model.encode([row['text'] for row in batch], normalize_embeddings=True).tolist()
                        collection.upsert(ids=[row['id'] for row in batch], documents=[row['text'] for row in batch],
                                          embeddings=embeddings, metadatas=[{key: value for key, value in row.items() if key not in ('id', 'text')} | {'version': version} for row in batch])
                item.update(status='ready', chapters=chapters, bytes=path.stat().st_size, version=version)
            except (ValueError, RuntimeError, KeyError) as error:
                item.update(status='needs_review', error=str(error))
                collection.delete(where={'book': book['id']})
        else:
            collection.delete(where={'book': book['id']})
        catalog.append(item)
    return catalog
