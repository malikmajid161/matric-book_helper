import re


def normalize(text):
    text = re.sub(r'^(?:q(?:uestion)?\s*)?\d+(?:\.\d+)+(?:[.)])?\s+', '', text.lower().strip())
    text = re.sub(r'^(?:q(?:uestion)?\s*)?\d+[.)]\s+', '', text)
    text = re.sub(r'[?"“”]', ' ', text)
    text = re.sub(r'\.(?!\d)', ' ', text)
    text = re.sub(r'\s*([+−\-×÷=<>/^()\[\]{}])\s*', r'\1', text)
    return ' '.join(text.split())


def saved_solution(query, book, chapter=None):
    matches = [(owner, item) for owner in book['chapters'] if chapter is None or owner['number'] == chapter
               for item in owner.get('exercises', []) if item.get('solution_status') == 'checked'
               and item.get('solution', '').strip() and normalize(item['text']) == normalize(query)]
    if not matches or len({row['solution'] for _, row in matches}) != 1:
        return None
    owner, item = matches[0]
    pages = {page['page_number']: page['text'] for page in owner.get('pages', [])}
    evidence = list(dict.fromkeys(item.get('solution_source_pages') or [item['page_number']]))
    if any(number not in pages for number in evidence):
        return None
    numbers = list(dict.fromkeys([item['page_number']] + evidence))
    sources = [{'id': f"{book['id']}:{number}:solution", 'book': book['id'], 'chapter_number': owner['number'],
                'chapter_title': owner['title'], 'page_number': number, 'text': pages.get(number, item['text']),
                'citation': index + 1, 'distance': 0} for index, number in enumerate(numbers)]
    citations = ' '.join(f'[{row["citation"]}]' for row in sources if row['page_number'] in evidence)
    return {'answer': f"## Question\n{item['text']} [1]\n\n{item['solution']}\n\n## Textbook basis\nThis independently checked study solution uses the saved textbook pages. {citations}",
            'supported': True, 'sources': sources}
