from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.core.utils import slugify, unique_slug
from app.models.article import Article
from app.models.enums import ArticleStatus
from app.models.tag import Tag
from app.schemas.article import ArticleCreate, ArticleUpdate


def _get(db: Session, article_id: UUID) -> Article:
    a = db.get(Article, article_id)
    if not a:
        raise HTTPException(status_code=404, detail="文章不存在")
    return a


def get_article(db: Session, article_id: UUID) -> Article:
    a = (
        db.query(Article)
        .options(selectinload(Article.tags), selectinload(Article.category))
        .filter(Article.id == article_id)
        .first()
    )
    if not a:
        raise HTTPException(status_code=404, detail="文章不存在")
    return a


def list_articles(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    status: str | None = None,
    category_id: UUID | None = None,
    tag_id: UUID | None = None,
) -> tuple[list[Article], int]:
    q = db.query(Article).options(
        selectinload(Article.tags), selectinload(Article.category)
    )
    if search:
        like = f"%{search}%"
        q = q.filter(Article.title.ilike(like) | Article.content.ilike(like))
    if status:
        q = q.filter(Article.status == status)
    if category_id:
        q = q.filter(Article.category_id == category_id)
    if tag_id:
        q = q.join(Article.tags).filter(Tag.id == tag_id)

    total = q.count()
    items = (
        q.order_by(Article.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def _gen_slug(db: Session, title: str) -> str:
    base = slugify(title)
    return unique_slug(
        base, lambda s: db.query(Article).filter(Article.slug == s).first() is not None
    )


def _resolve_tags(db: Session, tag_ids: list[UUID]) -> list[Tag]:
    if not tag_ids:
        return []
    return db.query(Tag).filter(Tag.id.in_(tag_ids)).all()


def create_article(db: Session, data: ArticleCreate, author_id: UUID) -> Article:
    article = Article(
        title=data.title,
        slug=_gen_slug(db, data.title),
        summary=data.summary,
        content=data.content,
        category_id=data.category_id,
        author_id=author_id,
        status=ArticleStatus.DRAFT.value,
    )
    article.tags = _resolve_tags(db, data.tag_ids)
    db.add(article)
    db.commit()
    return get_article(db, article.id)


def update_article(db: Session, article_id: UUID, data: ArticleUpdate) -> Article:
    article = _get(db, article_id)
    article.title = data.title
    article.summary = data.summary
    article.content = data.content
    article.category_id = data.category_id
    article.tags = _resolve_tags(db, data.tag_ids)
    db.commit()
    return get_article(db, article_id)


def delete_article(db: Session, article_id: UUID) -> None:
    article = _get(db, article_id)
    db.delete(article)
    db.commit()


def publish_article(db: Session, article_id: UUID) -> Article:
    article = _get(db, article_id)
    article.status = ArticleStatus.PUBLISHED.value
    article.published_at = datetime.now(timezone.utc)
    db.commit()
    return get_article(db, article_id)


def archive_article(db: Session, article_id: UUID) -> Article:
    article = _get(db, article_id)
    article.status = ArticleStatus.ARCHIVED.value
    db.commit()
    return get_article(db, article_id)
