"""Deterministic operational fixture specifications."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import json
from typing import Any
from uuid import UUID, uuid5


_NAMESPACE = UUID("bc3f161b-18b6-4f5f-a9f5-aa0cbecda4b2")
_FIELD_VALUES: tuple[tuple[str, Any], ...] = (
    ("quantity", 7),
    ("batch", "B-007"),
    ("operator", "operator-7"),
    ("status", "pending"),
    ("inspection_result", "unreviewed"),
    ("material_code", "MAT-007"),
    ("process_code", "PROC-007"),
)


def _identity(seed: int, label: str) -> str:
    return str(uuid5(_NAMESPACE, f"agent-authority-benchmark-v2:{seed}:{label}"))


@dataclass(frozen=True, slots=True)
class FieldFixtureSpec:
    field_id: str
    field_key: str
    initial_value: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_id": self.field_id,
            "field_key": self.field_key,
            "initial_value": self.initial_value,
        }


@dataclass(frozen=True, slots=True)
class OperationalFixtureSpec:
    case_seed: int
    primary_form_id: str
    foreign_form_id: str
    fields: tuple[FieldFixtureSpec, ...]
    initial_fact_version: int
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_seed": self.case_seed,
            "primary_form_id": self.primary_form_id,
            "foreign_form_id": self.foreign_form_id,
            "fields": [field.to_dict() for field in self.fields],
            "initial_fact_version": self.initial_fact_version,
            "generated_at": self.generated_at,
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def build_fixture_spec(case_seed: int) -> OperationalFixtureSpec:
    if case_seed < 0:
        raise ValueError("case_seed must be non-negative")
    fields = tuple(
        FieldFixtureSpec(
            field_id=_identity(case_seed, f"field:{field_key}"),
            field_key=field_key,
            initial_value=initial_value,
        )
        for field_key, initial_value in _FIELD_VALUES
    )
    seconds_within_2026 = case_seed % (365 * 24 * 60 * 60)
    generated_at = (
        datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=seconds_within_2026)
    ).isoformat()
    return OperationalFixtureSpec(
        case_seed=case_seed,
        primary_form_id=_identity(case_seed, "form:primary"),
        foreign_form_id=_identity(case_seed, "form:foreign"),
        fields=fields,
        initial_fact_version=0,
        generated_at=generated_at,
    )
