"""云端 Embedding（OpenAI 兼容 /embeddings 接口）。"""
import httpx

from app.rag.embedding.base import Embedder


class CloudEmbedder(Embedder):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        dim: int,
        batch_size: int = 16,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.dim = dim
        self.batch_size = batch_size

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            raise RuntimeError(
                "未配置 EMBEDDING_API_KEY。请在 backend/.env 中填写，"
                "或将 EMBEDDING_PROVIDER 设为 fake 进行离线测试。"
            )
        url = f"{self.base_url}/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = httpx.post(
            url,
            headers=headers,
            json={"model": self.model, "input": texts},
            timeout=60.0,
        )
        resp.raise_for_status()
        data = sorted(resp.json()["data"], key=lambda d: d["index"])
        return [d["embedding"] for d in data]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        result: list[list[float]] = []
        for i in range(0, len(texts), self.batch_size):
            result.extend(self._embed_batch(texts[i : i + self.batch_size]))
        return result
