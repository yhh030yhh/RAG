from functools import lru_cache

from app.core.config import settings
from app.rag.llm.base import LLM
from app.rag.llm.deepseek import DeepSeekLLM
from app.rag.llm.fake import FakeLLM


@lru_cache
def get_llm() -> LLM:
    if settings.LLM_PROVIDER == "fake":
        return FakeLLM()
    return DeepSeekLLM(
        settings.DEEPSEEK_API_KEY, settings.DEEPSEEK_BASE_URL, settings.DEEPSEEK_MODEL
    )


__all__ = ["LLM", "get_llm"]
