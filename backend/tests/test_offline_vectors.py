import json
import numpy as np
from rag.offline_vectors import build_index, terms


def test_portable_embeddings_rank_correct_page_and_unknown_query():
    chapters = [
        {'number': 14, 'title': 'Energy', 'pages': [{'page_number': 6, 'text': 'Internal energy is the total kinetic and potential energy of particles.'}]},
        {'number': 15, 'title': 'Reactions', 'pages': [{'page_number': 28, 'text': 'Electrolysis decomposes an electrolyte using an electric current.'}]},
    ]
    index = json.loads(json.dumps(build_index(chapters)))
    query = 'What is internal energy?'
    query_counts = {word: terms(query).count(word) for word in terms(query)}
    raw = np.array([(1 + np.log(query_counts[word])) * index['idf'][i] if word in query_counts else 0 for i, word in enumerate(index['vocabulary'])])
    vector = raw @ np.array(index['projection'])
    vector /= np.linalg.norm(vector)
    scores = [float(np.dot(vector, row['vector'])) for row in index['documents']]
    assert scores[0] > 0.5 and scores[0] > scores[1]
    assert index['documents'][0]['page_number'] == 6
    assert len(index['documents'][0]['vector']) == index['dimensions']
    assert not set(terms('chlorophyll photosynthesis')).intersection(index['vocabulary'])
    assert build_index([]) is None


def test_vector_chunks_preserve_end_of_long_page():
    text = ' '.join(f'word{i}' for i in range(490))
    index = build_index([{'number': 1, 'title': 'Test', 'pages': [{'page_number': 7, 'text': text}]}])
    assert len(index['documents']) == 3
    assert index['documents'][-1]['text'].endswith('word489')
    assert all(row['chapter_number'] == 1 for row in index['documents'])
