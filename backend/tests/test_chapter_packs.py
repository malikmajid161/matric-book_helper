from copy import deepcopy

import pymupdf
import pytest

from rag.chapter_packs import chapter_pack
from rag.ingest import digest


@pytest.fixture
def textbook(tmp_path):
    directory = tmp_path / 'books'
    directory.mkdir()
    path = directory / 'physics.pdf'
    with pymupdf.open() as pdf:
        for text in ['Cover page', 'Energy is conserved in a closed system.', 'Kinetic energy depends on the motion of particles.', 'An unrelated chapter about sound.']:
            pdf.new_page().insert_text((50, 50), text)
        pdf.save(path)
    book = {'id': 'physics', 'title': 'Physics', 'edition': 'Fixture', 'filename': 'physics.pdf',
        'sha256': digest(path), 'version': 'review-1', 'status': 'ready', 'chapters': [
            {'number': 10, 'title': 'Energy', 'start_page': 2, 'end_page': 3,
             'pages': [{'page_number': 2, 'text': 'Energy is conserved in a closed system.'}, {'page_number': 3, 'text': 'Kinetic energy depends on the motion of particles.'}],
             'topics': [], 'exercises': [
                 {'id': '10.1', 'text': 'Define kinetic energy.', 'page_number': 3, 'solution_status': 'checked', 'solution': 'Energy of motion.'},
                 {'id': '10.2', 'text': 'Explain energy conservation.', 'page_number': 2, 'solution_status': 'needs_review'},
             ]},
            {'number': 11, 'title': 'Sound', 'start_page': 4, 'end_page': 4, 'pages': [], 'topics': [], 'exercises': []},
        ]}
    return tmp_path, book


def test_chapter_pdf_pages_original_citations_and_verified_cache(textbook):
    directory, book = textbook
    result = chapter_pack(book, 10, directory)
    bundle = result['bundle']
    with pymupdf.open(result['pdf_path']) as pdf:
        assert len(pdf) == 2
        assert 'Energy is conserved' in pdf[0].get_text()
        assert 'Kinetic energy' in pdf[1].get_text()
        assert all('sound' not in page.get_text() for page in pdf)
    assert bundle['sha256'] == digest(result['pdf_path'])
    assert bundle['md5'] == digest(result['pdf_path'], 'md5')
    assert bundle['original_pdf_sha256'] == book['sha256']
    assert bundle['pdf_page_offset'] == 1
    assert {row['page_number'] for row in bundle['offline_index']['documents']} == {2, 3}
    assert bundle['solution_coverage'] == {'checked': 1, 'total': 2, 'pending': 1}
    before = result['pdf_path'].stat().st_mtime_ns
    cached = chapter_pack(book, 10, directory)
    assert cached['bundle'] == bundle and cached['pdf_path'].stat().st_mtime_ns == before
    # Study updates change the bundle, but never redownload/resplit the unchanged PDF.
    book['chapters'][0]['exercises'][1].update(solution_status='checked', solution='The total is unchanged.')
    updated = chapter_pack(book, 10, directory)
    assert updated['bundle']['version'] != bundle['version']
    assert updated['pdf_path'].stat().st_mtime_ns == before


def test_chapter_scope_bounds_and_source_hash_rejected(textbook):
    directory, book = textbook
    with pytest.raises(ValueError, match='Chapter not found'):
        chapter_pack(book, 999, directory)
    for bad in [True, '10', -1]:
        with pytest.raises(ValueError, match='chapter number'):
            chapter_pack(book, bad, directory)
    wrong = deepcopy(book)
    wrong['id'] = '../physics'
    with pytest.raises(ValueError, match='identifier'):
        chapter_pack(wrong, 10, directory)
    wrong = deepcopy(book)
    wrong['chapters'][0]['end_page'] = 8
    with pytest.raises(ValueError, match='boundaries'):
        chapter_pack(wrong, 10, directory)
    wrong = deepcopy(book)
    wrong['chapters'][0]['pages'][0]['page_number'] = 4
    with pytest.raises(ValueError, match='outside chapter'):
        chapter_pack(wrong, 10, directory)
    wrong = deepcopy(book)
    wrong['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='checksum'):
        chapter_pack(wrong, 10, directory)


def test_reader_pack_never_indexes_unreviewed_draft_text(textbook):
    directory, book = textbook
    book.update(status='readable', reader_only=True)
    result = chapter_pack(book, 10, directory)
    assert result['bundle']['status'] == 'readable'
    assert result['bundle']['offline_index'] is None
    assert result['bundle']['chapters'][0]['pages'] == []
    assert result['bundle']['solution_coverage']['total'] == 0
    assert book['chapters'][0]['pages']  # caller's catalog is not mutated
