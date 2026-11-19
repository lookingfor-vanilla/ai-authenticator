"""
HashProof AI — SQLite Database Backend.

Provides ACID-compliant persistence for examination records, parameterized queries,
search and retrieval without risk of SQL injection.
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


# Keep the database in the same folder as this file.
DB_PATH = Path(__file__).resolve().parent / "authenticator.db"


def get_connection():
    """Open a connection to the SQLite database."""
    connection = sqlite3.connect(str(DB_PATH), timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the reports table if it does not already exist."""
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    report_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    sha256 TEXT,
                    report_json TEXT NOT NULL
                )
                """
            )
    finally:
        conn.close()


def save_report_to_db(report: Dict[str, Any]) -> Dict[str, Any]:
    """Save or update one examination report permanently in SQLite."""
    if not isinstance(report, dict):
        raise TypeError("The report must be a dictionary.")

    report_to_save = dict(report)

    # Stable ID and ISO-8601 UTC timestamp
    report_id = str(
        report_to_save.get("report_id") or uuid.uuid4()
    )
    created_at = str(
        report_to_save.get("created_at")
        or datetime.now(timezone.utc).isoformat()
    )

    filename = str(
        report_to_save.get("filename")
        or report_to_save.get("file_name")
        or report_to_save.get("evidence_filename")
        or (report_to_save.get("evidence", {}).get("filename") if isinstance(report_to_save.get("evidence"), dict) else None)
        or "Unknown file"
    )

    sha256 = (
        report_to_save.get("sha256")
        or report_to_save.get("file_hash")
        or report_to_save.get("hash")
        or (report_to_save.get("evidence", {}).get("sha256") if isinstance(report_to_save.get("evidence"), dict) else None)
    )

    report_to_save["report_id"] = report_id
    report_to_save["created_at"] = created_at

    report_json = json.dumps(
        report_to_save,
        ensure_ascii=False,
        default=str
    )

    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO reports
                (report_id, created_at, filename, sha256, report_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    created_at,
                    filename,
                    str(sha256) if sha256 is not None else None,
                    report_json,
                ),
            )
    finally:
        conn.close()

    return report_to_save


def get_reports_from_db(limit: int = 100) -> List[Dict[str, Any]]:
    """Return the newest saved reports first."""
    limit = max(1, min(int(limit), 1000))
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT report_id, created_at, filename, sha256, report_json
            FROM reports
            ORDER BY created_at DESC, rowid DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        reports = []
        for row in rows:
            try:
                report = json.loads(row["report_json"])
                reports.append(report)
            except (json.JSONDecodeError, TypeError):
                continue
        return reports
    finally:
        conn.close()


def get_report_by_id(report_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve one saved report by its unique ID."""
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT report_json
            FROM reports
            WHERE report_id = ?
            """,
            (str(report_id),),
        ).fetchone()

        if row is None:
            return None

        try:
            return json.loads(row["report_json"])
        except (json.JSONDecodeError, TypeError):
            return None
    finally:
        conn.close()


def delete_report_from_db(report_id: str) -> bool:
    """Delete a report by its unique ID."""
    conn = get_connection()
    try:
        with conn:
            cursor = conn.execute(
                "DELETE FROM reports WHERE report_id = ?",
                (str(report_id),)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def search_reports_in_db(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search reports by filename, report ID, or SHA-256 digest."""
    q = f"%{query.strip()}%"
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT report_json
            FROM reports
            WHERE filename LIKE ? OR report_id LIKE ? OR sha256 LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (q, q, q, limit),
        ).fetchall()

        results = []
        for row in rows:
            try:
                results.append(json.loads(row["report_json"]))
            except Exception:
                continue
        return results
    finally:
        conn.close()


def get_report_count() -> int:
    """Count all saved examination reports."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS total FROM reports"
        ).fetchone()
        return row["total"] if row else 0
    finally:
        conn.close()
