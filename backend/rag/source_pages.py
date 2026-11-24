def attach_source_pages(result, book):
    """Attach the full stored page separately from retrieved chunks and generated prose."""
    pages = {page['page_number']: page['text'] for chapter in book['chapters'] for page in chapter.get('pages', [])}
    for row in result.get('sources', []):
        page = row['page_number']
        row['page_text'] = pages.get(page, row['text'])
        row['text_origin'] = book.get('text_origin', 'native')
        row['verification'] = 'OCR draft; compare original page' if row['text_origin'] == 'machine_transcribed' else 'Extracted or reviewed text; original page available'
        row['book_title'] = book['title']
    return result
