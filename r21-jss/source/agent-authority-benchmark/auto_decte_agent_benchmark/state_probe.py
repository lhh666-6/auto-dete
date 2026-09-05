"""Read-only logical SQLite snapshot for candidate/authority digesting."""

from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Any

from .digests import AUTHORITY_TABLES, CANDIDATE_TABLES


def _json_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"encoding": "hex", "value": value.hex()}
    return value


def snapshot_sqlite(database: Path) -> dict[str, Any]:
    if not database.is_file():
        raise FileNotFoundError(database)
    uri = f"{database.resolve().as_uri()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        existing = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        tables: dict[str, list[dict[str, Any]]] = {}
        for table in sorted(CANDIDATE_TABLES | AUTHORITY_TABLES):
            if table not in existing:
                tables[table] = []
                continue
            columns = [
                str(row[1])
                for row in connection.execute(f'PRAGMA table_info("{table}")').fetchall()
            ]
            rows = connection.execute(f'SELECT * FROM "{table}"').fetchall()
            tables[table] = [
                {column: _json_value(value) for column, value in zip(columns, row, strict=True)}
                for row in rows
            ]
    return {"user_version": user_version, "tables": tables}
