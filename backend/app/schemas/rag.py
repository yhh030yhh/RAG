from typing import Optional

from pydantic import BaseModel, Field


class RetrieveRequest(BaseModel):
    question: str
    top_k: int = Field(5, ge=1, le=50)
    threshold: Optional[float] = None
    generate: bool = False


class RetrieveHitOut(BaseModel):
    index: int
    score: float
    chunk_index: int
    page_number: Optional[int] = None
    content: str
    filename: str


class RetrieveResponse(BaseModel):
    question: str
    query_embedding_dim: int
    hits: list[RetrieveHitOut]
    answer: Optional[str] = None
