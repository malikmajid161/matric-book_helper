from copy import deepcopy
from types import SimpleNamespace

import pytest

from tools.generate_math_solutions import retry_delay, validate_generation, validate_task, validate_verification


TASK = {'exercise': '1.1', 'start_page': 6, 'end_page': 6, 'expected_question_ids': ['1.i']}
DRAFT = {'exercise': '1.1',
    'coverage': {'visible_question_ids': ['1.i'], 'all_visible_questions_included': True, 'continued_before': False, 'continued_after': False},
    'questions': [{'id': '1.i', 'question_number': '1', 'part': 'i', 'question_text': 'Simplify i⁵.',
        'source_pages': [6], 'given': ['i² = −1'], 'steps': ['i⁵ = i⁴ × i = 1 × i.'],
        'final_answer': 'i', 'check': 'Powers repeat every four.', 'diagram_required': False, 'ambiguous_symbols': False}]}
CHECK = {'exercise': '1.1', 'question_ids': ['1.i'], 'all_visible_questions_included': True,
    'transcription_correct': True, 'arithmetic_correct': True, 'reasoning_correct': True, 'issues': []}


def test_solution_draft_rejects_invented_page_and_ambiguous_answer():
    draft = deepcopy(DRAFT)
    draft['questions'][0]['source_pages'] = [7]
    with pytest.raises(ValueError, match='outside'):
        validate_generation(draft, TASK)
    draft = deepcopy(DRAFT)
    draft['questions'][0]['ambiguous_symbols'] = True
    with pytest.raises(ValueError, match='guessed'):
        validate_generation(draft, TASK)


def test_missing_question_and_second_check_disagreement_cannot_pass():
    task = {**TASK, 'expected_question_ids': ['1.i', '1.ii']}
    draft = validate_generation(deepcopy(DRAFT), task)
    assert draft['coverage']['all_visible_questions_included'] is False
    assert not validate_verification(deepcopy(CHECK), task, draft)['passed']
    check = deepcopy(CHECK)
    check['question_ids'] = ['1.ii']
    assert not validate_verification(check, TASK, deepcopy(DRAFT))['passed']


def test_ai_pass_always_requires_human_review_and_task_bounds():
    assert validate_task(TASK, 248) == TASK
    with pytest.raises(ValueError, match='limit'):
        validate_task({**TASK, 'end_page': 10}, 248)
    checked = validate_verification(deepcopy(CHECK), TASK, validate_generation(deepcopy(DRAFT), TASK))
    assert checked['passed'] and checked['human_review_required']


def test_retry_after_is_respected_but_bounded():
    error = SimpleNamespace(response=SimpleNamespace(headers={'Retry-After': '35'}))
    assert retry_delay(error, 0) == 35
    error.response.headers['Retry-After'] = '999'
    assert retry_delay(error, 0) == 60
