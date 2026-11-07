from sqlalchemy import Column, ForeignKey, Integer, JSON, Text, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import CreatedAtMixin, UUIDMixin
from app.models.embedding_type import EmbeddingVectorType


class DocumentChunk(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "document_chunks"

    document_id = Column(
        Uuid, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    # 属性名避开 SQLAlchemy 保留字 metadata，列名仍为 metadata
    meta = Column("metadata", JSON, nullable=True)
    embedding = Column(EmbeddingVectorType(), nullable=True)

    document = relationship("Document", back_populates="chunks")
