"""RAG 调试接口。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.rag.embedding import get_embedder
from app.rag.llm import get_llm
from app.rag.pipeline import NO_ANSWER, build_context, build_source
from app.rag.prompt.templates import build_messages
from app.rag.retrieval.vector_store import search_chunks
from app.schemas.rag import RetrieveHitOut, RetrieveRequest, RetrieveResponse

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve_debug(
    body: RetrieveRequest,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    embedder = get_embedder()
    query_embedding = embedder.embed_query(body.question)
    hits = search_chunks(db, query_embedding, body.top_k, body.threshold)
    hit_outs = [
        RetrieveHitOut(
            index=i + 1,
            score=round(h.score, 4),
            chunk_index=h.chunk.chunk_index,
            page_number=h.chunk.page_number,
            content=h.chunk.content,
            filename=(h.chunk.meta or {}).get("filename", ""),
        )
        for i, h in enumerate(hits)
    ]

    answer = None
    if body.generate:
        context = build_context(hits) if hits else ""
        answer = (
            get_llm().generate(build_messages(context, [], body.question))
            if context
            else NO_ANSWER
        )

    return RetrieveResponse(
        question=body.question,
        query_embedding_dim=len(query_embedding),
        hits=hit_outs,
        answer=answer,
    )


@router.get("/health")
def rag_health(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return {
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "embedding_configured": settings.EMBEDDING_PROVIDER == "fake"
        or bool(settings.EMBEDDING_API_KEY),
        "llm_provider": settings.LLM_PROVIDER,
        "llm_configured": settings.LLM_PROVIDER == "fake"
        or bool(settings.DEEPSEEK_API_KEY),
        "document_count": db.query(Document).count(),
        "chunk_count": db.query(DocumentChunk).count(),
    }
