"""解析器抽象。"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ParsedPage:
    text: str
    page_number: int | None = None


class Parser(ABC):
    file_type: str = ""

    @abstractmethod
    def parse(self, file_path: str) -> list[ParsedPage]:
        """解析文件，返回按页/段组织的文本。"""
