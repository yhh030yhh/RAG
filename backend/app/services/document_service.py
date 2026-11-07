"""知识库文档业务逻辑：上传、解析、分块、向量化、存储。"""
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.enums import DocumentStatus
from app.rag.embedding import get_embedder
from app.rag.parser import get_parser
from app.rag.splitter import split_text

ALLOWED_EXTENSIONS = {"pdf", "txt", "md", "markdown"}


def _get(db: Session, document_id: UUID) -> Document:
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return doc


def list_documents(db: Session) -> list[Document]:
    return db.query(Document).order_by(Document.created_at.desc()).all()


def get_document(db: Session, document_id: UUID) -> Document:
    return _get(db, document_id)


def get_chunks(db: Session, document_id: UUID) -> list[DocumentChunk]:
    _get(db, document_id)
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )


def get_status(db: Session, document_id: UUID) -> dict:
    doc = _get(db, document_id)
    return {
        "id": doc.id,
        "status": doc.status,
        "chunk_count": doc.chunk_count,
        "error_message": doc.error_message,
        "indexed_at": doc.indexed_at,
    }


def delete_document(db: Session, document_id: UUID) -> None:
    doc = _get(db, document_id)
    if doc.file_path:
        try:
            Path(doc.file_path).unlink(missing_ok=True)
        except OSError:
            pass
    db.delete(doc)  # 通过 relationship cascade 删除关联 chunk
    db.commit()


def mark_pending(db: Session, document_id: UUID) -> Document:
    doc = _get(db, document_id)
    doc.status = DocumentStatus.PENDING.value
    doc.error_message = None
    doc.chunk_count = 0
    db.commit()
    db.refresh(doc)
    return doc


def process_document(db: Session, document_id: UUID) -> None:
    """解析 -> 分块 -> Embedding -> 入库，并更新文档状态。"""
    doc = db.get(Document, document_id)
    if not doc:
        return
    try:
        doc.status = DocumentStatus.PROCESSING.value
        db.commit()

        parser = get_parser(doc.file_type)
        pages = parser.parse(doc.file_path)
        embedder = get_embedder()

        items: list[tuple[str, int | None]] = []
        for page in pages:
            for chunk_text in split_text(
                page.text,
                settings.CHUNK_SIZE,
                settings.CHUNK_OVERLAP,
                settings.CHARS_PER_TOKEN,
            ):
                items.append((chunk_text, page.page_number))

        texts = [t for t, _ in items]
        embeddings = embedder.embed_texts(texts) if texts else []

        # 幂等：先删除旧 chunk，再写入新 chunk
        db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
        for i, ((text, page_num), emb) in enumerate(zip(items, embeddings)):
            db.add(
                DocumentChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    content=text,
                    page_number=page_num,
                    meta={"filename": doc.filename},
                    embedding=emb,
                )
            )

        doc.status = DocumentStatus.COMPLETED.value
        doc.chunk_count = len(items)
        doc.indexed_at = datetime.now(timezone.utc)
        doc.error_message = None
        db.commit()
    except Exception as e:  # noqa: BLE001
        db.rollback()
        doc = db.get(Document, document_id)
        if doc:
            doc.status = DocumentStatus.FAILED.value
            doc.error_message = str(e)
            db.commit()


def process_document_background(document_id: UUID) -> None:
    """后台任务入口：使用独立会话。"""
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        process_document(db, document_id)
    finally:
        db.close()
