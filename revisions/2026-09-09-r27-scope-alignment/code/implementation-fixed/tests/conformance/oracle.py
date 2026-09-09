"""Independent raw-relational oracle for the finite R9 conformance catalogue.

This module deliberately does not import application validators, trace builders,
admission planning, or evidence-identity helpers.  It reads raw SQL rows and
expresses the expected relations independently.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from datetime import date, datetime
from typing import Any
from urllib.parse import quote, unquote

from sqlalchemy import Engine, text

_JSON_COLUMNS = {
    "after_state",
    "before_state",
    "bbox",
    "evidence_ids",
    "fact_sources",
    "filters",
    "included_records",
    "lineage_parent_ids",
    "payload",
    "values",
}


def _normalize(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bytes):
        return {"__bytes__": value.hex()}
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    return value


def canonical_database_state(engine: Engine) -> dict[str, object]:
    """Read every application table and identity sequence in stable order."""

    with engine.connect() as connection:
        user_version = int(connection.execute(text("PRAGMA user_version")).scalar_one())
        table_names = [
            row[0]
            for row in connection.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%' ORDER BY name"
                )
            )
        ]
        tables: dict[str, list[dict[str, object]]] = {}
        for table_name in table_names:
            columns = [
                row[1] for row in connection.execute(text(f'PRAGMA table_info("{table_name}")'))
            ]
            rows: list[dict[str, object]] = []
            for raw in connection.execute(text(f'SELECT * FROM "{table_name}"')):
                row: dict[str, object] = {}
                for column, value in zip(columns, raw, strict=True):
                    if column in _JSON_COLUMNS and isinstance(value, str):
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            pass
                    row[column] = _normalize(value)
                rows.append(row)
            rows.sort(key=_canonical_json)
            tables[table_name] = rows

        has_sequence = connection.execute(
            text("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'")
        ).scalar_one()
        identity_sequences: list[dict[str, object]] = []
        if has_sequence:
            identity_sequences = [
                {"name": row[0], "seq": row[1]}
                for row in connection.execute(
                    text("SELECT name, seq FROM sqlite_sequence ORDER BY name")
                )
            ]
    return {
        "user_version": user_version,
        "identity_sequences": identity_sequences,
        "tables": tables,
    }


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _integer(value: object) -> int:
    return int(str(value))


def state_digest(state: dict[str, object]) -> str:
    return hashlib.sha256(_canonical_json(state).encode("utf-8")).hexdigest()


def database_digest(engine: Engine) -> str:
    return state_digest(canonical_database_state(engine))


def _storage_uri(uri: str) -> str:
    normalized = unicodedata.normalize("NFC", uri).replace("\\", "/")
    segments = [
        quote(unicodedata.normalize("NFC", unquote(segment)), safe="-._~")
        for segment in normalized.split("/")
    ]
    return "/".join(segments)


def _evidence_locator(evidence: dict[str, object]) -> str:
    return _canonical_json(
        {
            "form_id": unicodedata.normalize("NFC", str(evidence["form_id"])),
            "related_field_id": (
                unicodedata.normalize("NFC", str(evidence["related_field_id"]))
                if evidence.get("related_field_id") is not None
                else None
            ),
            "uri": _storage_uri(str(evidence["uri"])),
            "v": 1,
        }
    )


def _table(state: dict[str, object], name: str) -> list[dict[str, object]]:
    tables = state.get("tables")
    if not isinstance(tables, dict):
        return []
    rows = tables.get(name, [])
    return rows if isinstance(rows, list) else []


def relational_authority_violations(state: dict[str, object], form_id: str) -> tuple[str, ...]:
    """Check P0/P1/P2/P3/P5/P6 relations from raw rows only."""

    failures: list[str] = []

    def fail(message: str) -> None:
        if message not in failures:
            failures.append(message)

    declared = {
        str(row["field_name"])
        for row in _table(state, "form_fields")
        if row.get("form_id") == form_id
    }
    records = sorted(
        (row for row in _table(state, "record_versions") if row.get("form_id") == form_id),
        key=lambda row: _integer(row["version"]),
    )
    transitions = [
        row for row in _table(state, "fact_transitions") if row.get("form_id") == form_id
    ]
    transition_by_id = {str(row["transition_id"]): row for row in transitions}
    decisions = {
        str(row["decision_id"]): row
        for row in _table(state, "human_decisions")
        if row.get("form_id") == form_id
    }
    bindings = {str(row["decision_id"]): row for row in _table(state, "authorization_bindings")}
    certificates = {
        str(row["certificate_id"]): row for row in _table(state, "candidate_certificates")
    }
    evidence = {str(row["file_id"]): row for row in _table(state, "evidence_files")}
    records_by_version = {_integer(row["version"]): row for row in records}

    previous: dict[str, object] | None = None
    for record in records:
        version = _integer(record["version"])
        values = record.get("values")
        sources = record.get("fact_sources")
        if not isinstance(values, dict) or set(values) != declared:
            fail(f"snapshot-domain:v{version}")
            values = values if isinstance(values, dict) else {}
        if not isinstance(sources, dict) or set(sources) != declared:
            fail(f"source-domain:v{version}")
            sources = sources if isinstance(sources, dict) else {}

        if previous is None:
            changed = set(declared)
        else:
            previous_values = previous.get("values")
            previous_sources = previous.get("fact_sources")
            previous_values = previous_values if isinstance(previous_values, dict) else {}
            previous_sources = previous_sources if isinstance(previous_sources, dict) else {}
            changed = {
                field
                for field in declared
                if _canonical_json(values.get(field)) != _canonical_json(previous_values.get(field))
            }
            for field in declared - changed:
                if sources.get(field) != previous_sources.get(field):
                    fail(f"copy-forward:v{version}:{field}")
            for field in changed:
                if sources.get(field) == previous_sources.get(field):
                    fail(f"changed-source-reused:v{version}:{field}")

        created = [row for row in transitions if _integer(row["created_version"]) == version]
        created_fields = [str(row["field_key"]) for row in created]
        if len(created_fields) != len(set(created_fields)):
            fail(f"duplicate-transition-field:v{version}")
        if set(created_fields) != changed:
            fail(f"transition-set:v{version}")

        for field in declared & set(sources):
            transition = transition_by_id.get(str(sources[field]))
            if transition is None:
                fail(f"missing-source:v{version}:{field}")
                continue
            source_version = _integer(transition["created_version"])
            source_record = records_by_version.get(source_version)
            if transition.get("record_id") != form_id:
                fail(f"source-record:v{version}:{field}")
            if transition.get("field_key") != field:
                fail(f"source-field:v{version}:{field}")
            if source_version > version:
                fail(f"future-source:v{version}:{field}")
            if field in changed and source_version != version:
                fail(f"changed-source-version:v{version}:{field}")
            if source_record is None or transition.get("record_version_id") != source_record.get(
                "record_id"
            ):
                fail(f"record-version-anchor:v{version}:{field}")
            if transition.get("value_payload") != _canonical_json(values.get(field)):
                fail(f"transition-value:v{version}:{field}")

            decision = decisions.get(str(transition.get("decision_id")))
            binding = bindings.get(str(transition.get("decision_id")))
            certificate = certificates.get(str(transition.get("certificate_id")))
            if decision is None or binding is None or certificate is None:
                fail(f"authority-chain:v{version}:{field}")
                continue
            if decision.get("field_key") != field:
                fail(f"decision-field:v{version}:{field}")
            if source_record is not None and decision.get("reviewer_id") != source_record.get(
                "confirmed_by"
            ):
                fail(f"principal:v{version}:{field}")
            if decision.get("candidate_id") != certificate.get("candidate_id"):
                fail(f"decision-candidate:v{version}:{field}")
            if binding.get("certificate_id") != transition.get("certificate_id"):
                fail(f"authorization-certificate:v{version}:{field}")
            if binding.get("authorized_value_payload") != transition.get("value_payload"):
                fail(f"authorization-value:v{version}:{field}")
            if (
                certificate.get("form_id") != form_id
                or certificate.get("target_record_id") != form_id
            ):
                fail(f"certificate-record:v{version}:{field}")
            if certificate.get("field_key") != field:
                fail(f"certificate-field:v{version}:{field}")
            if _integer(certificate.get("expected_fact_version", -1)) != source_version - 1:
                fail(f"certificate-version:v{version}:{field}")

            evidence_row = evidence.get(str(certificate.get("evidence_file_id")))
            if evidence_row is None:
                fail(f"evidence-missing:v{version}:{field}")
                continue
            locator = _evidence_locator(evidence_row)
            if evidence_row.get("form_id") != form_id:
                fail(f"evidence-owner:v{version}:{field}")
            if evidence_row.get("sha256") != certificate.get("evidence_hash"):
                fail(f"evidence-content:v{version}:{field}")
            if certificate.get("evidence_locator") != locator:
                fail(f"certificate-locator:v{version}:{field}")
            if transition.get("evidence_locator") != locator:
                fail(f"transition-locator:v{version}:{field}")
            if transition.get("evidence_hash") != evidence_row.get("sha256"):
                fail(f"transition-evidence-content:v{version}:{field}")
        previous = record

    return tuple(failures)
