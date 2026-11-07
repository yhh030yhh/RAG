"""离线测试用 Embedding：基于字符 n-gram 特征哈希的确定性向量。

不产生真实语义，但相同/相似文本会得到相近向量，可跑通检索链路。
"""
import hashlib

from app.rag.embedding.base import Embedder


class FakeEmbedder(Embedder):
    def __init__(self, dim: int = 1024):
        self.dim = dim

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        text = text.lower()
        for n in (2, 3):
            for i in range(len(text) - n + 1):
                gram = text[i : i + n]
                h = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16)
                idx = h % self.dim
                sign = 1.0 if ((h >> 8) & 1) else -1.0
                vec[idx] += sign
        norm = sum(x * x for x in vec) ** 0.5
        if norm:
            vec = [x / norm for x in vec]
        return vec

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]
