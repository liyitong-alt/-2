# Paper Distiller Library (MVP)

Local-first tool for distilling academic papers into structured, evidence-grounded notes with a lightweight library manager.

## Features
- Streamlit UI with two pages: **Library** and **Paper Detail**.
- SQLite metadata storage and local file storage under `data/papers/<paper_id>/`.
- PDF parsing with PyMuPDF, fallback to pdfplumber.
- Output modules with evidence tracking and explicit confidence levels.
- Mock LLM mode runs without any API keys.
- Export JSON/Markdown/CSV for evidence tables and vocabularies.

## Project Structure
```
paper_distiller_library/
  app.py
  distiller/
    __init__.py
    db.py
    models.py
    storage.py
    pdf_reader.py
    sectioner.py
    reference_parser.py
    llm_provider.py
    extractors.py
    schemas.py
    renderers.py
    utils.py
  tests/
    test_schemas.py
    test_reference_parser_smoke.py
  requirements.txt
  README.md
```

## Setup
```bash
cd paper_distiller_library
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
streamlit run app.py
```

## Mock Mode (Default)
No API key is required. The system generates placeholder outputs with evidence from the PDF when available.

## Real LLM Provider (Optional)
Set environment variables to enable OpenAI:
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_key
export OPENAI_MODEL=gpt-4o-mini
```

## Evidence & Confidence Policy
- All structured outputs include evidence with quote, page, citation key, and evidence level.
- When evidence is missing, `page=null` and `evidence_level=low` with notes explaining the limitation.
- Extract/Paraphrase/Inference are explicitly labeled.

## Notes
- The MVP uses heuristic extraction and placeholder summaries. Replace with stronger extraction logic or LLM prompts as needed.
- No cloud database is used; all data stays in the local `data/` directory.
