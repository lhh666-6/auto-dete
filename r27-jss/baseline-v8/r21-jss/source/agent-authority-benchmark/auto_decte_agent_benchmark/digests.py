"""Logical candidate and authoritative-state projections."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping


CANDIDATE_TABLES = frozenset(
    {
        "recognition_attempts",
        "evidence_files",
        "audit_events",
        "ai_reviews",
        "candidate_certificates",
    }
)

AUTHORITY_TABLES = frozenset(
    {
        "forms",
        "form_fields",
        "record_versions",
        "human_decisions",
        "fact_transitions",
        "authorization_bindings",
        "authority_meta",
    }
)


@dataclass(frozen=True, slots=True)
class StateDigests:
    candidate: str
    authority: str


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _projection(state: Mapping[str, object], table_names: frozenset[str]) -> dict[str, Any]:
    raw_tables = state.get("tables", {})
    tables = raw_tables if isinstance(raw_tables, Mapping) else {}
    projected: dict[str, list[object]] = {}
    for name in sorted(table_names):
        raw_rows = tables.get(name, [])
        rows = list(raw_rows) if isinstance(raw_rows, list) else []
        projected[name] = sorted(rows, key=_canonical_json)
    return {"user_version": state.get("user_version"), "tables": projected}


def _digest(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def digest_state(state: Mapping[str, object]) -> StateDigests:
    return StateDigests(
        candidate=_digest(_projection(state, CANDIDATE_TABLES)),
        authority=_digest(_projection(state, AUTHORITY_TABLES)),
    )
