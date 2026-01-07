from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


def render_markdown(outputs: Dict[str, Any]) -> str:
    lines: List[str] = []
    story = outputs.get("story_line", {})
    if story:
        lines.append("# Story Line")
        summary = story.get("one_paragraph_summary", {}).get("text", "")
        lines.append(summary)
        lines.append("")
        lines.append("## Bullets")
        for bullet in story.get("bullets", []):
            lines.append(f"- {bullet.get('text', '')}")
        lines.append("")
    lines.append("# Intro Evidence Table")
    for row in outputs.get("intro_evidence_table", []):
        lines.append(f"- {row.get('claim_id')}: {row.get('claim_text')}")
    lines.append("")
    lines.append("# Contributions & Implications")
    for key in ["innovations", "key_findings", "implications"]:
        lines.append(f"## {key.replace('_', ' ').title()}")
        for item in outputs.get("contributions_and_implications", {}).get(key, []):
            lines.append(f"- {item.get('text', '')}")
    lines.append("")
    lines.append("# Methods & Limits")
    for key in ["method_summary", "process_steps", "assumptions", "limitations"]:
        lines.append(f"## {key.replace('_', ' ').title()}")
        for item in outputs.get("method_process_limits", {}).get(key, []):
            lines.append(f"- {item.get('text', '')}")
    lines.append("")
    lines.append("# Glossary")
    for term in outputs.get("glossary_terms", []):
        lines.append(f"- {term.get('term')}: {term.get('definition')}")
    lines.append("")
    lines.append("# Advanced Vocabulary")
    for vocab in outputs.get("advanced_vocabulary", []):
        lines.append(f"- {vocab.get('word_or_phrase')}: {vocab.get('simple_explanation')}")
    return "\n".join(lines)


def export_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)


def export_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
