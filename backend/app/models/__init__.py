"""导入所有模型，确保 Base.metadata 能感知全部数据表。"""
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app.models.article import Article, article_tags
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.chat import ChatSession, ChatMessage

__all__ = [
    "User",
    "Category",
    "Tag",
    "Article",
    "article_tags",
    "Document",
    "DocumentChunk",
    "ChatSession",
    "ChatMessage",
]
