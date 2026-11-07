"""RAG 流程编排：检索 -> 构建上下文 -> 生成。"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.rag.embedding import get_embedder
from app.rag.llm import get_llm
from app.rag.prompt.templates import build_messages
from app.rag.retrieval.vector_store import RetrievalHit, search_chunks

NO_ANSWER = "知识库中没有找到与您问题相关的内容，请尝试其他问题或上传相关文档。"


@dataclass
class RagAnswer:
    answer: str
    sources: list[dict]


def build_context(hits: list[RetrievalHit]) -> str:
    parts = [f"[{i + 1}] {h.chunk.content}" for i, h in enumerate(hits)]
    return "\n\n".join(parts)


def build_source(hit: RetrievalHit, idx: int) -> dict:
    chunk = hit.chunk
    meta = chunk.meta or {}
    return {
        "index": idx + 1,
        "document_id": str(chunk.document_id),
        "filename": meta.get("filename", ""),
        "chunk_index": chunk.chunk_index,
        "page_number": chunk.page_number,
        "score": round(hit.score, 4),
        "content": chunk.content[:200],
    }


def retrieve(
    db: Session,
    question: str,
    top_k: int | None = None,
    threshold: float | None = None,
) -> tuple[list[RetrievalHit], str]:
    top_k = settings.TOP_K if top_k is None else top_k
    threshold = settings.SIMILARITY_THRESHOLD if threshold is None else threshold
    query_embedding = get_embedder().embed_query(question)
    hits = search_chunks(db, query_embedding, top_k, threshold)
    return hits, build_context(hits) if hits else ""


def retrieve_and_generate(
    db: Session, question: str, history: list[dict] | None = None
) -> RagAnswer:
    hits, context = retrieve(db, question)
    if not hits:
        return RagAnswer(answer=NO_ANSWER, sources=[])
    answer = get_llm().generate(build_messages(context, history or [], question))
    return RagAnswer(
        answer=answer, sources=[build_source(h, i) for i, h in enumerate(hits)]
    )
