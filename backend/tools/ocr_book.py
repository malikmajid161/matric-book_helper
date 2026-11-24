"""Create a resumable OCR draft; review it before binding its SHA-256 in the manifest.

Install requirements-ocr.txt, then: python tools/ocr_book.py data/books/physics.pdf
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pymupdf
from rapidocr_onnxruntime import RapidOCR


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--start', type=int, default=1)
    parser.add_argument('--end', type=int)
    args = parser.parse_args()
    output = args.pdf.with_suffix('.pages.draft.json')
    pages = json.loads(output.read_text(encoding='utf-8')) if output.exists() else {}
    engine = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=1)
    with pymupdf.open(args.pdf) as pdf:
        for index in range(args.start - 1, min(args.end or len(pdf), len(pdf))):
            if str(index + 1) in pages:
                continue
            pixmap = pdf[index].get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
            array = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, 3)
            result, _ = engine(array)
            lines = [row[1] for row in result or []]
            pages[str(index + 1)] = '\n'.join(lines)
            temporary = output.with_suffix('.tmp')
            temporary.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding='utf-8')
            temporary.replace(output)
            print(f'OCR draft page {index + 1}/{len(pdf)}', flush=True)
    print('Review equations, tables, order and chapter headings. Drafts are not indexed automatically.')


if __name__ == '__main__':
    main()
