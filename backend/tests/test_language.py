import json
from pathlib import Path

import pytest
from rag.language import detect_language, retrieval_text
from rag.exercises import resolve_exercise


@pytest.mark.parametrize('query,expected', [
    ('heat kya hai', 'roman-urdu'), ('ex1.1 samjhao', 'roman-urdu'),
    ('mujhe ex1.1 ka hal chahiye', 'roman-urdu'), ('Explain internal energy', 'english'),
    ('What is the main cause?', 'english'), ('ex1.1 Roman Urdu mein explain in English', 'english'),
    ('ex1.1 roman urdu', 'roman-urdu'),
])
def test_language_detection(query, expected):
    assert detect_language(query) == expected


@pytest.mark.parametrize('query,expected', [('heat kya hai', 'heat'), ('garmi kya hai', 'heat'),
    ('roshni aur awaz ka farq', 'light sound farq'), ('internal energy samjhao', 'internal energy'),
    ('x 2 + y 3', 'x 2 y 3'), ('mujhe batao', 'mujhe batao')])
def test_retrieval_text(query, expected):
    assert retrieval_text(query) == expected


def test_roman_saved_solutions_keep_english_source_and_same_final_answers():
    path = Path(__file__).resolve().parents[1] / 'data/books/mathematics.study.json'
    if not path.exists():
        pytest.skip('Reviewed private study bundle not installed')
    study = json.loads(path.read_text(encoding='utf-8'))
    rows = study['chapters']['1']['exercises']
    assert len(rows) == 17
    book = {'id': 'mathematics', 'chapters': [{'number': 1, 'title': 'Complex Numbers', 'start_page': 3, 'end_page': 23, 'exercises': rows}]}
    english = resolve_exercise('ex1.1 q3 solution', book)
    roman = resolve_exercise('ex1.1 q3 ka hal samjhao', book)
    assert english['supported'] and roman['supported']
    assert '## Question 3' in roman['answer'] and '**Final answer:**' in roman['answer']
    assert roman['answer'] == english['answer']
    assert '## Question 3' in english['answer'] and '**Final answer:**' in english['answer']
    assert roman['sources'] == english['sources']
