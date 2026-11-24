from rag.saved_solutions import saved_solution


def fixture():
    return {'id': 'chemistry', 'chapters': [{'number': 14, 'title': 'Matter', 'pages': [
        {'page_number': 6, 'text': 'Evaporation takes energy from the liquid.'},
        {'page_number': 17, 'text': '14.1 Where does energy come from?'}], 'exercises': [
        {'text': '14.1 Where does energy come from?', 'page_number': 17, 'solution_status': 'checked',
         'solution': 'From the liquid.', 'solution_source_pages': [6]}]}]}


def test_saved_solution_uses_actual_evidence_and_never_crosses_chapters():
    book = fixture()
    answer = saved_solution('Where does energy come from?', book)
    assert answer['supported']
    assert [row['page_number'] for row in answer['sources']] == [17, 6]
    assert answer['sources'][1]['text'] == 'Evaporation takes energy from the liquid.'
    assert saved_solution('Where does energy come from?', book, 15) is None
    assert saved_solution('Where does energy go?', book) is None
    book['chapters'][0]['pages'].pop(0)
    assert saved_solution('Where does energy come from?', book) is None


def test_changed_numbers_and_signs_are_not_equivalent():
    book = fixture(); row = book['chapters'][0]['exercises'][0]
    row['text'] = 'Calculate 2 + 3.'
    assert saved_solution('Calculate 2 - 3.', book) is None
    assert saved_solution('Calculate 2 + 4.', book) is None
