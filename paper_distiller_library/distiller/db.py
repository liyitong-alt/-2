import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

DB_FILENAME = "library.db"


@dataclass
class PaperRecord:
    id: str
    original_filename: str
    display_title: str
    short_title: str
    authors: Optional[str]
    year: Optional[int]
    doi: Optional[str]
    category: Optional[str]
    tags: Optional[str]
    status: Optional[str]
    added_at: str
    updated_at: str
    notes: Optional[str]


def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                display_title TEXT NOT NULL,
                short_title TEXT NOT NULL,
                authors TEXT,
                year INTEGER,
                doi TEXT,
                category TEXT,
                tags TEXT,
                status TEXT,
                added_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                notes TEXT
            )
            """
        )


def insert_paper(conn: sqlite3.Connection, record: PaperRecord) -> None:
    conn.execute(
        """
        INSERT INTO papers (
            id, original_filename, display_title, short_title, authors, year, doi,
            category, tags, status, added_at, updated_at, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.id,
            record.original_filename,
            record.display_title,
            record.short_title,
            record.authors,
            record.year,
            record.doi,
            record.category,
            record.tags,
            record.status,
            record.added_at,
            record.updated_at,
            record.notes,
        ),
    )
    conn.commit()


def update_paper_fields(conn: sqlite3.Connection, paper_id: str, fields: dict) -> None:
    if not fields:
        return
    fields["updated_at"] = datetime.utcnow().isoformat()
    assignments = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [paper_id]
    conn.execute(
        f"UPDATE papers SET {assignments} WHERE id = ?",
        values,
    )
    conn.commit()


def delete_paper(conn: sqlite3.Connection, paper_id: str) -> None:
    conn.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
    conn.commit()


def fetch_papers(conn: sqlite3.Connection) -> Iterable[PaperRecord]:
    rows = conn.execute("SELECT * FROM papers ORDER BY added_at DESC").fetchall()
    for row in rows:
        yield PaperRecord(**dict(row))


def fetch_paper(conn: sqlite3.Connection, paper_id: str) -> Optional[PaperRecord]:
    row = conn.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
    return PaperRecord(**dict(row)) if row else None
