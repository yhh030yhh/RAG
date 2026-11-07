from app.rag.parser.base import Parser, ParsedPage
from app.rag.parser.md_parser import MarkdownParser
from app.rag.parser.pdf_parser import PdfParser
from app.rag.parser.txt_parser import TxtParser

_PARSERS: dict[str, Parser] = {}
for _p in (PdfParser(), TxtParser(), MarkdownParser()):
    _PARSERS[_p.file_type] = _p
_PARSERS["markdown"] = _PARSERS["md"]


def get_parser(file_type: str) -> Parser:
    ft = "md" if file_type.lower() == "markdown" else file_type.lower()
    parser = _PARSERS.get(ft)
    if not parser:
        raise ValueError(f"不支持的文件类型: {file_type}")
    return parser


__all__ = ["Parser", "ParsedPage", "get_parser"]
