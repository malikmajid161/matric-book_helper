"""Honest catalog coverage counts; recorded questions are not a complete inventory."""


def _chapter_coverage(book, chapter):
    enabled = book.get('status') == 'ready' and not book.get('reader_only', False)
    pages = [page for page in chapter.get('pages', [])
             if enabled and isinstance(page.get('text'), str) and page['text'].strip()]
    # Count actual indexed page records, not reviewed_page_count (older ingestion
    # also used that field for machine OCR). Never infer human review from OCR.
    indexed = {page['page_number'] for page in pages}
    machine = {page['page_number'] for page in pages
               if page.get('text_origin', chapter.get('text_origin', book.get('text_origin'))) == 'machine_transcribed'}
    explicitly_reviewed = set(book.get('reviewed_pdf_pages', [])) | set(chapter.get('reviewed_pdf_pages', []))
    reviewed = {page['page_number'] for page in pages if page['page_number'] not in machine and
                (page['page_number'] in explicitly_reviewed or page.get('verification') == 'checked' or page.get('review_status') == 'checked')}
    questions = chapter.get('exercises', [])
    checked = sum(row.get('solution_status') == 'checked' and isinstance(row.get('solution'), str)
                  and bool(row['solution'].strip()) for row in questions)
    complete = chapter.get('exercise_inventory_complete') is True
    return {
        'chapter_number': chapter['number'], 'chapter_title': chapter.get('title', ''),
        'indexed_pages': len(indexed), 'machine_ocr_pages': len(machine),
        'explicitly_reviewed_pages': len(reviewed),
        'recorded_questions': len(questions), 'checked_solutions': checked,
        'pending_recorded_solutions': len(questions) - checked,
        'inventory_complete': complete,
        'coverage_note': _note(complete, len(questions), checked, len(machine)),
    }


def _note(complete, questions, checked, machine):
    note = (f'Counts cover {questions} recorded question parts and {checked} checked solutions only. '
            'Zero pending recorded solutions does not prove the whole chapter or book is solved. ')
    note += ('The exercise inventory is explicitly marked complete. ' if complete else
             'The complete exercise inventory is not yet verified; additional questions may be missing. ')
    if machine:
        note += f'{machine} indexed pages use machine OCR and are not marked human-verified.'
    else:
        note += 'Indexed text alone does not certify human review of every page.'
    return note


def book_coverage(book):
    """Return book and per-chapter statistics without mutating source metadata.

    Only the literal boolean ``exercise_inventory_complete=True`` certifies an
    inventory flag; AI check labels never count as checked solutions.
    """
    chapters = [_chapter_coverage(book, chapter) for chapter in book.get('chapters', [])]
    complete = book.get('exercise_inventory_complete') is True
    fields = ('indexed_pages', 'machine_ocr_pages', 'explicitly_reviewed_pages',
              'recorded_questions', 'checked_solutions', 'pending_recorded_solutions')
    counts = {field: sum(chapter[field] for chapter in chapters) for field in fields}
    return {
        'book_id': book['id'], 'total_chapters': len(chapters), **counts,
        'inventory_complete': complete,
        'coverage_note': _note(complete, counts['recorded_questions'], counts['checked_solutions'], counts['machine_ocr_pages']),
        'chapters': chapters,
    }
