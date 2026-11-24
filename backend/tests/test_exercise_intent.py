import pytest
from rag.exercises import exercise_reference, resolve_exercise


def book(status='checked'):
    return {'id': 'mathematics', 'chapters': [{'number': 1, 'title': 'Complex Numbers', 'start_page': 3, 'end_page': 23,
        'exercises': [{'id': '1.1:1:i', 'exercise': '1.1', 'question_number': 1, 'part': 'i', 'text': 'Simplify i⁵.', 'page_number': 6,
                       'solution_status': status, 'solution': '1. Use i⁴ = 1.\n2. Therefore i⁵ = i.'},
                      {'id': '1.1:2:i', 'exercise': '1.1', 'question_number': 2, 'part': 'i', 'text': 'Write 2 + √(-4) in terms of i.',
                       'page_number': 6, 'solution_status': 'checked', 'solution': '2 + 2i.'}]}]}


@pytest.mark.parametrize('query,expected', [('ex 1.1 soltion', ('1.1', None)), ('give me all q of ex 1.1', ('1.1', None)),
    ('exercise1.1 q2', ('1.1', 2)), ('excersise 1.1', ('1.1', None)), ('ex1.1 q 3', ('1.1', 3)), ('EX. 01-01 Q#2', ('1.1', 2))])
def test_shorthand(query, expected):
    assert exercise_reference(query) == expected


def test_questions_only_and_saved_worked_solution():
    listed = resolve_exercise('give me all q of ex 1.1', book())
    assert listed['supported'] and 'Simplify i⁵.' in listed['answer'] and 'Therefore' not in listed['answer']
    solved = resolve_exercise('ex 1.1 soltion', book())
    assert solved['supported'] and 'Therefore i⁵ = i.' in solved['answer']
    assert len(solved['sources']) == 1 and solved['sources'][0]['page_number'] == 6
    assert solved['sources'][0]['citation'] == 1


def test_question_filter_unknown_reference_and_chapter_scope():
    result = resolve_exercise('exercise1.1 q2', book())
    assert '2 + 2i.' in result['answer'] and 'Simplify i⁵' not in result['answer']
    assert not resolve_exercise('ex1.1 q3', book())['supported']
    assert not resolve_exercise('ex1.1', book(), chapter=2)['supported']
    assert resolve_exercise('what is energy?', book()) is None


def test_unchecked_solution_is_not_claimed_supported_or_shown():
    result = resolve_exercise('ex1.1 q1 solution', book('draft'))
    assert not result['supported'] and 'awaiting checking' in result['answer']
    assert 'Therefore i⁵ = i.' not in result['answer']


def test_multiple_exercise_references_need_clarification():
    assert not resolve_exercise('ex1.1 or ex1.2', book())['supported']
