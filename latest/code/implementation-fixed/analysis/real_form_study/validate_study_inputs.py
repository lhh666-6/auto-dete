"""Schema validation for the locked study data contracts.

Enforces the exact CSV headers, value domains, referential integrity, hash
formats, and timestamp conventions from the data dictionary. The analysis
pipeline refuses to run on data that fails validation (fail-closed).
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

CONTRACTS: dict[str, dict[str, object]] = {
    "forms.csv": {
        "columns": [
            "study_form_id", "source_batch", "template_id", "capture_condition",
            "image_sha256", "authorization_status", "redaction_status",
            "eligible", "inclusion_status", "exclusion_reason",
            "physical_form_cluster",
        ],
        "required": [
            "study_form_id", "template_id", "image_sha256", "eligible",
            "inclusion_status",
        ],
        "domains": {
            "authorization_status": {"authorized", "pending", "denied"},
            "redaction_status": {"redacted", "under_review", "failed"},
            "inclusion_status": {"included", "excluded", "pilot"},
            "eligible": {"true", "false"},
        },
        "sha256": ["image_sha256"],
    },
    "reference_fields.csv": {
        "columns": [
            "study_form_id", "field_key", "reference_value", "reference_source",
            "transcriber_passes", "ambiguity_flag", "adjudication_status",
            "reference_notes_code",
        ],
        "required": ["study_form_id", "field_key", "reference_source"],
        "domains": {
            "reference_source": {
                "source_system", "transcription_pass1", "transcription_pass2",
                "adjudicated",
            },
            "adjudication_status": {"none", "adjudicated", "unresolved"},
            "ambiguity_flag": {"true", "false"},
        },
    },
    "machine_candidates.csv": {
        "columns": [
            "study_form_id", "field_key", "candidate_id", "certificate_id",
            "machine_value", "confidence", "selection_state", "producer_id",
            "producer_version", "template_id", "template_version",
            "evidence_hash", "evidence_locator",
        ],
        "required": [
            "study_form_id", "field_key", "candidate_id", "certificate_id",
            "selection_state",
        ],
        "domains": {
            "selection_state": {"SELECTED", "ABSTAINED"},
        },
        "sha256": ["certificate_id", "evidence_hash"],
    },
    "review_decisions.csv": {
        "columns": [
            "study_form_id", "field_key", "reviewer_pseudonym", "review_session_id",
            "action", "presented_machine_value", "final_value", "decision_id",
            "certificate_id", "form_opened_at", "field_action_at", "submitted_at",
            "manual_resolution",
        ],
        "required": ["study_form_id", "field_key", "reviewer_pseudonym", "action"],
        "domains": {
            "reviewer_pseudonym": {"R0", "R1", "R2"},
            "action": {
                "retain_machine", "correct_machine", "manual_entry",
                "abstain_reacquire",
            },
            "manual_resolution": {"true", "false"},
        },
        "timestamps": ["form_opened_at", "field_action_at", "submitted_at"],
    },
    "study_flow.csv": {
        "columns": [
            "study_form_id", "import_status", "classify_status",
            "recognition_status", "review_status", "trace_status",
            "reference_status", "endpoint_inclusion_reason",
        ],
        "required": ["study_form_id", "import_status"],
        "domains": {
            "import_status": {"ok", "failed", "not_attempted"},
            "classify_status": {"ok", "failed", "manual_route", "not_attempted"},
            "recognition_status": {"candidates", "abstained", "missing"},
            "review_status": {"confirmed", "corrected", "unreviewed"},
            "trace_status": {"complete", "incomplete", "pre-certificate"},
            "reference_status": {"available", "ambiguous", "unavailable"},
        },
    },
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_study_inputs(data_dir: Path) -> list[str]:
    """Validate all contract files under data_dir; return error messages.

    An empty list means every contract passed. The pipeline is fail-closed:
    any error blocks dataset construction and analysis.
    """
    errors: list[str] = []
    tables: dict[str, list[dict[str, str]]] = {}
    for filename, contract in CONTRACTS.items():
        path = data_dir / filename
        if not path.exists():
            errors.append(f"{filename}: missing")
            continue
        rows = _read_csv(path)
        tables[filename] = rows
        columns = contract["columns"]
        assert isinstance(columns, list)
        if not rows:
            errors.append(f"{filename}: empty (no header row)")
            continue
        headers = list(rows[0].keys())
        missing_columns = [column for column in columns if column not in headers]
        extra_columns = [header for header in headers if header not in columns]
        if missing_columns:
            errors.append(f"{filename}: missing columns {missing_columns}")
        if extra_columns:
            errors.append(f"{filename}: unexpected columns {extra_columns}")
        for index, row in enumerate(rows, start=2):
            for column in contract.get("required", []):
                assert isinstance(column, str)
                if not row.get(column, "").strip():
                    errors.append(f"{filename}:{index}: {column} is required")
            domains = contract.get("domains", {})
            assert isinstance(domains, dict)
            for column, allowed in domains.items():
                value = row.get(column, "")
                if value and value not in allowed:
                    errors.append(
                        f"{filename}:{index}: {column}={value!r} "
                        f"not in {sorted(allowed)}"
                    )
            for column in contract.get("sha256", []):
                assert isinstance(column, str)
                value = row.get(column, "")
                if value and not SHA256_RE.match(value):
                    errors.append(
                        f"{filename}:{index}: {column} is not a sha256 hex string"
                    )
            for column in contract.get("timestamps", []):
                assert isinstance(column, str)
                value = row.get(column, "")
                if value:
                    _check_timestamp(value, filename, index, column, errors)
    _check_referential_integrity(tables, errors)
    return errors


def _check_timestamp(
    value: str,
    filename: str,
    index: int,
    column: str,
    errors: list[str],
) -> None:
    if not TIMESTAMP_RE.match(value):
        errors.append(f"{filename}:{index}: {column} is not ISO8601 UTC")
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{filename}:{index}: {column} is not a valid timestamp")
        return
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{filename}:{index}: {column} must be timezone-aware")


def _check_referential_integrity(
    tables: dict[str, list[dict[str, str]]], errors: list[str]
) -> None:
    forms = tables.get("forms.csv", [])
    form_ids = {
        row.get("study_form_id", "")
        for row in forms
        if row.get("study_form_id")
    }
    for filename in (
        "reference_fields.csv",
        "machine_candidates.csv",
        "review_decisions.csv",
        "study_flow.csv",
    ):
        for index, row in enumerate(tables.get(filename, []), start=2):
            form_id = row.get("study_form_id", "")
            if form_id and form_id not in form_ids:
                errors.append(f"{filename}:{index}: unknown study_form_id {form_id!r}")
    # every reviewed field must be a known target field (reference or machine)
    reference_keys = {
        (row.get("study_form_id", ""), row.get("field_key", ""))
        for row in tables.get("reference_fields.csv", [])
        if row.get("study_form_id")
    }
    machine_keys = {
        (row.get("study_form_id", ""), row.get("field_key", ""))
        for row in tables.get("machine_candidates.csv", [])
        if row.get("study_form_id")
    }
    for index, row in enumerate(tables.get("review_decisions.csv", []), start=2):
        key = (row.get("study_form_id", ""), row.get("field_key", ""))
        if key[0] and key not in reference_keys and key not in machine_keys:
            errors.append(f"review_decisions.csv:{index}: field {key} is not a target field")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate study data contracts")
    parser.add_argument("--data-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    errors = validate_study_inputs(args.data_dir)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("study inputs valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
