"""Resolve informal exercise references against reviewed entries, never guessed text."""
import re

EXERCISE = re.compile(r'\b(?:exercise|excersise|excercise|excercize|exersise|exersize|exercice|exer|ex)\.?\s*(\d+)\s*[.\-]\s*(\d+)\b', re.I)
QUESTION = re.compile(r'\b(?:questions?|ques|qn|q)\.?\s*#?\s*(\d+)\b', re.I)


def exercise_reference(query):
    match = EXERCISE.search(query)
    if not match:
        return None
    exercise = f'{int(match[1])}.{int(match[2])}'
    question = QUESTION.search(query)
    return exercise, int(question[1]) if question else None


def resolve_exercise(query, book, chapter=None):
    reference = exercise_reference(query)
    if not reference:
        return None
    exercise, question = reference
    if len({(int(match[1]), int(match[2])) for match in EXERCISE.finditer(query)}) > 1:
        return {'answer': '## Choose one exercise\nPlease ask for one exercise at a time, for example: ex 1.1 q 2.', 'supported': False, 'sources': []}
    chapters = [row for row in book['chapters'] if chapter is None or row['number'] == chapter]
    owned = [(row, item) for row in chapters for item in row.get('exercises', [])
             if item.get('exercise') == exercise and (question is None or item.get('question_number') == question)
             and row['start_page'] <= item.get('page_number', -1) <= row.get('end_page', item.get('page_number', -1))]
    rows = [item for _, item in owned]
    if not rows:
        message = f'## Exercise {exercise}\nI understood the exercise reference, but its exact questions have not been reviewed in this saved book yet.\n\n## Next step\nOpen the original PDF or paste one complete question, including powers and signs. I will not invent the missing questions.'
        return {'answer': message, 'supported': False, 'sources': []}
    questions_only = bool(re.search(r'\b(?:all\s+q|questions|list|show.*q|give.*q|sawal|sawalat)', query.lower())) and not re.search(r'sol|solve|answer|\bhal\b|\bjawab\b', query.lower())
    introduction = 'Questions checked against the original textbook page.' if questions_only else 'Saved worked solutions are independently derived study help, not an official board answer key.'
    parts = [f'## Exercise {exercise}', introduction]
    sources, page_ids = [], {}
    complete = True
    for owner, item in owned:
        page = item['page_number']
        source_key = (owner['number'], page)
        if source_key not in page_ids:
            page_ids[source_key] = len(sources) + 1
            sources.append({'id': f"{book['id']}:{page}:exercise", 'citation': page_ids[source_key], 'book': book['id'],
                'chapter_number': owner['number'], 'chapter_title': owner['title'], 'page_number': page,
                'text': '\n'.join(row['text'] for row in rows if row['page_number'] == page), 'distance': 0})
        citation = page_ids[source_key]
        parts.extend([f"## Question {item['question_number']}" + (f" ({item['part']})" if item.get('part') else ''), item['text'] + f' [{citation}]'])
        if not questions_only:
            solution = item.get('solution')
            if item.get('solution_status') == 'checked' and solution:
                parts.append(solution + f' [{citation}]')
            else:
                complete = False
                parts.append('This solution is still awaiting checking. Ask one complete question for online help.')
    return {'answer': '\n\n'.join(parts), 'supported': questions_only or complete, 'sources': sources}
