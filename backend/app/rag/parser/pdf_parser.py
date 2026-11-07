import pymupdf

from app.rag.parser.base import Parser, ParsedPage


class PdfParser(Parser):
    file_type = "pdf"

    def parse(self, file_path: str) -> list[ParsedPage]:
        doc = pymupdf.open(file_path)
        pages: list[ParsedPage] = []
        try:
            for i, page in enumerate(doc):
                text = page.get_text().strip()
                if text:
                    pages.append(ParsedPage(text=text, page_number=i + 1))
        finally:
            doc.close()
        return pages
