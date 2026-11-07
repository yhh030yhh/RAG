from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas.article import ArticleCreate, ArticleOut, ArticleUpdate
from app.schemas.common import Page
from app.services import article_service

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=Page[ArticleOut])
def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    status: str | None = None,
    category_id: UUID | None = None,
    tag_id: UUID | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    items, total = article_service.list_articles(
        db, page, page_size, search, status, category_id, tag_id
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("", response_model=ArticleOut, status_code=201)
def create_article(
    data: ArticleCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    return article_service.create_article(db, data, current.id)


@router.get("/{article_id}", response_model=ArticleOut)
def get_article(
    article_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return article_service.get_article(db, article_id)


@router.put("/{article_id}", response_model=ArticleOut)
def update_article(
    article_id: UUID,
    data: ArticleUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return article_service.update_article(db, article_id, data)


@router.delete("/{article_id}", status_code=204)
def delete_article(
    article_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    article_service.delete_article(db, article_id)


@router.post("/{article_id}/publish", response_model=ArticleOut)
def publish_article(
    article_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return article_service.publish_article(db, article_id)


@router.post("/{article_id}/archive", response_model=ArticleOut)
def archive_article(
    article_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return article_service.archive_article(db, article_id)
