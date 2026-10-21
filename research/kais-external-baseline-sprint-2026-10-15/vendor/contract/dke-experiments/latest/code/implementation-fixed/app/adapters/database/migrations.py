"""Canonical idempotent SQLite migration chain for the certificate era."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Engine, text

SCHEMA_VERSION = 5

_V5_UNIQUE_INDEXES = {
    "uq_fact_transitions_decision_id": (
        "fact_transitions",
        "decision_id",
    ),
    "uq_fact_transitions_certificate_id": (
        "fact_transitions",
        "certificate_id",
    ),
    "uq_authorization_bindings_decision_id": (
        "authorization_bindings",
        "decision_id",
    ),
    "uq_authorization_bindings_certificate_id": (
        "authorization_bindings",
        "certificate_id",
    ),
}


def schema_version(engine: Engine) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text("PRAGMA user_version")).scalar_one())


def _column_exists(connection: Any, table: str, column: str) -> bool:
    return any(
        row[1] == column for row in connection.execute(text(f'PRAGMA table_info("{table}")'))
    )


def _ensure_meta_marker(connection: Any, key: str, value: str) -> None:
    connection.execute(
        text("INSERT OR IGNORE INTO authority_meta (key, value) VALUES (:key, :value)"),
        {"key": key, "value": value},
    )


def migrate_schema(engine: Engine) -> None:
    """Advance a created schema to v5, stamping only after every step passes."""

    version = schema_version(engine)
    if version > SCHEMA_VERSION:
        raise RuntimeError(
            f"database schema version {version} exceeds supported version {SCHEMA_VERSION}"
        )
    with engine.begin() as connection:
        now = datetime.now(UTC).isoformat()
        earliest = connection.execute(
            text("SELECT MIN(created_at) FROM fact_transitions")
        ).scalar_one_or_none()
        _ensure_meta_marker(
            connection,
            "certificate_era_started_at",
            str(earliest) if earliest is not None else now,
        )

        if not _column_exists(connection, "record_versions", "fact_sources"):
            connection.execute(text("ALTER TABLE record_versions ADD COLUMN fact_sources JSON"))
        if not _column_exists(connection, "fact_transitions", "value_payload"):
            connection.execute(text("ALTER TABLE fact_transitions ADD COLUMN value_payload TEXT"))

        for index_name, (table, column) in _V5_UNIQUE_INDEXES.items():
            connection.execute(
                text(f'CREATE UNIQUE INDEX IF NOT EXISTS "{index_name}" ON "{table}" ("{column}")')
            )
        _ensure_meta_marker(
            connection,
            "canonical_evidence_locator_v1_started_at",
            now,
        )
        connection.execute(text(f"PRAGMA user_version={SCHEMA_VERSION}"))


def schema_fingerprint(engine: Engine) -> str:
    """Hash declared tables, columns, FKs, and named indexes deterministically."""

    with engine.connect() as connection:
        tables = [
            row[0]
            for row in connection.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%' ORDER BY name"
                )
            )
        ]
        payload: dict[str, object] = {"schema_version": SCHEMA_VERSION, "tables": {}}
        table_payload: dict[str, object] = {}
        for table in tables:
            columns = [
                tuple(row) for row in connection.execute(text(f'PRAGMA table_info("{table}")'))
            ]
            foreign_keys = sorted(
                tuple(row)
                for row in connection.execute(text(f'PRAGMA foreign_key_list("{table}")'))
            )
            indexes: list[tuple[object, ...]] = []
            for row in connection.execute(text(f'PRAGMA index_list("{table}")')):
                index_name = row[1]
                if index_name.startswith("sqlite_autoindex"):
                    continue
                index_columns = tuple(
                    item[2]
                    for item in connection.execute(text(f'PRAGMA index_info("{index_name}")'))
                )
                indexes.append((index_name, bool(row[2]), index_columns))
            table_payload[table] = {
                "columns": columns,
                "foreign_keys": foreign_keys,
                "indexes": sorted(indexes),
            }
        payload["tables"] = table_payload
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()
