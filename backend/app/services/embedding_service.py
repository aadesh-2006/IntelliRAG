import math
import hashlib
from abc import ABC, abstractmethod
from typing import List
from app.config import settings

class BaseEmbeddingService(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

class LocalEmbeddingService(BaseEmbeddingService):
    def __init__(self, dimension: int = settings.VECTOR_DIMENSION):
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def _generate_vector(self, text: str) -> List[float]:
        if not text or not text.strip():
            return [0.0] * self._dimension

        clean = text.lower().strip()
        words = clean.split()
        vector = [0.0] * self._dimension

        for w_idx, word in enumerate(words):
            word_hash = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            for i in range(8):
                bucket = (word_hash + i * 31) % self._dimension
                sign = 1.0 if ((word_hash >> i) & 1) == 1 else -1.0
                weight = 1.0 / math.log2(w_idx + 2)
                vector[bucket] += sign * weight

        for i in range(len(clean) - 2):
            trigram = clean[i:i + 3]
            tri_hash = int(hashlib.md5(trigram.encode("utf-8")).hexdigest(), 16)
            bucket = tri_hash % self._dimension
            sign = 1.0 if (tri_hash & 1) == 1 else -1.0
            vector[bucket] += sign * 0.5

        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [round(v / norm, 6) for v in vector]
        else:
            vector[0] = 1.0

        return vector

    def embed_text(self, text: str) -> List[float]:
        return self._generate_vector(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._generate_vector(t) for t in texts]

embedding_service: BaseEmbeddingService = LocalEmbeddingService()
