import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class SectionRange:
    name: str
    start_page: int
    end_page: int
    confidence: float


SECTION_PATTERNS = {
    "introduction": re.compile(r"\bintroduction\b", re.IGNORECASE),
    "methods": re.compile(r"\b(methods|methodology)\b", re.IGNORECASE),
    "results": re.compile(r"\bresults\b", re.IGNORECASE),
    "discussion": re.compile(r"\bdiscussion\b", re.IGNORECASE),
    "references": re.compile(r"\breferences\b", re.IGNORECASE),
}


def _find_section_pages(pages: List[Tuple[int, str]]) -> Dict[str, int]:
    hits = {}
    for page_num, text in pages:
        for name, pattern in SECTION_PATTERNS.items():
            if name in hits:
                continue
            if pattern.search(text):
                hits[name] = page_num
    return hits


def section_pages(pages: List[Tuple[int, str]]) -> List[SectionRange]:
    hits = _find_section_pages(pages)
    if not hits:
        if pages:
            return [SectionRange(name="full_text", start_page=1, end_page=pages[-1][0], confidence=0.2)]
        return []
    ordered = sorted(hits.items(), key=lambda item: item[1])
    ranges: List[SectionRange] = []
    for idx, (name, start_page) in enumerate(ordered):
        end_page = pages[-1][0]
        if idx + 1 < len(ordered):
            end_page = ordered[idx + 1][1] - 1
        ranges.append(SectionRange(name=name, start_page=start_page, end_page=max(start_page, end_page), confidence=0.6))
    return ranges


def section_lookup(ranges: List[SectionRange]) -> Dict[str, SectionRange]:
    return {section.name: section for section in ranges}
