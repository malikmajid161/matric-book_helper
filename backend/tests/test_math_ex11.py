import cmath
from fractions import Fraction
from pathlib import Path

from tools.build_math_ex11 import exercises
from rag.exercises import exercise_reference, resolve_exercise


def test_all_eight_power_answers_by_direct_complex_arithmetic():
    actual = [1j**5, 1j**16, (-1j)**-19, 27 * 1j**-26,
              1j**11 + 1j**5, (1j**4 + 1j**3 + 1j**2 + 1j)**2,
              (1j**8 / 1j**5)**-5, 1j**13 * 1j**29]
    rows = [row for row in exercises() if row['question_number'] == 1]
    assert len(rows) == 8
    for row, value in zip(rows, actual):
        expected = complex(*row['verification']['result'])
        assert abs(value - expected) < 1e-12
        assert row['solution_status'] == 'checked'


def test_four_radical_answers_keep_original_sign_and_denominator():
    actual = [2 + cmath.sqrt(-4), 3 - cmath.sqrt(-7),
              Fraction(2, 5) + cmath.sqrt(-16) / 5, 2**0.5 - cmath.sqrt(-3)]
    rows = [row for row in exercises() if row['question_number'] == 2]
    assert len(rows) == 4
    for row, value in zip(rows, actual):
        check = row['verification']
        real = check.get('real')
        real = float(Fraction(*real)) if real else check['real_sqrt']**0.5
        imaginary = check['imaginary_sign'] * check['radicand']**0.5 / check['denominator']
        assert abs(value - complex(real, imaginary)) < 1e-12


def test_five_xy_answers_substitute_into_the_original_complex_equations():
    originals = [
        lambda x, y: ((2*x + 5) + (y - 3)*1j, 1 + 2j),
        lambda x, y: ((3*x + 2) - (4 - y)*1j, 5 + 3j),
        lambda x, y: ((2 + 1j)*x + (1 - 2j)*y, 3 + 4j),
        lambda x, y: ((1 - 1j)*x + (2 + 1j)*y, 4 - 1j),
        lambda x, y: ((3*x - 1) + (2*y - 3)*1j, 8 + 7j),
    ]
    rows = [row for row in exercises() if row['question_number'] == 3]
    assert len(rows) == 5
    for row, equation in zip(rows, originals):
        x, y = row['verification']['result']
        lhs, rhs = equation(x, y)
        assert lhs == rhs
    # The scan says +2i. A minus-sign OCR error would produce y=1 instead.
    assert rows[0]['verification']['result'] == [-2, 5]
    assert rows[0]['text'].endswith('1 + 2i.')


def test_reviewed_exercise_shorthand_lists_all_seventeen_and_solves_offline():
    book = {'id': 'mathematics', 'chapters': [
        {'number': 1, 'title': 'Complex Numbers', 'start_page': 3, 'end_page': 23, 'exercises': exercises()}]}
    assert exercise_reference('ex 1.1 soltion') == ('1.1', None)
    assert exercise_reference('excercise 1.1 question 3') == ('1.1', 3)
    result = resolve_exercise('give me all q of ex 1.1', book)
    assert result['supported'] is True
    assert result['answer'].count('## Question ') == 17
    assert '**Final answer:**' not in result['answer']
    worked = resolve_exercise('ex 1.1 soltion', book)
    assert worked['answer'].count('**Final answer:**') == 17
    assert worked['sources'][0]['page_number'] == 6
    one = resolve_exercise('solve ex 1.1 q3', book)
    assert one['answer'].count('## Question ') == 5
    assert resolve_exercise('ex 1.2 solution', book)['supported'] is False


def test_reviewed_math_manifest_and_ocr_are_bound_to_the_actual_book():
    from rag.ingest import read_manifest, validate_book, extract_book
    from rag.lexical import WordTokenizer
    data = Path(__file__).resolve().parents[1] / 'data'
    if not (data / 'books' / 'mathematics.pdf').exists():
        import pytest
        pytest.skip('Real textbook review artifacts are intentionally excluded from Git.')
    book = next(row for row in read_manifest(data) if row['id'] == 'mathematics')
    validate_book(book, data / 'books' / 'mathematics.pdf')
    records, chapters = extract_book(book, data / 'books' / 'mathematics.pdf', WordTokenizer())
    assert len(chapters) == 12
    assert {row['page_number'] for row in records} == {4, 6}
    assert len(chapters[0]['exercises']) == 17
    assert not chapters[1]['pages']
    assert chapters[1]['coverage'] == 'pdf-only'
