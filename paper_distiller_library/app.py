from __future__ import annotations

import uuid
from pathlib import Path

import pandas as pd
import streamlit as st

from distiller import db, extractors, pdf_reader, renderers, sectioner, storage, utils
from distiller.schemas import OutputBundle

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
PAPERS_DIR = DATA_DIR / "papers"
DB_PATH = DATA_DIR / db.DB_FILENAME


st.set_page_config(page_title="Paper Distiller Library", layout="wide")

storage_manager = storage.StorageManager(PAPERS_DIR)

db.init_db(DB_PATH)


def _load_papers() -> list[db.PaperRecord]:
    with db.get_connection(DB_PATH) as conn:
        return list(db.fetch_papers(conn))


def _save_outputs(paper_id: str, pages: list[tuple[int, str]]) -> OutputBundle:
    bundle = extractors.build_output_bundle(pages)
    storage_manager.save_json(paper_id, "outputs.json", bundle.model_dump())
    return bundle


def _prepare_page_text(pdf_path: Path) -> list[tuple[int, str]]:
    parsed = pdf_reader.read_pdf(pdf_path)
    pages = [(page.page, page.text) for page in parsed.pages]
    storage_manager.save_json(
        pdf_path.parent.name,
        "parsed_text.json",
        {
            "source": parsed.source,
            "pages": [page.__dict__ for page in parsed.pages],
        },
    )
    return pages


def _process_upload(uploaded_file) -> None:
    paper_id = str(uuid.uuid4())
    pdf_path = storage_manager.save_pdf(paper_id, uploaded_file.name, uploaded_file.getvalue())
    pages = _prepare_page_text(pdf_path)
    sections = sectioner.section_pages(pages)
    storage_manager.save_json(
        paper_id,
        "sections.json",
        {"sections": [section.__dict__ for section in sections]},
    )
    _save_outputs(paper_id, pages)

    now = utils.now_iso()
    title = utils.simplify_title(uploaded_file.name)
    record = db.PaperRecord(
        id=paper_id,
        original_filename=uploaded_file.name,
        display_title=title,
        short_title=title[:40],
        authors=None,
        year=None,
        doi=None,
        category=None,
        tags=None,
        status="unread",
        added_at=now,
        updated_at=now,
        notes=None,
    )
    with db.get_connection(DB_PATH) as conn:
        db.insert_paper(conn, record)


def library_page() -> None:
    st.header("Library")
    uploaded = st.file_uploader("Upload PDF", type=["pdf"], accept_multiple_files=False)
    if uploaded:
        _process_upload(uploaded)
        st.success("Uploaded and processed.")

    papers = _load_papers()
    if not papers:
        st.info("No papers yet. Upload a PDF to get started.")
        return

    search = st.text_input("Search")
    categories = sorted({paper.category for paper in papers if paper.category})
    statuses = sorted({paper.status for paper in papers if paper.status})
    tags_set = sorted({tag.strip() for paper in papers if paper.tags for tag in paper.tags.split(",") if tag.strip()})

    selected_categories = st.multiselect("Category", categories)
    selected_statuses = st.multiselect("Status", statuses)
    selected_tags = st.multiselect("Tags", tags_set)

    def _match(paper: db.PaperRecord) -> bool:
        if search and search.lower() not in (paper.display_title or "").lower():
            return False
        if selected_categories and paper.category not in selected_categories:
            return False
        if selected_statuses and paper.status not in selected_statuses:
            return False
        if selected_tags:
            paper_tags = {tag.strip() for tag in (paper.tags or "").split(",") if tag.strip()}
            if not paper_tags.intersection(selected_tags):
                return False
        return True

    filtered = [paper for paper in papers if _match(paper)]

    df = pd.DataFrame([
        {
            "id": paper.id,
            "display_title": paper.display_title,
            "short_title": paper.short_title,
            "year": paper.year,
            "tags": paper.tags,
            "category": paper.category,
            "status": paper.status,
        }
        for paper in filtered
    ])
    edited = st.data_editor(df, num_rows="fixed", use_container_width=True)

    if st.button("Save edits"):
        updates = edited.to_dict(orient="records")
        with db.get_connection(DB_PATH) as conn:
            for row in updates:
                paper_id = row.pop("id")
                db.update_paper_fields(conn, paper_id, row)
        st.success("Updates saved.")

    st.subheader("Delete")
    delete_id = st.selectbox("Select paper", options=[paper.id for paper in papers])
    delete_files = st.checkbox("Delete files from disk", value=False)
    if st.button("Delete paper"):
        with db.get_connection(DB_PATH) as conn:
            db.delete_paper(conn, delete_id)
        if delete_files:
            paper_dir = storage_manager.paper_dir(delete_id)
            if paper_dir.exists():
                for item in paper_dir.rglob("*"):
                    if item.is_file():
                        item.unlink()
                for item in sorted(paper_dir.rglob("*"), reverse=True):
                    if item.is_dir():
                        item.rmdir()
                paper_dir.rmdir()
        st.success("Deleted.")


