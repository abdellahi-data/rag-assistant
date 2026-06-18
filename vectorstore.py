# stores chunk vectors and finds the closest ones to a query. uses faiss for the similarity search.
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

import faiss
import numpy as np


# one piece of a pdf, plus where it came from (for citations)
@dataclass
class Chunk:
    text: str
    source: str   # filename
    page: int     # page number


# the contract for any vector store
class VectorStore(ABC):
    @abstractmethod
    def add(self, vectors, chunks):
        ...

    @abstractmethod
    def search(self, query_vector, k):
        ...

    @abstractmethod
    def save(self, path):
        ...

    @classmethod
    @abstractmethod
    def load(cls, path):
        ...


# faiss index using inner product. vectors are normalized first, so inner product == cosine similarity.
class FaissVectorStore(VectorStore):
    def __init__(self):
        self.index = None        # the faiss index, built on first add
        self._chunks = []        # the matching chunks, same order as the index

    def add(self, vectors, chunks):
        mat = np.array(vectors, dtype=np.float32)
        faiss.normalize_L2(mat)              # normalize so inner product = cosine
        if self.index is None:
            dim = mat.shape[1]               # vector length, from the model
            self.index = faiss.IndexFlatIP(dim)
        self.index.add(mat)
        self._chunks.extend(chunks)

    def search(self, query_vector, k):
        q = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(q)
        # faiss returns the scores and the row indices of the top k
        scores, idxs = self.index.search(q, k)
        hits = []
        for score, i in zip(scores[0], idxs[0]):
            if i == -1:                      # faiss pads with -1 if fewer than k results
                continue
            hits.append((float(score), self._chunks[i]))
        return hits

    def save(self, path):
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "chunks.json"), "w") as f:
            json.dump([c.__dict__ for c in self._chunks], f)

    @classmethod
    def load(cls, path):
        store = cls()
        store.index = faiss.read_index(os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "chunks.json")) as f:
            store._chunks = [Chunk(**d) for d in json.load(f)]
        return store