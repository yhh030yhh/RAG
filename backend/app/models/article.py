from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    Text,
    Uuid,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin, utcnow
from app.models.enums import ArticleStatus

# 文章-标签 多对多关联表
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column(
        "article_id",
        Uuid,
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Uuid,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Article(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "articles"

    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    summary = Column(String(512), nullable=True)
    content = Column(Text, nullable=False, default="")
    category_id = Column(
        Uuid, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    author_id = Column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status = Column(String(32), nullable=False, default=ArticleStatus.DRAFT.value)
    published_at = Column(DateTime(timezone=True), nullable=True)

    category = relationship("Category", backref="articles")
    author = relationship("User", backref="articles")
    tags = relationship("Tag", secondary=article_tags, backref="articles")
