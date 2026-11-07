from app.rag.parser.base import Parser, ParsedPage


class TxtParser(Parser):
    file_type = "txt"

    def parse(self, file_path: str) -> list[ParsedPage]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        return [ParsedPage(text=text)] if text.strip() else []
