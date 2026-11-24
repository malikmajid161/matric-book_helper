from copy import deepcopy

from rag.coverage import book_coverage


def fixture():
    return {'id': 'physics', 'status': 'ready', 'text_origin': 'machine_transcribed',
        'reviewed_pdf_pages': [4], 'chapters': [
            {'number': 10, 'title': 'Energy', 'reviewed_page_count': 20,
             'pages': [{'page_number': 4, 'text': 'Machine extracted energy text.'}],
             'exercises': [{'solution_status': 'ai_checked', 'solution': 'An AI draft.'},
                           {'solution_status': 'checked', 'solution': ' '},
                           {'solution_status': 'checked', 'solution': 'A checked solution.'}]}]}


def test_machine_ocr_never_inferred_as_verified_or_solved():
    result = book_coverage(fixture())
    assert result['indexed_pages'] == 1 and result['machine_ocr_pages'] == 1
    assert result['explicitly_reviewed_pages'] == 0
    assert result['recorded_questions'] == 3 and result['checked_solutions'] == 1
    assert result['pending_recorded_solutions'] == 2
    assert 'not marked human-verified' in result['coverage_note']


def test_missing_inventory_and_zero_pending_do_not_claim_all_solved():
    book = fixture()
    book['chapters'][0]['exercises'] = [{'solution_status': 'checked', 'solution': 'Done.'}] * 17
    result = book_coverage(book)
    assert result['recorded_questions'] == 17
    assert result['pending_recorded_solutions'] == 0
    assert result['inventory_complete'] is False
    assert 'additional questions may be missing' in result['coverage_note']
    assert 'does not prove' in result['coverage_note']
    book['exercise_inventory_complete'] = 'true'
    assert book_coverage(book)['inventory_complete'] is False
    book['exercise_inventory_complete'] = True
    assert book_coverage(book)['inventory_complete'] is True


def test_empty_reader_only_and_source_metadata_stay_independent():
    book = fixture()
    original = deepcopy(book)
    result = book_coverage(book)
    result['chapters'][0]['chapter_title'] = 'Changed result'
    assert book == original
    reader = {**book, 'status': 'readable', 'reader_only': True}
    assert book_coverage(reader)['indexed_pages'] == 0
    empty = book_coverage({'id': 'mathematics', 'chapters': []})
    assert empty['total_chapters'] == 0 and not empty['inventory_complete']
