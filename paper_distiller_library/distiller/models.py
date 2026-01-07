from dataclasses import dataclass
from typing import List

from distiller.pdf_reader import PageText


@dataclass
class ParsedPaper:
    pages: List[PageText]
    source: str
