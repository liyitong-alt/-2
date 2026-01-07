from distiller.schemas import OutputBundle


def test_output_bundle_schema_roundtrip():
    payload = {
        "story_line": {
            "one_paragraph_summary": {
                "text": "summary",
                "type": "inference",
                "evidence": {
                    "quote": "quote",
                    "page": None,
                    "citation_key": None,
                    "evidence_level": "low",
                },
                "notes": None,
            },
            "bullets": [
                {
                    "text": "bullet",
                    "type": "inference",
                    "evidence": {
                        "quote": "quote",
                        "page": 1,
                        "citation_key": None,
                        "evidence_level": "medium",
                    },
                    "notes": None,
                }
            ],
        },
        "intro_evidence_table": [],
        "contributions_and_implications": {
            "innovations": [],
            "key_findings": [],
            "implications": [],
        },
        "method_process_limits": {
            "method_summary": [],
            "process_steps": [],
            "assumptions": [],
            "limitations": [],
        },
        "glossary_terms": [],
        "advanced_vocabulary": [],
        "metadata": {"generated_by": "test"},
    }
    bundle = OutputBundle.model_validate(payload)
    assert bundle.metadata["generated_by"] == "test"
