import re

from app.rag.parser.base import Parser, ParsedPage


class MarkdownParser(Parser):
    file_type = "md"

    def parse(self, file_path: str) -> list[ParsedPage]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        # 去除 YAML front matter
        text = re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.DOTALL)
        return [ParsedPage(text=text)] if text.strip() else []
