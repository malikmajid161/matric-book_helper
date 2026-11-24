from pathlib import Path
import pytest
from tools.build_chemistry14_solutions import checked_solutions, solutions


def body(question):
    return solutions()[f'14.B.14.{question}']['solution'].lower()


def test_energy_direction_is_consistent_between_evaporation_and_condensation():
    # Evaporation must not be described as needing no energy, or as heating a liquid.
    assert 'inside the liquid' in body(1)
    assert 'cool' in body(1)
    assert 'requires no energy' not in body(1)
    # Condensation is the reverse energy direction; it must not absorb heat.
    assert 'exothermic' in body(2)
    assert 'releases' in body(2)
    assert 'absorbs heat' not in body(2)


def test_naphthalene_and_phase_change_explanations_do_not_change_the_process():
    assert 'sublim' in body(3)
    assert 'without first becoming liquid' in body(3)
    assert 'forces of attraction' in body(4)
    assert 'until that phase change is complete' in body(4)
    assert 'no heat is supplied' not in body(4)


def test_compressibility_and_pressure_answer_avoid_common_wrong_absolute_claims():
    assert 'much less compressible' in body(5)
    assert 'cannot be compressed at all' not in body(5)
    assert 'reducing the external pressure lowers' in body(6)
    assert 'increasing the external pressure raises' in body(6)
    assert 'sealed' not in body(6)  # Do not invent a student pressure-vessel procedure.


def test_checked_answers_have_specific_evidence_and_honest_review_label():
    rows = solutions()
    assert len(rows) == 6
    for row in rows.values():
        assert row['solution_status'] == 'checked'
        assert row['solution_source_pages']
        assert set(row['solution_source_pages']) <= {5, 6, 7, 8, 9, 10, 12}
        assert 'not a teacher-reviewed or official board answer key' in row['verification_note']
        assert '## Short answer' in row['solution']
        assert '## Understand it simply' in row['solution']
        assert '## Final answer' in row['solution']


def test_solution_package_rejects_changed_source_pdf(tmp_path):
    path = tmp_path / 'chemistry.pdf'
    path.write_bytes(b'a different file')
    with pytest.raises(ValueError, match='different textbook'):
        checked_solutions(path)
    source = Path(__file__).resolve().parents[1] / 'data' / 'books' / 'chemistry.pdf'
    if source.exists():
        assert len(checked_solutions(source)) == 6
