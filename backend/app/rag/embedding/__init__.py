from functools import lru_cache

from app.core.config import settings
from app.rag.embedding.base import Embedder
from app.rag.embedding.cloud import CloudEmbedder
from app.rag.embedding.fake import FakeEmbedder


@lru_cache
def get_embedder() -> Embedder:
    if settings.EMBEDDING_PROVIDER == "fake":
        return FakeEmbedder(dim=settings.EMBEDDING_DIM)
    return CloudEmbedder(
        base_url=settings.EMBEDDING_BASE_URL,
        api_key=settings.EMBEDDING_API_KEY,
        model=settings.EMBEDDING_MODEL,
        dim=settings.EMBEDDING_DIM,
        batch_size=settings.EMBEDDING_BATCH_SIZE,
    )


__all__ = ["Embedder", "get_embedder"]
