from fastapi import APIRouter

from app.api.v1 import articles, auth, categories, chat, documents, rag, tags

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(articles.router)
api_router.include_router(categories.router)
api_router.include_router(tags.router)
api_router.include_router(documents.router)
api_router.include_router(chat.router)
api_router.include_router(rag.router)
