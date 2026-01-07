from __future__ import annotations

import re
from typing import List, Tuple

from wordfreq import zipf_frequency

from distiller.schemas import (
    AdvancedVocabularyItem,
    Contributions,
    Evidence,
    EvidenceItem,
    GlossaryTerm,
    IntroEvidenceRow,
    MethodsAndLimits,
    OutputBundle,
    StoryLine,
)

MAX_QUOTE_CHARS = 160


def _short_quote(text: str) -> str:
    trimmed = re.sub(r"\s+", " ", text.strip())
    return trimmed[:MAX_QUOTE_CHARS]


def _page_evidence(pages: List[Tuple[int, str]]) -> tuple[int | None, str]:
    for page_num, text in pages:
        if text.strip():
            return page_num, _short_quote(text)
    return None, ""


def _make_evidence(quote: str, page: int | None, citation_key: str | None, level: str) -> Evidence:
    return Evidence(quote=quote, page=page, citation_key=citation_key, evidence_level=level)


def extract_story_line(pages: List[Tuple[int, str]]) -> StoryLine:
    page_num, quote = _page_evidence(pages)
    evidence = _make_evidence(quote or "", page_num, None, "low" if not quote else "medium")
    summary = EvidenceItem(
        text="This paper addresses a research gap, outlines a method, and discusses implications based on reported findings.",
        type="inference",
        evidence=evidence,
        notes="Mock summary generated from available text.",
    )
    bullets = []
    stages = [
        "Motivation: why the topic matters.",
        "Gap: what is missing in prior work.",
        "Method: how the study approaches the problem.",
        "Results: key outcomes reported.",
        "Implications: why the findings are meaningful.",
    ]
    for stage in stages:
        bullets.append(
            EvidenceItem(
                text=stage,
                type="inference",
                evidence=evidence,
                notes="Placeholder bullet; regenerate with LLM for stronger grounding.",
            )
        )
    return StoryLine(one_paragraph_summary=summary, bullets=bullets)


def extract_intro_evidence(pages: List[Tuple[int, str]]) -> List[IntroEvidenceRow]:
    page_num, quote = _page_evidence(pages)
    rows = []
    for idx in range(1, 9):
        rows.append(
            IntroEvidenceRow(
                claim_id=f"C{idx:02d}",
                topic="background",
                claim_text=f"Claim placeholder {idx} based on introduction context.",
                claim_type="viewpoint",
                value=None,
                unit=None,
                context="Motivation for the study.",
                evidence_quote=quote,
                page=page_num,
                citation_key=None,
                reference_entry=None,
                evidence_level="low" if not quote else "medium",
                notes="Placeholder; update with extracted claims when available.",
            )
        )
    return rows


def extract_contributions(pages: List[Tuple[int, str]]) -> Contributions:
    page_num, quote = _page_evidence(pages)
    evidence = _make_evidence(quote, page_num, None, "low" if not quote else "medium")
    def _items(prefix: str, count: int) -> List[EvidenceItem]:
        return [
            EvidenceItem(
                text=f"{prefix} placeholder {i + 1}.",
                type="inference",
                evidence=evidence,
                notes="Mock output; replace with grounded extraction.",
            )
            for i in range(count)
        ]

    return Contributions(
        innovations=_items("Innovation", 3),
        key_findings=_items("Finding", 3),
        implications=_items("Implication", 2),
    )


def extract_methods_limits(pages: List[Tuple[int, str]]) -> MethodsAndLimits:
    page_num, quote = _page_evidence(pages)
    evidence = _make_evidence(quote, page_num, None, "low" if not quote else "medium")
    def _items(prefix: str, count: int) -> List[EvidenceItem]:
        return [
            EvidenceItem(
                text=f"{prefix} placeholder {i + 1}.",
                type="inference",
                evidence=evidence,
                notes="Mock output; replace with grounded extraction.",
            )
            for i in range(count)
        ]

    return MethodsAndLimits(
        method_summary=_items("Method", 5),
        process_steps=_items("Process step", 5),
        assumptions=_items("Assumption", 3),
        limitations=_items("Limitation", 3),
    )


def _find_glossary_candidates(pages: List[Tuple[int, str]]) -> List[Tuple[str, int, str]]:
    candidates: List[Tuple[str, int, str]] = []
    pattern = re.compile(r"\b[A-Z]{2,}\b")
    for page_num, text in pages:
        for match in pattern.finditer(text):
            term = match.group(0)
            if term not in {"THE", "AND", "FOR"}:
                quote = _short_quote(text[max(0, match.start() - 40): match.end() + 40])
                candidates.append((term, page_num, quote))
        if len(candidates) > 60:
            break
    return candidates


def extract_glossary(pages: List[Tuple[int, str]]) -> List[GlossaryTerm]:
    terms = []
    candidates = _find_glossary_candidates(pages)
    if not candidates:
        page_num, quote = _page_evidence(pages)
        candidates = [("TERM", page_num or 1, quote)]
    for term, page_num, quote in candidates[:20]:
        terms.append(
            GlossaryTerm(
                term=term,
                term_type="abbreviation",
                expansion=None,
                zh="",
                definition="Placeholder definition derived from paper usage.",
                paper_usage_quote=quote,
                page=page_num,
                citation_key=None,
                evidence_level="low" if not quote else "medium",
                notes="Mock glossary term; update with extracted definitions.",
            )
        )
    return terms


def _candidate_vocab(text: str) -> List[str]:
    words = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", text)
    seen = []
    for word in words:
        w = word.lower()
        if w not in seen:
            seen.append(w)
    return seen


def extract_vocabulary(pages: List[Tuple[int, str]]) -> List[AdvancedVocabularyItem]:
    items: List[AdvancedVocabularyItem] = []
    for page_num, text in pages:
        candidates = _candidate_vocab(text)
        for word in candidates:
            if word.isupper():
                continue
            if zipf_frequency(word, "en") > 3.5:
                continue
            quote = _short_quote(text)
            items.append(
                AdvancedVocabularyItem(
                    word_or_phrase=word,
                    pos=None,
                    zh="",
                    simple_explanation="Placeholder explanation for an advanced academic term.",
                    example_quote=quote,
                    page=page_num,
                    difficulty_signal=str(zipf_frequency(word, "en")),
                    why_it_matters="Useful for academic reading and writing.",
                    evidence_level="low" if not quote else "medium",
                    notes="Mock vocabulary item; refine with contextual meaning.",
                )
            )
            if len(items) >= 30:
                return items
    if not items:
        page_num, quote = _page_evidence(pages)
        items.append(
            AdvancedVocabularyItem(
                word_or_phrase="analysis",
                pos=None,
                zh="",
                simple_explanation="Placeholder advanced word.",
                example_quote=quote,
                page=page_num,
                difficulty_signal=None,
                why_it_matters="Common in academic writing.",
                evidence_level="low" if not quote else "medium",
                notes="Mock vocabulary item; replace with extracted term.",
            )
        )
    return items


def build_output_bundle(pages: List[Tuple[int, str]]) -> OutputBundle:
    bundle = OutputBundle(
        story_line=extract_story_line(pages),
        intro_evidence_table=extract_intro_evidence(pages),
        contributions_and_implications=extract_contributions(pages),
        method_process_limits=extract_methods_limits(pages),
        glossary_terms=extract_glossary(pages),
        advanced_vocabulary=extract_vocabulary(pages),
        metadata={"generated_by": "mock"},
    )
    return bundle
