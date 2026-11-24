"""Small CPU-only ranked retrieval option; semantic embeddings remain optional."""
import math
import re
from collections import Counter
from rag.ingest import extract_book, validate_book, read_manifest, PIPELINE_VERSION
import hashlib
import json

STOP = set('a an the is are was were what why how explain give me of in on to for and or with from does do can please'.split())


def terms(text):
    return [word for word in re.findall(r'[a-z0-9]+', text.lower()) if len(word) > 1 and word not in STOP]


class WordTokenizer:
    def encode(self, text, **kwargs):
        return text.split()
    def decode(self, tokens, **kwargs):
        return ' '.join(tokens)


def prepare(data_dir):
    catalog, records = [], []
    for book in read_manifest(data_dir):
        path = data_dir / 'books' / book['filename']
        item = {**book, 'status': 'missing', 'chapters': [], 'bytes': 0}
        if path.is_file():
            try:
                validate_book(book, path)
                if book.get('reader_only'):
                    version = hashlib.sha256((book['sha256'] + json.dumps(book, sort_keys=True)).encode()).hexdigest()
                    item.update(status='readable', bytes=path.stat().st_size, version=version,
                                chapters=[{**chapter, 'topics': [], 'exercises': [], 'pages': []} for chapter in book.get('chapters', [])])
                    catalog.append(item)
                    continue
                chunks, chapters = extract_book(book, path, WordTokenizer())
                version = hashlib.sha256((book['sha256'] + PIPELINE_VERSION + json.dumps(book, sort_keys=True)).encode()).hexdigest()
                records.extend(chunks)
                item.update(status='ready', chapters=chapters, bytes=path.stat().st_size, version=version)
            except (ValueError, RuntimeError, KeyError) as error:
                item.update(status='needs_review', error=str(error))
        catalog.append(item)
    return catalog, LexicalRetriever(records)


class LexicalRetriever:
    def __init__(self, records):
        self.rows = [(row, Counter(terms(row['text']))) for row in records]

    def search(self, query, book, chapter=None, limit=5):
        from rag.language import retrieval_text
        query = retrieval_text(query)
        words = set(terms(query))
        if not words:
            return []
        rows = [(row, counts) for row, counts in self.rows if row['book'] == book and (chapter is None or row['chapter_number'] == chapter)]
        frequency = {word: sum(word in counts for _, counts in rows) for word in words}
        ranked = []
        for row, counts in rows:
            if sum(word in counts for word in words) < min(2, len(words)):
                continue
            score = sum(math.log(1 + (len(rows) + 1) / (frequency[word] + 1)) * counts[word] / (counts[word] + 1.2 + sum(counts.values()) / 200) for word in words)
            ranked.append((score, row))
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [{**row, 'citation': index + 1, 'distance': 0} for index, (_, row) in enumerate(ranked[:limit])]
