from sqlalchemy import Column, String

from app.core.database import Base
from app.models.base import CreatedAtMixin, UUIDMixin


class User(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "users"

    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default="admin")
