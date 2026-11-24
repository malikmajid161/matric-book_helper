import fitz
from rag.page_evidence import page_images


def test_ocr_answer_uses_original_pages_with_matching_citations(tmp_path):
    path = tmp_path / 'book.pdf'
    doc = fitz.open()
    for page in range(4):
        doc.new_page().insert_text((30, 40), f'Original textbook page {page + 1}')
    doc.save(path); doc.close()
    rows = [{'page_number': page, 'citation': index + 1} for index, page in enumerate([2, 2, 4, 1, 3])]
    selected, images = page_images(path, rows)
    assert [page['page'] for page in images] == [2, 4, 1]
    assert images[0]['citations'] == [1, 2]
    assert all(page['data'].startswith(b'\x89PNG') for page in images)
    assert [row['citation'] for row in selected] == [1, 2, 3, 4]
