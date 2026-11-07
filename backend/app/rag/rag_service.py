"""RAG 问答服务：会话消息持久化 + 问答/流式回答。"""
import json
from typing import Iterator
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.chat import ChatMessage
from app.rag.llm import get_llm
from app.rag.pipeline import NO_ANSWER, build_source, retrieve
from app.rag.prompt.templates import build_messages


def get_history(db: Session, session_id: UUID, limit: int = 10) -> list[dict]:
    msgs = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id,
            ChatMessage.role.in_(["user", "assistant"]),
        )
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in msgs[-limit:]]


def _save_assistant(session_id: UUID, content: str, sources: list[dict]) -> None:
    db = SessionLocal()
    try:
        db.add(
            ChatMessage(
                session_id=session_id, role="assistant", content=content, sources=sources
            )
        )
        db.commit()
    finally:
        db.close()


def answer_question(db: Session, session_id: UUID, question: str) -> ChatMessage:
    """非流式问答：保存用户消息 + 检索生成 + 保存助手消息。"""
    history = get_history(db, session_id)
    db.add(ChatMessage(session_id=session_id, role="user", content=question))
    db.commit()

    hits, context = retrieve(db, question)
    sources = [build_source(h, i) for i, h in enumerate(hits)]
    if context:
        answer = get_llm().generate(build_messages(context, history, question))
    else:
        answer = NO_ANSWER

    assistant = ChatMessage(
        session_id=session_id, role="assistant", content=answer, sources=sources
    )
    db.add(assistant)
    db.commit()
    db.refresh(assistant)
    return assistant


def stream_question(
    session_id: UUID,
    question: str,
    history: list[dict],
    context: str,
    sources: list[dict],
) -> Iterator[str]:
    """SSE 流式回答（用户消息由调用方已保存，助手消息在流式结束后保存）。"""
    yield f"event: sources\ndata: {json.dumps(sources, ensure_ascii=False)}\n\n"

    if not context:
        _save_assistant(session_id, NO_ANSWER, sources)
        yield f"data: {json.dumps(NO_ANSWER, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
        return

    messages = build_messages(context, history, question)
    llm = get_llm()
    buffer = ""
    try:
        for token in llm.stream(messages):
            buffer += token
            yield f"data: {json.dumps(token, ensure_ascii=False)}\n\n"
    except Exception as e:  # noqa: BLE001
        buffer = f"生成回答失败：{e}"
        yield f"data: {json.dumps(buffer, ensure_ascii=False)}\n\n"

    _save_assistant(session_id, buffer, sources)
    yield "data: [DONE]\n\n"
