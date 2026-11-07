"""向量检索：PostgreSQL(pgvector) 与 SQLite 双路径。"""
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document_chunk import DocumentChunk


@dataclass
class RetrievalHit:
    chunk: DocumentChunk
    score: float


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def search_chunks(
    db: Session,
    query_embedding: list[float],
    top_k: int,
    threshold: float | None = None,
) -> list[RetrievalHit]:
    """返回按相似度降序的 Top-K 命中；threshold 非空时过滤低于阈值的结果。"""
    if settings.is_postgres:
        hits = _search_pgvector(db, query_embedding, top_k)
    else:
        hits = _search_sqlite(db, query_embedding, top_k)
    if threshold is not None:
        hits = [h for h in hits if h.score >= threshold]
    return hits


def _search_sqlite(
    db: Session, query_embedding: list[float], top_k: int
) -> list[RetrievalHit]:
    chunks = (
        db.query(DocumentChunk).filter(DocumentChunk.embedding.isnot(None)).all()
    )
    hits = [
        RetrievalHit(chunk=c, score=cosine_similarity(query_embedding, c.embedding))
        for c in chunks
    ]
    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:top_k]


def _search_pgvector(
    db: Session, query_embedding: list[float], top_k: int
) -> list[RetrievalHit]:
    vec_str = "[" + ",".join(str(float(x)) for x in query_embedding) + "]"
    sql = text(
        """
        SELECT c.id, 1 - (c.embedding <=> CAST(:q AS vector)) AS similarity
        FROM document_chunks c
        WHERE c.embedding IS NOT NULL
        ORDER BY c.embedding <=> CAST(:q AS vector)
        LIMIT :k
        """
    )
    rows = db.execute(sql, {"q": vec_str, "k": top_k}).fetchall()
    id_to_score = {row[0]: float(row[1]) for row in rows}
    if not id_to_score:
        return []
    chunks = (
        db.query(DocumentChunk).filter(DocumentChunk.id.in_(id_to_score.keys())).all()
    )
    hits = [RetrievalHit(chunk=c, score=id_to_score[c.id]) for c in chunks]
    hits.sort(key=lambda h: h.score, reverse=True)
    return hits
