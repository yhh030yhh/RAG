"""聊天会话管理业务逻辑。"""
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.base import utcnow
from app.models.chat import ChatMessage, ChatSession


def create_session(db: Session, user_id: UUID, title: str = "新会话") -> ChatSession:
    s = ChatSession(user_id=user_id, title=title)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def list_sessions(db: Session, user_id: UUID) -> list[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


def get_session(db: Session, session_id: UUID) -> ChatSession:
    s = db.get(ChatSession, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="会话不存在")
    return s


def list_messages(db: Session, session_id: UUID) -> list[ChatMessage]:
    get_session(db, session_id)
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def delete_session(db: Session, session_id: UUID) -> None:
    s = get_session(db, session_id)
    db.delete(s)  # cascade 删除消息
    db.commit()


def auto_title(db: Session, session_id: UUID, question: str) -> None:
    """首条消息时用问题前 30 字作为会话标题，并刷新 updated_at。"""
    s = db.get(ChatSession, session_id)
    if not s:
        return
    user_count = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id, ChatMessage.role == "user")
        .count()
    )
    if s.title == "新会话" and user_count == 1:
        s.title = question[:30] + ("..." if len(question) > 30 else "")
    s.updated_at = utcnow()
    db.commit()
