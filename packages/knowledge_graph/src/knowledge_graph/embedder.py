from abc import ABC, abstractmethod
from typing import List

try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


class Embedder(ABC):
    """
    Interface for generating vector embeddings from text.
    """

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        pass

    @property
    @abstractmethod
    def vector_size(self) -> int:
        pass


class LocalSentenceTransformerEmbedder(Embedder):
    """
    Local embedder using the `sentence-transformers` library.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError("sentence-transformers is not installed")
        self._model = SentenceTransformer(model_name)
        self._vector_size = self._model.get_sentence_embedding_dimension()

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    @property
    def vector_size(self) -> int:
        return self._vector_size


class MockEmbedder(Embedder):
    def __init__(self, size: int = 384):
        self._size = size

    def embed(self, texts: List[str]) -> List[List[float]]:
        import random

        return [[random.random() for _ in range(self._size)] for _ in texts]

    @property
    def vector_size(self) -> int:
        return self._size
