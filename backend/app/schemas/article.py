from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryOut
from app.schemas.tag import TagOut


class ArticleBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: str = ""
    category_id: Optional[UUID] = None
    tag_ids: List[UUID] = Field(default_factory=list)


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(ArticleBase):
    pass


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    summary: Optional[str] = None
    content: str
    category_id: Optional[UUID] = None
    author_id: Optional[UUID] = None
    status: str
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryOut] = None
    tags: List[TagOut] = Field(default_factory=list)
