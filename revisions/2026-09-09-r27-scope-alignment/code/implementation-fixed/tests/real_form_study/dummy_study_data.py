"""Deterministic dummy study data generator (synthetic, NOT real data).

Produces a small, hand-computable fixture so the pipeline can be tested
end to end before any real forms exist. Every value here is synthetic;
nothing in this module is or can become study evidence.
"""

from __future__ import annotations

import csv
from datetime import UTC, datetime
from pathlib import Path

SHA = "ab" * 32


def _hash(index: int) -> str:
    return f"{index:02x}" * 32


def _timestamp(minute: int, second: int = 0) -> str:
    return datetime(2026, 8, 17, 12, minute, second, tzinfo=UTC).isoformat()


def write_dummy_study_data(data_dir: Path) -> None:
    """Write the five locked CSV contracts with 6 forms and 12 fields."""
    data_dir.mkdir(parents=True, exist_ok=True)

    forms = [
        # form, template, condition, batch, eligible, inclusion, sha
        ("F-001", "T1", "A", "B1", "true", "included", _hash(1)),
        ("F-002", "T1", "B", "B1", "true", "included", _hash(2)),
        ("F-003", "T1", "A", "B1", "true", "included", _hash(3)),
        ("F-004", "T2", "B", "B2", "true", "included", _hash(4)),
        ("F-005", "T1", "A", "B2", "true", "included", _hash(5)),
        ("F-006", "T1", "A", "B2", "true", "pilot", _hash(6)),
    ]
    with (data_dir / "forms.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "study_form_id",
                "source_batch",
                "template_id",
                "capture_condition",
                "image_sha256",
                "authorization_status",
                "redaction_status",
                "eligible",
                "inclusion_status",
                "exclusion_reason",
                "physical_form_cluster",
            ]
        )
        for form_id, template, condition, batch, eligible, inclusion, sha in forms:
            writer.writerow(
                [
                    form_id,
                    batch,
                    template,
                    condition,
                    sha,
                    "authorized",
                    "redacted",
                    eligible,
                    inclusion,
                    "",
                    form_id,
                ]
            )

    # reference: (form, field) -> reference value
    references = {
        ("F-001", "total_quantity"): "10",
        ("F-001", "qualified_quantity"): "9",
        ("F-002", "total_quantity"): "20",
        ("F-002", "qualified_quantity"): "18",
        ("F-003", "total_quantity"): "30",
        ("F-003", "qualified_quantity"): "27",
        ("F-004", "total_quantity"): "40",
        ("F-004", "qualified_quantity"): "36",
        ("F-005", "total_quantity"): "50",
        ("F-005", "qualified_quantity"): "45",
        ("F-006", "total_quantity"): "60",
        ("F-006", "qualified_quantity"): "54",
    }
    ambiguous = {("F-005", "total_quantity")}
    with (data_dir / "reference_fields.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "study_form_id",
                "field_key",
                "reference_value",
                "reference_source",
                "transcriber_passes",
                "ambiguity_flag",
                "adjudication_status",
                "reference_notes_code",
            ]
        )
        for (form_id, field_key), value in sorted(references.items()):
            writer.writerow(
                [
                    form_id,
                    field_key,
                    value,
                    "transcription_pass1",
                    "1",
                    "true" if (form_id, field_key) in ambiguous else "false",
                    "unresolved" if (form_id, field_key) in ambiguous else "none",
                    "",
                ]
            )

    # machine candidates: (form, field) -> machine value or None (abstained)
    machines = {
        ("F-001", "total_quantity"): "10",
        ("F-001", "qualified_quantity"): "9",
        ("F-002", "total_quantity"): "25",  # wrong
        ("F-002", "qualified_quantity"): "18",
        ("F-003", "total_quantity"): "30",
        ("F-003", "qualified_quantity"): "26",  # wrong
        ("F-004", "total_quantity"): "40",
        ("F-004", "qualified_quantity"): "36",
        ("F-005", "total_quantity"): "51",  # wrong, retained -> danger
        ("F-005", "qualified_quantity"): None,  # abstained
        ("F-006", "total_quantity"): "60",
        ("F-006", "qualified_quantity"): "54",
    }
    with (data_dir / "machine_candidates.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "study_form_id",
                "field_key",
                "candidate_id",
                "certificate_id",
                "machine_value",
                "confidence",
                "selection_state",
                "producer_id",
                "producer_version",
                "template_id",
                "template_version",
                "evidence_hash",
                "evidence_locator",
            ]
        )
        for index, ((form_id, field_key), value) in enumerate(sorted(machines.items())):
            state = "SELECTED" if value is not None else "ABSTAINED"
            writer.writerow(
                [
                    form_id,
                    field_key,
                    f"ATT-{index:03d}",
                    _hash(100 + index),
                    value if value is not None else "",
                    "0.9",
                    state,
                    "fault-injector",
                    "1",
                    "T1",
                    "1",
                    SHA,
                    f"{form_id}/{field_key}",
                ]
            )

    # R1 decisions: (form, field) -> (action, final)
    r1 = {
        ("F-001", "total_quantity"): ("retain_machine", "10"),
        ("F-001", "qualified_quantity"): ("retain_machine", "9"),
        ("F-002", "total_quantity"): ("correct_machine", "20"),
        ("F-002", "qualified_quantity"): ("retain_machine", "18"),
        ("F-003", "total_quantity"): ("retain_machine", "30"),
        ("F-003", "qualified_quantity"): ("correct_machine", "27"),
        ("F-004", "total_quantity"): ("retain_machine", "40"),
        ("F-004", "qualified_quantity"): ("correct_machine", "37"),  # unnecessary
        ("F-005", "total_quantity"): ("retain_machine", "51"),  # danger
        ("F-005", "qualified_quantity"): ("manual_entry", "45"),
    }
    # R2 decisions on the locked subset F-001, F-002; one disagreement
    r2 = {
        ("F-001", "total_quantity"): ("retain_machine", "10"),
        ("F-001", "qualified_quantity"): ("retain_machine", "9"),
        ("F-002", "total_quantity"): ("correct_machine", "20"),
        ("F-002", "qualified_quantity"): ("correct_machine", "19"),
    }
    with (data_dir / "review_decisions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "study_form_id",
                "field_key",
                "reviewer_pseudonym",
                "review_session_id",
                "action",
                "presented_machine_value",
                "final_value",
                "decision_id",
                "certificate_id",
                "form_opened_at",
                "field_action_at",
                "submitted_at",
                "manual_resolution",
            ]
        )
        minutes = {"F-001": 0, "F-002": 2, "F-003": 4, "F-004": 6, "F-005": 8}
        durations = {"F-001": 90, "F-002": 90, "F-003": 120, "F-004": 60, "F-005": 60}

        def _submitted(form_id: str) -> str:
            total = minutes[form_id] * 60 + durations[form_id]
            return _timestamp(total // 60, total % 60)

        for (form_id, field_key), (action, final) in sorted(r1.items()):
            machine = machines[(form_id, field_key)] or ""
            # certificate present on every R1 decision except the manual one
            has_cert = action != "manual_entry"
            writer.writerow(
                [
                    form_id,
                    field_key,
                    "R1",
                    f"S-{form_id}",
                    action,
                    machine,
                    final,
                    f"D-{form_id}-{field_key}",
                    _hash(300) if has_cert else "",
                    _timestamp(minutes[form_id]),
                    _timestamp(minutes[form_id] + 1),
                    _submitted(form_id),
                    "false",
                ]
            )
        for (form_id, field_key), (action, final) in sorted(r2.items()):
            writer.writerow(
                [
                    form_id,
                    field_key,
                    "R2",
                    f"S2-{form_id}",
                    action,
                    machines[(form_id, field_key)],
                    final,
                    f"D2-{form_id}-{field_key}",
                    _hash(400),
                    _timestamp(20),
                    _timestamp(21),
                    _timestamp(21, 30),
                    "false",
                ]
            )

    flow = {
        "F-001": ("ok", "ok", "candidates", "confirmed", "complete", "available", ""),
        "F-002": ("ok", "ok", "candidates", "corrected", "complete", "available", ""),
        "F-003": ("ok", "ok", "candidates", "corrected", "complete", "available", ""),
        "F-004": (
            "ok",
            "failed",
            "candidates",
            "corrected",
            "incomplete",
            "available",
            "manual route",
        ),
        "F-005": (
            "ok",
            "ok",
            "abstained",
            "confirmed",
            "complete",
            "ambiguous",
            "ambiguous field",
        ),
        "F-006": (
            "failed",
            "not_attempted",
            "missing",
            "unreviewed",
            "pre-certificate",
            "available",
            "pilot",
        ),
    }
    with (data_dir / "study_flow.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "study_form_id",
                "import_status",
                "classify_status",
                "recognition_status",
                "review_status",
                "trace_status",
                "reference_status",
                "endpoint_inclusion_reason",
            ]
        )
        for form_id, values in sorted(flow.items()):
            writer.writerow([form_id, *values])
