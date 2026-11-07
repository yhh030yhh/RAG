"""离线占位 LLM。"""
from typing import Iterator

from app.rag.llm.base import LLM


class FakeLLM(LLM):
    def generate(self, messages: list[dict]) -> str:
        last = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        return (
            "（离线占位回答）已收到您的问题：「" + last + "」。"
            "当前未配置 DeepSeek API Key，配置后即可获得基于知识库的真实回答。"
        )

    def stream(self, messages: list[dict]) -> Iterator[str]:
        text = self.generate(messages)
        for ch in text:
            yield ch
