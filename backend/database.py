"""
database.py — SQLite storage for comparison history.

Stores every comparison run so the frontend can display past results.
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

_DB_PATH = Path(__file__).parent / "plagiarism.db"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


@contextmanager
def _db():
    conn = _get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they don't already exist."""
    with _db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS comparisons (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       TEXT    NOT NULL,
                code1_preview   TEXT    NOT NULL DEFAULT '',
                code2_preview   TEXT    NOT NULL DEFAULT '',
                similarity_score REAL   NOT NULL,
                plagiarism      INTEGER NOT NULL,
                details_json    TEXT    NOT NULL DEFAULT '{}'
            )
        """)


def save_comparison(
    code1: str,
    code2: str,
    similarity_score: float,
    plagiarism: bool,
    details: dict,
) -> int:
    """
    Persist a comparison result.

    Returns the row id.
    """
    preview_len = 120
    c1_preview = code1[:preview_len].replace('\n', ' ').strip()
    c2_preview = code2[:preview_len].replace('\n', ' ').strip()
    ts = datetime.now(timezone.utc).isoformat()

    with _db() as conn:
        cur = conn.execute(
            """
            INSERT INTO comparisons
                (timestamp, code1_preview, code2_preview,
                 similarity_score, plagiarism, details_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (ts, c1_preview, c2_preview, similarity_score, int(plagiarism),
             json.dumps(details)),
        )
        return cur.lastrowid  # type: ignore[return-value]


def get_history(limit: int = 50, offset: int = 0) -> list[dict]:
    """Return recent comparison records, newest first."""
    with _db() as conn:
        rows = conn.execute(
            """
            SELECT id, timestamp, code1_preview, code2_preview,
                   similarity_score, plagiarism
            FROM comparisons
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "timestamp": r["timestamp"],
            "code1_preview": r["code1_preview"],
            "code2_preview": r["code2_preview"],
            "similarity_score": r["similarity_score"],
            "plagiarism": bool(r["plagiarism"]),
        }
        for r in rows
    ]


def count_history() -> int:
    with _db() as conn:
        row = conn.execute("SELECT COUNT(*) AS cnt FROM comparisons").fetchone()
        return row["cnt"]


def clear_history() -> None:
    """Delete all comparison records."""
    with _db() as conn:
        conn.execute("DELETE FROM comparisons")
