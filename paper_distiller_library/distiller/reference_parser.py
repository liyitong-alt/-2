import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ReferenceEntry:
    citation_key: str
    entry: str
    doi: str | None


DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
AUTHOR_YEAR_PATTERN = re.compile(r"([A-Z][A-Za-z\-]+)\s*(?:et al\.)?\s*\((\d{4})\)")


def parse_references(text: str) -> List[ReferenceEntry]:
    entries: List[ReferenceEntry] = []
    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        doi_match = DOI_PATTERN.search(clean)
        doi = doi_match.group(0) if doi_match else None
        author_year = AUTHOR_YEAR_PATTERN.search(clean)
        if author_year:
            citation_key = f"{author_year.group(1)}-{author_year.group(2)}"
        elif doi:
            citation_key = doi
        else:
            citation_key = ""
        entries.append(ReferenceEntry(citation_key=citation_key, entry=clean, doi=doi))
    return entries


def extract_in_text_citations(text: str) -> List[str]:
    return [match.group(0) for match in AUTHOR_YEAR_PATTERN.finditer(text)]


def build_citation_map(entries: List[ReferenceEntry]) -> Dict[str, str]:
    mapping = {}
    for entry in entries:
        if entry.citation_key:
            mapping[entry.citation_key] = entry.entry
    return mapping
