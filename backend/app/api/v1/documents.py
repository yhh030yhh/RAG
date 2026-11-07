from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.document import Document
from app.models.enums import DocumentStatus
from app.schemas.document import DocumentChunkOut, DocumentOut
from app.services.document_service import (
    delete_document,
    get_chunks,
    get_document,
    get_status,
    list_documents,
    mark_pending,
    process_document_background,
)

router = APIRouter(prefix="/documents", tags=["documents"])


def _ext(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    ext = "md" if _ext(file.filename) == "markdown" else _ext(file.filename)
    if ext not in ("pdf", "txt", "md"):
        raise HTTPException(status_code=400, detail="仅支持 PDF / TXT / Markdown 文件")

    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400, detail=f"文件超过 {settings.MAX_UPLOAD_SIZE_MB}MB 限制"
        )

    doc = Document(
        filename=file.filename,
        file_type=ext,
        file_path="",
        file_size=len(content),
        status=DocumentStatus.PENDING.value,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    storage = Path(settings.STORAGE_DIR)
    storage.mkdir(parents=True, exist_ok=True)
    file_path = storage / f"{doc.id}.{ext}"
    file_path.write_bytes(content)
    doc.file_path = str(file_path)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(process_document_background, doc.id)
    return doc


@router.get("", response_model=list[DocumentOut])
def list_all(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return list_documents(db)


@router.get("/{document_id}", response_model=DocumentOut)
def read_document(
    document_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    return get_document(db, document_id)


@router.delete("/{document_id}", status_code=204)
def remove_document(
    document_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    delete_document(db, document_id)


@router.post("/{document_id}/reindex", response_model=DocumentOut)
def reindex_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    doc = mark_pending(db, document_id)
    background_tasks.add_task(process_document_background, doc.id)
    return doc


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkOut])
def read_chunks(
    document_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    return get_chunks(db, document_id)


@router.get("/{document_id}/status")
def read_status(
    document_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    return get_status(db, document_id)
