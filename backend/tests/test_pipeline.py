import asyncio
import json
from types import SimpleNamespace
import fitz
import pytest
from fastapi.testclient import TestClient

import main
from rag.ingest import digest, extract_book, token_chunks, validate_book
from rag.generator import Generator
from rag.retriever import Retriever
from rag.lexical import LexicalRetriever


class Tokenizer:
    def encode(self, text, add_special_tokens=False):
        return text.split()
    def decode(self, tokens, skip_special_tokens=True):
        return ' '.join(tokens)


def test_chunk_overlap_and_full_coverage():
    chunks = list(token_chunks(' '.join(str(number) for number in range(500)), Tokenizer()))
    assert len(chunks) == 3
    assert chunks[0].split()[-30:] == chunks[1].split()[:30]
    assert chunks[-1].split()[-1] == '499'


def test_extraction_preserves_pages_and_verified_boundaries(tmp_path):
    path = tmp_path / 'physics.pdf'
    pdf = fitz.open()
    for text in ['Waves transfer energy. A wave has a frequency and wavelength.', 'Sound travels through matter. Sound waves need a medium.']:
        pdf.new_page().insert_text((50, 50), text)
    pdf.save(path)
    pdf.close()
    book = {'id': 'physics', 'filename': 'physics.pdf', 'sha256': digest(path), 'edition': 'Test fixture',
            'chapters': [{'number': 12, 'title': 'Waves', 'start_page': 1}, {'number': 13, 'title': 'Sound', 'start_page': 2}]}
    validate_book(book, path)
    rows, chapters = extract_book(book, path, Tokenizer())
    assert [row['page_number'] for row in rows] == [1, 2]
    assert rows[1]['chapter_title'] == 'Sound'
    assert chapters[0]['end_page'] == 1
    with pytest.raises(ValueError, match='checksum'):
        validate_book({**book, 'sha256': 'invalid'}, path)


def test_scanned_pdf_refuses_ingestion(tmp_path):
    path = tmp_path / 'scan.pdf'
    pdf = fitz.open(); pdf.new_page(); pdf.save(path); pdf.close()
    with pytest.raises(ValueError, match='OCR'):
        extract_book({'id': 'physics', 'chapters': [{'number': 1, 'title': 'Test', 'start_page': 1}]}, path, Tokenizer())


def test_retrieval_filters_subject_chapter_and_weak_matches():
    class Collection:
        def get(self, **kwargs):
            return {'ids': ['one', 'two']}
        def query(self, **kwargs):
            assert kwargs['where'] == {'$and': [{'book': 'physics'}, {'chapter_number': 12}]}
            return {'ids': [['one', 'two']], 'documents': [['wave', 'unrelated']],
                    'metadatas': [[{'book': 'physics', 'chapter_number': 12, 'chapter_title': 'Waves', 'page_number': 4}] * 2], 'distances': [[0.2, 0.9]]}
    class Model:
        def encode(self, *args, **kwargs):
            return SimpleNamespace(tolist=lambda: [0.1])
    rows = Retriever(Collection(), Model(), 0.65).search('wave', 'physics', 12)
    assert len(rows) == 1 and rows[0]['citation'] == 1


def fake_generator(response):
    async def generate(**kwargs):
        return SimpleNamespace(text=json.dumps(response))
    value = Generator('', 'test')
    value.client = SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=generate)))
    return value


SOURCE = {'id': 'one', 'citation': 1, 'text': 'Waves transfer energy.'}


@pytest.mark.parametrize('response', [
    {'answer': 'Energy [8]', 'supported': True, 'citations': [8]},
    {'answer': 'Energy', 'supported': True, 'citations': [1]},
    {'answer': 'Energy [1]', 'supported': True, 'citations': []},
])
def test_invalid_ai_citations_rejected(response):
    with pytest.raises(ValueError):
        asyncio.run(fake_generator(response).answer('What transfers?', [SOURCE]))


def test_grounded_response_and_abstention():
    result = asyncio.run(fake_generator({'answer': 'Waves transfer energy [1].', 'supported': True, 'citations': [1]}).answer('What transfers?', [SOURCE]))
    assert result['supported'] and result['sources'] == [SOURCE]
    result = asyncio.run(Generator('', 'test').answer('What transfers?', []))
    assert not result['supported']


def test_api_missing_book_auth_and_validation(monkeypatch):
    monkeypatch.setattr(main.settings, 'student_profiles_json', '')
    monkeypatch.setitem(main.state, 'status', 'ready')
    monkeypatch.setitem(main.state, 'catalog', [{'id': 'physics', 'status': 'missing', 'chapters': []}])
    client = TestClient(main.app)
    assert client.get('/health').json()['books_ready'] == 0
    assert client.get('/books/physics/download').status_code == 409
    assert client.get('/chapters/unknown').status_code == 404
    assert client.post('/ask', json={'question': 'x', 'book': 'physics'}).status_code == 422
    monkeypatch.setattr(main.settings, 'study_access_code', 'fixture-code')
    assert client.get('/chapters/physics').status_code == 401
    assert client.get('/chapters/physics', headers={'X-Study-Code': 'fixture-code'}).status_code == 409


def test_lexical_retrieval_abstains_and_preserves_metadata():
    row = {'id': 'one', 'book': 'physics', 'chapter_number': 12, 'chapter_title': 'Waves', 'page_number': 5, 'text': 'Waves transfer energy through a medium.'}
    retriever = LexicalRetriever([row])
    assert retriever.search('energy medium', 'physics')[0]['page_number'] == 5
    assert retriever.search('energy medium', 'chemistry') == []
    assert retriever.search('photosynthesis chlorophyll', 'physics') == []


def test_named_profile_login_and_protected_download(monkeypatch):
    import hashlib
    import auth
    salt = b'test-profile-salt'
    profiles = [{'id': 'fixture', 'name': 'Fixture Student', 'salt': salt.hex(),
                 'hash': hashlib.scrypt(b'fixture-pass', salt=salt, n=16384, r=8, p=1).hex()}]
    monkeypatch.setattr(main.settings, 'student_profiles_json', json.dumps(profiles))
    monkeypatch.setattr(main.settings, 'study_access_code', '')
    monkeypatch.setitem(main.state, 'status', 'ready')
    monkeypatch.setitem(main.state, 'catalog', [{'id': 'physics', 'status': 'missing', 'chapters': []}])
    auth.attempts.clear()
    client = TestClient(main.app)
    assert client.get('/profiles').json() == [{'id': 'fixture', 'name': 'Fixture Student'}]
    assert client.get('/books').status_code == 401
    assert client.post('/login', json={'profile_id': 'fixture', 'code': 'wrong'}).status_code == 401
    result = client.post('/login', json={'profile_id': 'fixture', 'code': 'fixture-pass'})
    assert result.status_code == 200
    token = result.json()['token']
    assert client.get('/books', headers={'Authorization': f'Bearer {token}'}).status_code == 200


def test_publisher_watermark_is_not_treated_as_scanned_book_text(tmp_path):
    path = tmp_path / 'scan.pdf'
    pdf = fitz.open(); pdf.new_page().insert_text((50, 50), 'Web Version of PECTAA of Textbook\nNot for Sale'); pdf.save(path); pdf.close()
    with pytest.raises(ValueError, match='OCR'):
        extract_book({'id': 'mathematics', 'chapters': [{'number': 1, 'title': 'Test', 'start_page': 1}]}, path, Tokenizer())
