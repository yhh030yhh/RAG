"""LLM 抽象。"""
from abc import ABC, abstractmethod
from typing import Iterator


class LLM(ABC):
    @abstractmethod
    def generate(self, messages: list[dict]) -> str:
        """非流式生成。"""

    @abstractmethod
    def stream(self, messages: list[dict]) -> Iterator[str]:
        """流式生成，逐段 yield 文本。"""
