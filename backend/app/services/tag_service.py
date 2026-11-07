from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import TagCreate


def list_tags(db: Session) -> list[Tag]:
    return db.query(Tag).order_by(Tag.created_at.desc()).all()


def create_tag(db: Session, data: TagCreate) -> Tag:
    if db.query(Tag).filter(Tag.name == data.name).first():
        raise HTTPException(status_code=409, detail="标签已存在")
    t = Tag(name=data.name)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def delete_tag(db: Session, tag_id: UUID) -> None:
    t = db.get(Tag, tag_id)
    if not t:
        raise HTTPException(status_code=404, detail="标签不存在")
    db.delete(t)
    db.commit()
