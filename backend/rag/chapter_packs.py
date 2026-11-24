"""Persistent per-chapter downloads with original textbook page references.

Only already indexed/reviewed chapter text is used for vectors. Reader-only books
still receive a chapter PDF, without promoting OCR drafts into searchable content.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

import pymupdf

from rag.ingest import digest
from rag.offline_vectors import MODEL_VERSION, build_index

PACK_VERSION = 'chapter-pack-1'


def _atomic_json(path, payload):
    descriptor, name = tempfile.mkstemp(prefix=path.stem + '-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, ensure_ascii=False, separators=(',', ':'))
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def _validate_chapter(chapter, page_count):
    start, end = chapter.get('start_page'), chapter.get('end_page')
    if type(start) is not int or type(end) is not int or start < 1 or end < start or end > page_count:
        raise ValueError('Invalid chapter PDF page boundaries')
    for page in chapter.get('pages', []):
        number = page.get('page_number')
        if type(number) is not int or not start <= number <= end:
            raise ValueError('Reviewed text page lies outside chapter')
    for row in chapter.get('topics', []) + chapter.get('exercises', []):
        if type(row.get('page_number')) is not int or not start <= row['page_number'] <= end:
            raise ValueError('Study item lies outside chapter')
    return start, end


def chapter_pack(book, chapter_number, data_dir):
    """Return ``{bundle, pdf_path, bundle_path}`` for one original chapter.

    ``bundle.sha256``/``md5`` identify the smaller PDF, whereas citations and
    chapter page numbers remain 1-based full-book PDF pages. Subtract
    ``pdf_page_offset`` when selecting a page in this pack's PDF viewer.
    """
    identifier = book.get('id', '')
    if not isinstance(identifier, str) or not re.fullmatch(r'[a-z0-9-]+', identifier):
        raise ValueError('Invalid book identifier')
    if type(chapter_number) is not int or chapter_number < 1:
        raise ValueError('Invalid chapter number')
    matches = [row for row in book.get('chapters', []) if row.get('number') == chapter_number]
    if len(matches) != 1:
        raise ValueError('Chapter not found or ambiguous')
    chapter = deepcopy(matches[0])
    filename = book.get('filename', '')
    if not isinstance(filename, str) or not filename or Path(filename).name != filename or '/' in filename or '\\' in filename:
        raise ValueError('Invalid source PDF filename')
    expected_sha = book.get('sha256', '')
    if not isinstance(expected_sha, str) or not re.fullmatch(r'[a-f0-9]{64}', expected_sha):
        raise ValueError('Source PDF checksum is required')
    data_dir = Path(data_dir).resolve()
    books_dir = (data_dir / 'books').resolve()
    source = (books_dir / filename).resolve()
    if source.parent != books_dir or not source.is_file():
        raise ValueError('Source PDF is outside the books directory or missing')
    if digest(source) != expected_sha:
        raise ValueError('Source PDF checksum differs from verified book')
    cache = data_dir / 'chapter_packs'
    cache.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(source) as original:
        start, end = _validate_chapter(chapter, len(original))
        key = hashlib.sha256(f'{PACK_VERSION}:{expected_sha}:{start}:{end}'.encode()).hexdigest()
        stem = f'{identifier}-{chapter_number}-{key}'
        pdf_path = cache / (stem + '.pdf')
        bundle_path = cache / (stem + '.json')
        reusable = False
        if pdf_path.is_file():
            try:
                with pymupdf.open(pdf_path) as existing:
                    reusable = len(existing) == end - start + 1
                if bundle_path.is_file():
                    previous = json.loads(bundle_path.read_text(encoding='utf-8'))
                    reusable = reusable and previous.get('sha256') == digest(pdf_path)
            except (ValueError, RuntimeError, OSError):
                reusable = False
        if not reusable:
            descriptor, temporary = tempfile.mkstemp(prefix=stem + '-', suffix='.pdf', dir=cache)
            os.close(descriptor)
            try:
                with pymupdf.open() as pack:
                    pack.insert_pdf(original, from_page=start - 1, to_page=end - 1)
                    pack.save(temporary, garbage=4, deflate=True)
                os.replace(temporary, pdf_path)
            finally:
                Path(temporary).unlink(missing_ok=True)
    # A book being reader-only never implies its OCR drafts were reviewed.
    indexed = book.get('status') == 'ready' and not book.get('reader_only', False)
    if not indexed:
        chapter.update(pages=[], topics=[], exercises=[])
    exercises = chapter.get('exercises', [])
    solved = sum(row.get('solution_status') == 'checked' and bool(row.get('solution')) for row in exercises)
    study_fingerprint = hashlib.sha256(json.dumps({
        'pack': key, 'book_version': book.get('version'), 'chapter': chapter,
        'vector_model': MODEL_VERSION, 'indexed': indexed,
    }, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if bundle_path.is_file():
        try:
            previous = json.loads(bundle_path.read_text(encoding='utf-8'))
            if previous.get('version') == study_fingerprint and previous.get('sha256') == digest(pdf_path):
                return {'bundle': previous, 'pdf_path': pdf_path, 'bundle_path': bundle_path}
        except (ValueError, OSError):
            pass
    bundle = {
        'id': identifier, 'title': book.get('title', identifier), 'edition': book.get('edition', ''),
        'chapter_number': chapter_number, 'chapter_title': chapter['title'],
        'version': study_fingerprint, 'sha256': digest(pdf_path), 'md5': digest(pdf_path, 'md5'),
        'source_book_version': book.get('version'),
        'bytes': pdf_path.stat().st_size, 'original_pdf_sha256': expected_sha,
        'pdf_page_offset': start - 1, 'chapters': [chapter],
        'offline_index': build_index([chapter]) if indexed else None,
        'solution_coverage': {'checked': solved, 'total': len(exercises), 'pending': len(exercises) - solved},
        'inventory_complete': False,
        'coverage_note': 'Counts describe recorded questions only. Complete chapter exercise coverage has not been certified.',
        'status': 'ready' if indexed else 'readable',
    }
    _atomic_json(bundle_path, bundle)
    return {'bundle': bundle, 'pdf_path': pdf_path, 'bundle_path': bundle_path}
