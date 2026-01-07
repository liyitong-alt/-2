from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class PageText:
    page: int
    text: str
    char_count: int
    suspicious: bool


@dataclass
class PdfReadResult:
    pages: List[PageText]
    source: str


def _analyze_page(text: str) -> tuple[int, bool]:
    char_count = len(text.strip())
    suspicious = char_count < 30
    if any(char.isdigit() for char in text[:100]) and char_count < 100:
        suspicious = True
    return char_count, suspicious


def read_pdf(path: Path) -> PdfReadResult:
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(path)
        pages = []
        for index in range(len(doc)):
            page = doc.load_page(index)
            text = page.get_text("text")
            char_count, suspicious = _analyze_page(text)
            pages.append(PageText(page=index + 1, text=text, char_count=char_count, suspicious=suspicious))
        return PdfReadResult(pages=pages, source="pymupdf")
    except Exception:
        import pdfplumber

        pages = []
        with pdfplumber.open(path) as pdf:
            for index, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                char_count, suspicious = _analyze_page(text)
                pages.append(PageText(page=index + 1, text=text, char_count=char_count, suspicious=suspicious))
        return PdfReadResult(pages=pages, source="pdfplumber")
