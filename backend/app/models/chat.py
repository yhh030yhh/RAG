from sqlalchemy import Column, ForeignKey, JSON, String, Text, Uuid
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import CreatedAtMixin, TimestampMixin, UUIDMixin


class ChatSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_sessions"

    user_id = Column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title = Column(String(255), nullable=False, default="新会话")

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class ChatMessage(Base, UUIDMixin, CreatedAtMixin):
    __tablename__ = "chat_messages"

    session_id = Column(
        Uuid,
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(32), nullable=False)  # user / assistant
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)

    session = relationship("ChatSession", back_populates="messages")