def detail_page() -> None:
    st.header("Paper Detail")
    papers = _load_papers()
    if not papers:
        st.info("No papers available.")
        return

    paper_lookup = {paper.display_title: paper for paper in papers}
    selected_title = st.selectbox("Select paper", options=list(paper_lookup.keys()))
    paper = paper_lookup[selected_title]

    outputs = storage_manager.load_json(paper.id, "outputs.json")
    if not outputs:
        outputs = _save_outputs(paper.id, _prepare_page_text(storage_manager.paper_dir(paper.id) / paper.original_filename)).model_dump()

    nav = st.sidebar.radio(
        "Sections",
        [
            "Overview",
            "Intro Evidence Table",
            "Story Line",
            "Contributions",
            "Methods & Limits",
            "Glossary",
            "Vocabulary",
            "Exports",
        ],
    )

    if st.button("Regenerate outputs"):
        pdf_path = storage_manager.paper_dir(paper.id) / paper.original_filename
        pages = _prepare_page_text(pdf_path)
        outputs = _save_outputs(paper.id, pages).model_dump()
        st.success("Outputs regenerated.")

    if nav == "Overview":
        st.subheader(paper.display_title)
        st.write(outputs.get("metadata", {}))
    elif nav == "Intro Evidence Table":
        st.dataframe(pd.DataFrame(outputs.get("intro_evidence_table", [])), use_container_width=True)
    elif nav == "Story Line":
        st.json(outputs.get("story_line", {}))
    elif nav == "Contributions":
        st.json(outputs.get("contributions_and_implications", {}))
    elif nav == "Methods & Limits":
        st.json(outputs.get("method_process_limits", {}))
    elif nav == "Glossary":
        st.dataframe(pd.DataFrame(outputs.get("glossary_terms", [])), use_container_width=True)
    elif nav == "Vocabulary":
        st.dataframe(pd.DataFrame(outputs.get("advanced_vocabulary", [])), use_container_width=True)
    elif nav == "Exports":
        st.subheader("Exports")
        markdown = renderers.render_markdown(outputs)
        st.download_button("Download JSON", data=OutputBundle.model_validate(outputs).model_dump_json(indent=2), file_name="outputs.json")
        st.download_button("Download Markdown", data=markdown, file_name="outputs.md")

        intro_path = storage_manager.export_path(paper.id, "intro_evidence_table.csv")
        glossary_path = storage_manager.export_path(paper.id, "glossary_terms.csv")
        vocab_path = storage_manager.export_path(paper.id, "advanced_vocabulary.csv")

        renderers.export_csv(intro_path, outputs.get("intro_evidence_table", []))
        renderers.export_csv(glossary_path, outputs.get("glossary_terms", []))
        renderers.export_csv(vocab_path, outputs.get("advanced_vocabulary", []))

        st.download_button("Download Intro Evidence CSV", data=intro_path.read_bytes(), file_name=intro_path.name)
        st.download_button("Download Glossary CSV", data=glossary_path.read_bytes(), file_name=glossary_path.name)
        st.download_button("Download Vocabulary CSV", data=vocab_path.read_bytes(), file_name=vocab_path.name)


def main() -> None:
    page = st.sidebar.radio("Navigate", ["Library", "Paper Detail"])
    if page == "Library":
        library_page()
    else:
        detail_page()


if __name__ == "__main__":
    main()
