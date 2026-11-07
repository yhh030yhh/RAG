from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas.tag import TagCreate, TagOut
from app.services import tag_service

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return tag_service.list_tags(db)


@router.post("", response_model=TagOut, status_code=201)
def create_tag(
    data: TagCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return tag_service.create_tag(db, data)


@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    tag_service.delete_tag(db, tag_id)
