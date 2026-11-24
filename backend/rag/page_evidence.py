"""Read original scanned pages for online answers; OCR is retrieval only."""
import fitz


def page_images(path, sources, limit=3):
    pages = list(dict.fromkeys(row['page_number'] for row in sources))[:limit]
    selected = [row for row in sources if row['page_number'] in pages]
    images = []
    with fitz.open(path) as pdf:
        for page in pages:
            if not 1 <= page <= len(pdf):
                raise ValueError('Invalid evidence page')
            citations = [row['citation'] for row in selected if row['page_number'] == page]
            images.append({'page': page, 'citations': citations,
                           'data': pdf[page - 1].get_pixmap(matrix=fitz.Matrix(1.7, 1.7)).tobytes('png')})
    return selected, images
