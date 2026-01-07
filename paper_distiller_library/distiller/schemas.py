from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    quote: str
    page: Optional[int]
    citation_key: Optional[str]
    evidence_level: str


class EvidenceItem(BaseModel):
    text: str
    type: str
    evidence: Evidence
    notes: Optional[str] = None


class StoryLine(BaseModel):
    one_paragraph_summary: EvidenceItem
    bullets: List[EvidenceItem]


class IntroEvidenceRow(BaseModel):
    claim_id: str
    topic: str
    claim_text: str
    claim_type: str
    value: Optional[str]
    unit: Optional[str]
    context: str
    evidence_quote: str
    page: Optional[int]
    citation_key: Optional[str]
    reference_entry: Optional[str]
    evidence_level: str
    notes: Optional[str]


class Contributions(BaseModel):
    innovations: List[EvidenceItem]
    key_findings: List[EvidenceItem]
    implications: List[EvidenceItem]


class MethodsAndLimits(BaseModel):
    method_summary: List[EvidenceItem]
    process_steps: List[EvidenceItem]
    assumptions: List[EvidenceItem]
    limitations: List[EvidenceItem]


class GlossaryTerm(BaseModel):
    term: str
    term_type: str
    expansion: Optional[str]
    zh: Optional[str]
    definition: str
    paper_usage_quote: str
    page: Optional[int]
    citation_key: Optional[str]
    evidence_level: str
    notes: Optional[str]


class AdvancedVocabularyItem(BaseModel):
    word_or_phrase: str
    pos: Optional[str]
    zh: str
    simple_explanation: str
    example_quote: str
    page: Optional[int]
    difficulty_signal: Optional[str]
    why_it_matters: str
    evidence_level: str
    notes: Optional[str]


class OutputBundle(BaseModel):
    story_line: StoryLine
    intro_evidence_table: List[IntroEvidenceRow]
    contributions_and_implications: Contributions
    method_process_limits: MethodsAndLimits
    glossary_terms: List[GlossaryTerm]
    advanced_vocabulary: List[AdvancedVocabularyItem]
    metadata: dict = Field(default_factory=dict)
