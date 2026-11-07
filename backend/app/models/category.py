from sqlalchemy import Column, String

from app.core.database import Base
from app.models.base import CreatedAtMixin, UUIDMixin


class Category(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "categories"

    name = Column(String(128), unique=True, nullable=False)
    description = Column(String(512), nullable=True)
