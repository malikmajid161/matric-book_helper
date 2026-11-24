from rag.source_pages import attach_source_pages


def test_exact_page_stays_separate_from_ai_answer_and_ocr_not_called_verified():
    original = 'A page\nwith original spacing and a formula x².'
    book = {'title': 'Physics', 'text_origin': 'machine_transcribed', 'chapters': [{'pages': [{'page_number': 9, 'text': original}]}]}
    result = {'answer': 'Generated explanation [1]', 'sources': [{'page_number': 9, 'text': 'with original spacing'}]}
    attached = attach_source_pages(result, book)
    assert attached['answer'] == result['answer']
    assert attached['sources'][0]['page_text'] == original
    assert attached['sources'][0]['verification'].startswith('OCR draft')
