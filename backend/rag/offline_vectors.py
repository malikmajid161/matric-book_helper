"""Portable local LSA embeddings. Query projection runs on the phone without an API.

This is a compact latent semantic index, not a generative language model.
Vectors and their projection are versioned with the textbook bundle.
"""
import math
import re
from collections import Counter

import numpy as np

MODEL_VERSION = 'lsa-tfidf-1'
STOP = set('a an the is are was were what why how explain give me of in on to for and or with from does do can please this that which have has it as be by its'.split())


def terms(text):
    return [word for word in re.findall(r'[a-z0-9]+', text.lower()) if len(word) > 1 and word not in STOP]


def build_index(chapters):
    documents = []
    for chapter in chapters:
        for page in chapter.get('pages', []):
            words = page['text'].split()
            for start in range(0, len(words), 190):
                text = ' '.join(words[start:start + 220])
                if not terms(text):
                    continue
                documents.append({'id': f"{chapter['number']}:{page['page_number']}:{start}",
                    'chapter_number': chapter['number'], 'chapter_title': chapter['title'],
                    'page_number': page['page_number'], 'text': text})
                if start + 220 >= len(words):
                    break
    if not documents:
        return None
    counts = [Counter(terms(row['text'])) for row in documents]
    frequency = Counter(word for row in counts for word in row)
    vocabulary = sorted(frequency, key=lambda word: (-frequency[word], word))[:6000]
    lookup = {word: index for index, word in enumerate(vocabulary)}
    idf = np.array([math.log((1 + len(documents)) / (1 + frequency[word])) + 1 for word in vocabulary], dtype=np.float32)
    matrix = np.zeros((len(documents), len(vocabulary)), dtype=np.float32)
    for index, row in enumerate(counts):
        for word, count in row.items():
            if word in lookup:
                matrix[index, lookup[word]] = (1 + math.log(count)) * idf[lookup[word]]
    matrix /= np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-12)
    dimensions = min(64, len(documents), len(vocabulary))
    # Randomized truncated SVD avoids a full vocabulary-sized square decomposition.
    rng = np.random.default_rng(42)
    random = rng.standard_normal((len(vocabulary), min(dimensions + 8, len(vocabulary))), dtype=np.float32)
    q, _ = np.linalg.qr(matrix @ random, mode='reduced')
    for _ in range(2):
        q, _ = np.linalg.qr(matrix @ (matrix.T @ q), mode='reduced')
    _, _, vt = np.linalg.svd(q.T @ matrix, full_matrices=False)
    projection = vt[:dimensions].T
    vectors = matrix @ projection
    vectors /= np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-12)
    for row, vector in zip(documents, vectors):
        row['vector'] = np.round(vector, 6).tolist()
    return {'model': MODEL_VERSION, 'dimensions': dimensions, 'vocabulary': vocabulary,
            'idf': np.round(idf, 6).tolist(), 'projection': np.round(projection, 6).tolist(),
            'documents': documents}
