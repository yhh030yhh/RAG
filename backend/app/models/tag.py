from sqlalchemy import Column, String

from app.core.database import Base
from app.models.base import CreatedAtMixin, UUIDMixin


class Tag(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "tags"

    name = Column(String(64), unique=True, nullable=False)
