"""Build reviewed study material for the original 2026–27 Maths PDF.

Only PDF pages 4 and 6 have been visually checked. The rest of the book remains
available as a PDF, not silently accepted from the unreviewed OCR draft.
Worked solutions are independently derived study help, not a board answer key.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ROOT / 'data' / 'books'
PDF_SHA256 = '8ca72023ba062f4a5abcc7d465d8f21f86cae2551790a167e003a9670a3d7e2f'


def exercise(question, part, text, steps, answer, check, **verification):
    return {
        'id': f'1.1.{question}.{part}', 'exercise': '1.1',
        'question_number': question, 'part': part, 'text': text,
        'page_number': 6, 'printed_page': 4, 'solution_status': 'checked',
        'solution_origin': 'independently derived; source question visually checked',
        'solution': '\n'.join(f'{index}. {step}' for index, step in enumerate(steps, 1))
            + '\n\n**Final answer:** ' + answer + '\n\n**Check:** ' + check,
        'expected_answer': answer, **verification,
    }


def exercises():
    return [
        exercise(1, 'i', 'Simplify i^5.', [
            'Use i² = −1. Therefore i⁴ = (i²)² = (−1)² = 1.',
            'Split the power: i⁵ = i⁴ × i.', 'Substitute i⁴ = 1: i⁵ = 1 × i = i.',
        ], 'i', 'The powers repeat every four. The remainder of 5 ÷ 4 is 1.', verification={'kind': 'power', 'base': 'i', 'power': 5, 'result': [0, 1]}),
        exercise(1, 'ii', 'Simplify i^16.', [
            'Use i² = −1, so i⁴ = 1.', 'Write 16 = 4 × 4.', 'Then i¹⁶ = (i⁴)⁴ = 1⁴ = 1.',
        ], '1', '16 is a multiple of four, so its position in the power cycle is 1.', verification={'kind': 'power', 'base': 'i', 'power': 16, 'result': [1, 0]}),
        exercise(1, 'iii', 'Simplify (−i)^(−19).', [
            'The base is −i, not i. Since (−i)² = −1, we have (−i)⁴ = 1.',
            'Write −19 = 4(−5) + 1.', 'Then (−i)^(−19) = ((−i)⁴)^(−5) × (−i) = 1 × (−i).',
        ], '−i', 'Multiplying the result by (−i)¹⁹ gives 1, as required for a negative power.', verification={'kind': 'power', 'base': '-i', 'power': -19, 'result': [0, -1]}),
        exercise(1, 'iv', 'Simplify 27i^(−26).', [
            'Keep the coefficient 27 outside the power.', 'Write −26 = 4(−7) + 2.',
            'Then i^(−26) = (i⁴)^(−7) × i² = 1 × (−1) = −1.', 'Multiply: 27 × (−1) = −27.',
        ], '−27', 'i²⁶ = −1, whose reciprocal is also −1.', verification={'kind': 'scaled_power', 'base': 'i', 'power': -26, 'scale': 27, 'result': [-27, 0]}),
        exercise(1, 'v', 'Simplify i^11 + i^5.', [
            'Write i¹¹ = i⁸ × i³ = (i⁴)² × (i² × i) = 1 × (−i) = −i.',
            'Also i⁵ = i⁴ × i = i.', 'Add the terms: −i + i = 0.',
        ], '0', 'The two imaginary terms have equal size and opposite signs.', verification={'kind': 'sum_powers', 'powers': [11, 5], 'result': [0, 0]}),
        exercise(1, 'vi', 'Simplify (i^4 + i^3 + i^2 + i)^2.', [
            'Evaluate the powers inside the bracket: i⁴ = 1, i³ = −i, and i² = −1.',
            'The bracket becomes 1 − i − 1 + i = 0.', 'Square the whole bracket: 0² = 0.',
        ], '0', 'The real terms cancel and the imaginary terms cancel before squaring.', verification={'kind': 'sum_square', 'powers': [4, 3, 2, 1], 'result': [0, 0]}),
        exercise(1, 'vii', 'Simplify (i^8 / i^5)^(−5).', [
            'Use the quotient rule: i⁸ / i⁵ = i^(8−5) = i³. Division is valid because i is nonzero.',
            'Use the power rule: (i³)^(−5) = i^(−15).',
            'Write −15 = 4(−4) + 1. Then i^(−15) = (i⁴)^(−4) × i = i.',
        ], 'i', 'i³ = −i. Its reciprocal is i, so (−i)^(−5) = i⁵ = i.', verification={'kind': 'quotient_power', 'numerator': 8, 'denominator': 5, 'power': -5, 'result': [0, 1]}),
        exercise(1, 'viii', 'Simplify i^13 × i^29.', [
            'For powers with the same base, add the exponents: i¹³ × i²⁹ = i⁴².',
            'Write 42 = 4 × 10 + 2.', 'Then i⁴² = (i⁴)¹⁰ × i² = 1 × (−1) = −1.',
        ], '−1', 'i¹³ = i and i²⁹ = i; their product is i² = −1.', verification={'kind': 'product_powers', 'powers': [13, 29], 'result': [-1, 0]}),
        exercise(2, 'i', 'Write 2 + √(−4) in terms of i.', [
            'Use i = √(−1). For a positive real number a, √(−a) = i√a.',
            'Therefore √(−4) = i√4 = 2i.', 'Substitute: 2 + √(−4) = 2 + 2i.',
        ], '2 + 2i', '(2i)² = 4i² = −4, so the imaginary square-root term is correct.', verification={'kind': 'radical', 'real': [2, 1], 'radicand': 4, 'imaginary_sign': 1, 'denominator': 1}),
        exercise(2, 'ii', 'Write 3 − √(−7) in terms of i.', [
            'Use √(−7) = i√7.', 'Keep the minus sign already present in the question.',
            'Substitute: 3 − √(−7) = 3 − i√7.',
        ], '3 − i√7', '(i√7)² = i² × 7 = −7; the subtraction sign remains outside the root.', verification={'kind': 'radical', 'real': [3, 1], 'radicand': 7, 'imaginary_sign': -1, 'denominator': 1}),
        exercise(2, 'iii', 'Write 2/5 + √(−16)/5 in terms of i.', [
            'Only −16 is under the square root; the denominator is 5.',
            'Use √(−16) = i√16 = 4i.', 'Substitute: 2/5 + √(−16)/5 = 2/5 + 4i/5 = (2 + 4i)/5.',
        ], '(2 + 4i)/5', '(4i)² = −16, and both original denominators are still 5.', verification={'kind': 'radical', 'real': [2, 5], 'radicand': 16, 'imaginary_sign': 1, 'denominator': 5}),
        exercise(2, 'iv', 'Write √2 − √(−3) in terms of i.', [
            'The first root √2 is real and stays unchanged.', 'Replace √(−3) by i√3.',
            'Keep the subtraction sign: √2 − √(−3) = √2 − i√3.',
        ], '√2 − i√3', '(i√3)² = −3. The real part remains √2.', verification={'kind': 'radical', 'real_sqrt': 2, 'radicand': 3, 'imaginary_sign': -1, 'denominator': 1}),
        exercise(3, 'i', 'Find x and y: (2x + 5) + (y − 3)i = 1 + 2i.', [
            'Equal complex numbers have equal real parts and equal imaginary parts.',
            'Compare real parts: 2x + 5 = 1. Subtract 5: 2x = −4. Divide by 2: x = −2.',
            'Compare imaginary parts: y − 3 = 2. Add 3: y = 5.',
        ], 'x = −2, y = 5', 'Substitute: (2(−2) + 5) + (5 − 3)i = 1 + 2i.', verification={'kind': 'linear', 'matrix': [[2, 0], [0, 1]], 'rhs': [-4, 5], 'result': [-2, 5]}),
        exercise(3, 'ii', 'Find x and y: (3x + 2) − (4 − y)i = 5 + 3i.', [
            'Rewrite the imaginary term carefully: −(4 − y)i = (y − 4)i.',
            'Compare real parts: 3x + 2 = 5, so 3x = 3 and x = 1.',
            'Compare imaginary parts: y − 4 = 3, so y = 7.',
        ], 'x = 1, y = 7', '(3(1) + 2) − (4 − 7)i = 5 − (−3)i = 5 + 3i.', verification={'kind': 'linear', 'matrix': [[3, 0], [0, 1]], 'rhs': [3, 7], 'result': [1, 7]}),
        exercise(3, 'iii', 'Find x and y: (2 + i)x + (1 − 2i)y = 3 + 4i.', [
            'Expand and group: (2x + y) + (x − 2y)i = 3 + 4i.',
            'Compare parts: 2x + y = 3 and x − 2y = 4.',
            'From 2x + y = 3, get y = 3 − 2x.',
            'Substitute into x − 2y = 4: x − 2(3 − 2x) = 4.',
            'Expand: x − 6 + 4x = 4, so 5x = 10 and x = 2.',
            'Then y = 3 − 2(2) = −1.',
        ], 'x = 2, y = −1', '(2 + i)(2) + (1 − 2i)(−1) = 4 + 2i − 1 + 2i = 3 + 4i.', verification={'kind': 'linear', 'matrix': [[2, 1], [1, -2]], 'rhs': [3, 4], 'result': [2, -1]}),
        exercise(3, 'iv', 'Find x and y: (1 − i)x + (2 + i)y = 4 − i.', [
            'Expand and group: (x + 2y) + (−x + y)i = 4 − i.',
            'Compare parts: x + 2y = 4 and −x + y = −1.',
            'Add the two equations: 3y = 3, so y = 1.',
            'Substitute into x + 2y = 4: x + 2 = 4, so x = 2.',
        ], 'x = 2, y = 1', '(1 − i)(2) + (2 + i)(1) = 2 − 2i + 2 + i = 4 − i.', verification={'kind': 'linear', 'matrix': [[1, 2], [-1, 1]], 'rhs': [4, -1], 'result': [2, 1]}),
        exercise(3, 'v', 'Find x and y: (3x − 1) + (2y − 3)i = 8 + 7i.', [
            'Compare real parts: 3x − 1 = 8. Add 1: 3x = 9. Divide by 3: x = 3.',
            'Compare imaginary parts: 2y − 3 = 7. Add 3: 2y = 10. Divide by 2: y = 5.',
        ], 'x = 3, y = 5', '(3(3) − 1) + (2(5) − 3)i = 8 + 7i.', verification={'kind': 'linear', 'matrix': [[3, 0], [0, 2]], 'rhs': [9, 10], 'result': [3, 5]}),
    ]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def build(books=BOOKS):
    pdf = books / 'mathematics.pdf'
    if sha(pdf) != PDF_SHA256:
        raise ValueError('Review is bound to a different Maths PDF; do not reuse these page references.')
    rows = exercises()
    pages = {
        '4': '1.1 Complex Numbers\n'
             'Equation 1: x² − 1 = 0. x² = 1. x = ±1.\n'
             'Equation 2: x² + 1 = 0. x² = −1.\n'
             'Equation 1 has two real solutions, x = −1, 1.\n'
             'Equation 2 has no real solution, since the graph of f(x) = x² + 1 does not cross the x-axis.\n'
             'This is because squaring any real number never results in a negative value. Therefore, '
             'if equation 2 has a solution, we need to introduce a new kind of number, an imaginary '
             'number, defined as the square root of −1. This imaginary unit is represented by the '
             'symbol i (iota). The imaginary number i tells us that i² = −1.\n'
             'Example 1: Simplify i^7, i^8, i^17, i^(−25).\n'
             'i^7 = i^6 × i = (i²)^3 × i = (−1)^3 × i = −i.\n'
             'i^8 = (i²)^4 = (−1)^4 = 1.',
        '6': 'Example 2: If (2x − 1) + (y + 4)i = 5 + 7i, then find the values of x and y.\n'
             'Since the two complex numbers are equal, their real and imaginary parts must be equal.\n'
             '2x − 1 = 5; 2x = 6; x = 3. y + 4 = 7; y = 7 − 4; y = 3.\n'
             'EXERCISE 1.1\n' + '\n'.join(f"Q{row['question_number']} ({row['part']}): {row['text']}" for row in rows),
    }
    write_json(books / 'mathematics.pages.json', pages)
    study = {
        'pdf_sha256': PDF_SHA256, 'reviewed_pdf_pages': [4, 6],
        'coverage': 'partial: Exercise 1.1 only; other exercises and pages await review',
        'solution_disclaimer': 'Independently derived study solutions. Not an official Sargodha Board marking scheme or answer key.',
        'chapters': {'1': {
            'coverage': 'partial-reviewed',
            'topics': [{'id': '1.1', 'title': 'Complex Numbers and Exercise 1.1', 'page_number': 4,
                        'key_points': ['The imaginary unit satisfies i² = −1.', 'Match real and imaginary parts when equating complex numbers.']}],
            'exercises': rows,
        }},
    }
    write_json(books / 'mathematics.study.json', study)
    manifest_path = books / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    maths = next(book for book in manifest if book['id'] == 'mathematics')
    titles = ['Complex Numbers', 'Quadratic Equations and Inequalities', 'Matrices and Determinants',
              'Functions and Graphs', 'Algebraic Fractions', 'Vectors in Plane', 'Trigonometry',
              'Chords and Arcs of a Circle', 'Tangent and Angles of a Circle',
              'Practical Geometry of Circles', 'Information Handling', 'Probability']
    starts = [1, 22, 47, 81, 97, 111, 125, 143, 155, 168, 176, 196, 212]
    maths.update(reader_only=False, reviewed_pages_only=True, coverage='partial-reviewed',
                 coverage_note='Exercise 1.1 (17 subparts) and PDF pages 4 and 6 checked; remaining solutions and text await review.',
                 reviewed_pdf_pages=[4, 6], ocr_sha256=sha(books / 'mathematics.pages.json'),
                 study_sha256=sha(books / 'mathematics.study.json'),
                 chapters=[{'number': i + 1, 'title': title, 'start_page': starts[i] + 2,
                            'end_page': starts[i + 1] + 1,
                            'coverage': 'partial-reviewed' if i == 0 else 'pdf-only'} for i, title in enumerate(titles)])
    write_json(manifest_path, manifest)
    return rows


if __name__ == '__main__':
    print(f'Built {len(build())} checked Exercise 1.1 subparts; remaining Maths coverage is explicitly partial.')
