from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.chat import ChatMessage
from app.rag import rag_service
from app.rag.llm import get_llm
from app.rag.pipeline import build_source, retrieve
from app.rag.prompt.templates import build_messages
from app.schemas.chat import (
    ChatMessageOut,
    ChatQuestion,
    ChatSessionCreate,
    ChatSessionOut,
)
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionOut, status_code=201)
def create_session(
    data: ChatSessionCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    return chat_service.create_session(db, current.id, data.title)


@router.get("/sessions", response_model=list[ChatSessionOut])
def list_sessions(
    db: Session = Depends(get_db), current=Depends(get_current_user)
):
    return chat_service.list_sessions(db, current.id)


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
def list_messages(
    session_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return chat_service.list_messages(db, session_id)


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    chat_service.delete_session(db, session_id)


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageOut)
def submit_message(
    session_id: UUID,
    data: ChatQuestion,
    stream: bool = Query(False),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    chat_service.get_session(db, session_id)

    if stream:
        history = rag_service.get_history(db, session_id)
        db.add(ChatMessage(session_id=session_id, role="user", content=data.content))
        db.commit()
        chat_service.auto_title(db, session_id, data.content)
        hits, context = retrieve(db, data.content)
        sources = [build_source(h, i) for i, h in enumerate(hits)]
        return StreamingResponse(
            rag_service.stream_question(
                session_id, data.content, history, context, sources
            ),
            media_type="text/event-stream",
        )

    assistant = rag_service.answer_question(db, session_id, data.content)
    chat_service.auto_title(db, session_id, data.content)
    return assistant
