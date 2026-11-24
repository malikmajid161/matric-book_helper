"""Six independently explained answers checked against the 2026–27 source PDF.

Returns data for the caller to merge into the private study sidecar. No API calls,
manifest writes, or claim of an official board marking key. Page numbers are PDF
pages, not printed page numbers (the difference is three for this chapter).
"""
import hashlib
import json
from pathlib import Path

PDF_SHA256 = '64fcd73190ad12858ff756a2fcfde6cdf8f108cc0b318d55999554cf4f53aed6'


def answer(short, steps, final, pages, note):
    return {
        'solution_status': 'checked',
        'solution': '## Short answer\n' + short + '\n\n## Understand it simply\n'
            + '\n'.join(f'{index}. {step}' for index, step in enumerate(steps, 1))
            + '\n\n## Final answer\n' + final,
        'solution_source_pages': pages,
        'verification_note': 'Question visually checked on PDF page 17. ' + note
            + ' Independently derived study explanation; not a teacher-reviewed or official board answer key.',
    }


def solutions():
    return {
        '14.B.14.1': answer(
            'The energy comes from inside the liquid itself.',
            ['Evaporation happens when molecules escape from the surface of a liquid.',
             'The textbook says that the smaller amount of energy required for evaporation is provided from inside the liquid.',
             'As this energy is used, evaporation produces cooling. This is the energy-source explanation given in the textbook comparison with boiling.'],
            'A liquid supplies the energy for evaporation from within itself, so evaporation cools the liquid.',
            [6, 9], 'PDF page 6 defines surface escape; the table on PDF page 9 explicitly identifies the energy source and cooling.'),
        '14.B.14.2': answer(
            'No. Condensation releases heat; it is exothermic, not endothermic.',
            ['Condensation changes a gas into its liquid form when the gas is cooled.',
             'During cooling, its molecules lose energy and move closer together because of attraction.',
             'This is the reverse of boiling, which requires heat to change liquid into gas. Therefore condensation releases energy instead of absorbing it.'],
            'Condensation is an exothermic process because energy is removed as vapour changes into liquid.',
            [7, 8], 'PDF page 7 describes cooling and decreased molecular kinetic energy; PDF page 8 describes the reverse cooling path. The exothermic label is a qualitative derivation from that direction of energy transfer.'),
        '14.B.14.3': answer(
            'Naphthalene balls disappear because they sublime: solid naphthalene changes directly into vapour.',
            ['Sublimation is a direct change from solid to vapour without first becoming liquid.',
             'Naphthalene balls are given as an example in the textbook.',
             'Their molecules gain enough energy to overcome neighbouring attractions and escape into the vapour phase. The solid balls therefore become smaller and disappear.'],
            'They disappear by sublimation, not by first melting into a liquid.',
            [10], 'PDF page 10 explicitly names disappearing naphthalene balls as sublimation and explains escape into the vapour phase.'),
        '14.B.14.4': answer(
            'During a phase change, energy changes the physical state instead of raising the temperature.',
            ['When a solid has started melting, further supplied heat is used to convert it into liquid.',
             'At the boiling point, supplied heat overcomes the forces of attraction between particles and converts the liquid into gas.',
             'The temperature stays constant until that phase change is complete. The flat parts of the heating and cooling curves show this.'],
            'At fixed pressure, the temperature remains constant during the phase change because energy is used for changing the state.',
            [6, 7, 8, 9], 'PDF pages 6–7 explain constant temperature during melting and boiling; PDF pages 8–9 describe the constant-temperature portions of the heating/cooling curves.'),
        '14.B.14.5': answer(
            'A liquid cannot be compressed as easily as a gas.',
            ['Gas particles are widely apart at low pressure, leaving room for them to be pushed closer together.',
             'Liquid particles are already quite close to one another. Their inter-particle forces give the liquid a fixed volume.',
             'There is therefore much less room to reduce the volume of a liquid than the volume of a gas.'],
            'Liquids are much less compressible than gases because their particles are already close together.',
            [5, 12], 'PDF page 5 contrasts widely separated gas particles and close liquid particles; PDF page 12 describes gas compression as a decrease in molecular separation. Avoids the inaccurate absolute claim that liquids cannot compress at all.'),
        '14.B.14.6': answer(
            'Yes. Changing the external pressure changes the temperature at which water boils.',
            ['A liquid boils when its vapour pressure equals the external pressure.',
             'Reducing the external pressure lowers the boiling point.',
             'Increasing the external pressure raises the boiling point, as shown by the pressure comparison in the textbook.'],
            'In a suitable laboratory experiment, vary the external pressure to change water’s boiling temperature.',
            [7, 10], 'PDF page 7 defines boiling by equal vapour and external pressures. PDF page 10 explicitly states lower atmospheric pressure lowers the boiling point and its diagram shows higher pressure gives a higher boiling point. No unprovided apparatus or hazardous procedure is invented.'),
    }


def checked_solutions(pdf_path=None):
    """Check source identity before the root ingestion tool merges these answers."""
    path = Path(pdf_path) if pdf_path else Path(__file__).resolve().parents[1] / 'data' / 'books' / 'chemistry.pdf'
    if hashlib.sha256(path.read_bytes()).hexdigest() != PDF_SHA256:
        raise ValueError('Chemistry solutions were reviewed against a different textbook PDF.')
    return solutions()


if __name__ == '__main__':
    print(json.dumps(checked_solutions(), ensure_ascii=False, indent=2))
