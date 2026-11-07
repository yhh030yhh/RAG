from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import CreatedAtMixin, UUIDMixin, utcnow
from app.models.enums import DocumentStatus


class Document(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "documents"

    filename = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_type = Column(String(32), nullable=False)  # pdf / txt / md
    file_size = Column(Integer, nullable=False, default=0)
    status = Column(
        String(32), nullable=False, default=DocumentStatus.PENDING.value, index=True
    )
    chunk_count = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    indexed_at = Column(DateTime(timezone=True), nullable=True)

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )
