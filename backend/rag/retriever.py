import threading


class Retriever:
    def __init__(self, collection, model, max_distance):
        self.collection, self.model, self.max_distance = collection, model, max_distance
        self.lock = threading.Lock()

    def search(self, query: str, book: str, chapter: int | None = None, limit=5):
        from rag.language import retrieval_text
        query = retrieval_text(query)
        where = {'book': book} if chapter is None else {'$and': [{'book': book}, {'chapter_number': chapter}]}
        count = len(self.collection.get(where=where, include=[])['ids'])
        if not count:
            return []
        with self.lock:
            vector = self.model.encode(query, normalize_embeddings=True).tolist()
        result = self.collection.query(query_embeddings=[vector], n_results=min(limit, count), where=where,
                                       include=['documents', 'metadatas', 'distances'])
        sources = []
        for identifier, text, meta, distance in zip(result['ids'][0], result['documents'][0], result['metadatas'][0], result['distances'][0]):
            if distance <= self.max_distance:
                sources.append({'id': identifier, 'text': text, **{key: value for key, value in meta.items() if key != 'version'},
                                'distance': round(distance, 4), 'citation': len(sources) + 1})
        return sources
