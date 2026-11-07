"""Embedding 抽象。"""
from abc import ABC, abstractmethod


class Embedder(ABC):
    dim: int

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """批量向量化。"""

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]
