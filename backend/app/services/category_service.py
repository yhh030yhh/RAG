from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def list_categories(db: Session) -> list[Category]:
    return db.query(Category).order_by(Category.created_at.desc()).all()


def _get(db: Session, category_id: UUID) -> Category:
    c = db.get(Category, category_id)
    if not c:
        raise HTTPException(status_code=404, detail="分类不存在")
    return c


def _name_exists(db: Session, name: str, exclude_id: UUID | None = None) -> bool:
    q = db.query(Category).filter(Category.name == name)
    if exclude_id:
        q = q.filter(Category.id != exclude_id)
    return q.first() is not None


def create_category(db: Session, data: CategoryCreate) -> Category:
    if _name_exists(db, data.name):
        raise HTTPException(status_code=409, detail="分类名称已存在")
    c = Category(name=data.name, description=data.description)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def update_category(db: Session, category_id: UUID, data: CategoryUpdate) -> Category:
    c = _get(db, category_id)
    if _name_exists(db, data.name, exclude_id=category_id):
        raise HTTPException(status_code=409, detail="分类名称已存在")
    c.name = data.name
    c.description = data.description
    db.commit()
    db.refresh(c)
    return c


def delete_category(db: Session, category_id: UUID) -> None:
    c = _get(db, category_id)
    db.delete(c)
    db.commit()
