"""Build the long-format analysis dataset from the locked study CSVs.

Joins forms, reference_fields, machine_candidates, review_decisions (R1),
and study_flow into one row per (study_form_id, field_key) with the derived
estimand flags from protocol section 2.3:

- A_i: reviewer retains the presented machine value unchanged;
- W_i: a machine value is presented and differs from the reference value;
- correct: final fact equals the reference value.

The join happens only after the review export is frozen (protocol 5.2);
this script never touches reference or decision sources that are not part
of the locked CSV exports.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from analysis.real_form_study.validate_study_inputs import (
    validate_study_inputs,
)

OUTPUT_COLUMNS = [
    "study_form_id", "field_key", "template_id", "capture_condition",
    "inclusion_status", "physical_form_cluster",
    "reference_value", "reference_source", "ambiguity_flag", "adjudication_status",
    "machine_presented", "machine_value", "confidence", "selection_state",
    "producer_id", "producer_version", "certificate_id",
    "action", "final_value", "reviewed", "retained_a", "wrong_w", "correct",
    "evaluable", "confirmatory", "reviewer_pseudonym",
    "import_status", "classify_status", "trace_status",
]


def _load(data_dir: Path, filename: str) -> list[dict[str, str]]:
    path = data_dir / filename
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _eq(left: str | None, right: str | None) -> bool:
    """Canonical value equality: stripped strings, empty == None."""
    return (left or "").strip() == (right or "").strip()


def build_analysis_dataset(data_dir: Path) -> list[dict[str, str]]:
    """Return the long-format analysis rows (one per target field)."""
    errors = validate_study_inputs(data_dir)
    if errors:
        raise ValueError(
            "study inputs failed validation; refusing to build dataset:\n"
            + "\n".join(errors)
        )
    forms = {row["study_form_id"]: row for row in _load(data_dir, "forms.csv")}
    references = _load(data_dir, "reference_fields.csv")
    machines = _load(data_dir, "machine_candidates.csv")
    decisions = _load(data_dir, "review_decisions.csv")
    flows = {row["study_form_id"]: row for row in _load(data_dir, "study_flow.csv")}

    reference_by_key = {(row["study_form_id"], row["field_key"]): row for row in references}
    machine_by_key = {(row["study_form_id"], row["field_key"]): row for row in machines}
    r1_by_key: dict[tuple[str, str], dict[str, str]] = {}
    for row in decisions:
        if row["reviewer_pseudonym"] == "R1":
            r1_by_key[(row["study_form_id"], row["field_key"])] = row

    keys = sorted(set(reference_by_key) | set(machine_by_key))
    rows: list[dict[str, str]] = []
    for form_id, field_key in keys:
        reference = reference_by_key.get((form_id, field_key), {})
        machine = machine_by_key.get((form_id, field_key), {})
        decision = r1_by_key.get((form_id, field_key), {})
        form = forms.get(form_id, {})
        flow = flows.get(form_id, {})
        machine_presented = bool(machine.get("machine_value", "").strip())
        action = decision.get("action", "")
        final_value = decision.get("final_value", "")
        reviewed = bool(decision)
        retained = reviewed and action == "retain_machine"
        reference_value = reference.get("reference_value", "")
        evaluable = bool(reference_value)
        wrong = (
            machine_presented and evaluable
            and not _eq(machine.get("machine_value"), reference_value)
        )
        correct = (
            reviewed and evaluable and _eq(final_value, reference_value)
        )
        rows.append(
            {
                "study_form_id": form_id,
                "field_key": field_key,
                "template_id": form.get("template_id", ""),
                "capture_condition": form.get("capture_condition", ""),
                "inclusion_status": form.get("inclusion_status", ""),
                "physical_form_cluster": form.get("physical_form_cluster", ""),
                "reference_value": reference_value,
                "reference_source": reference.get("reference_source", ""),
                "ambiguity_flag": reference.get("ambiguity_flag", ""),
                "adjudication_status": reference.get("adjudication_status", ""),
                "machine_presented": "true" if machine_presented else "false",
                "machine_value": machine.get("machine_value", ""),
                "confidence": machine.get("confidence", ""),
                "selection_state": machine.get("selection_state", ""),
                "producer_id": machine.get("producer_id", ""),
                "producer_version": machine.get("producer_version", ""),
                "certificate_id": machine.get("certificate_id", ""),
                "action": action,
                "final_value": final_value,
                "reviewed": "true" if reviewed else "false",
                "retained_a": "true" if retained else "false",
                "wrong_w": "true" if wrong else "false",
                "correct": "true" if correct else "false",
                "evaluable": "true" if evaluable else "false",
                "confirmatory": (
                    "true" if form.get("inclusion_status", "") == "included" else "false"
                ),
                "reviewer_pseudonym": decision.get("reviewer_pseudonym", ""),
                "import_status": flow.get("import_status", ""),
                "classify_status": flow.get("classify_status", ""),
                "trace_status": flow.get("trace_status", ""),
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the analysis dataset")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    rows = build_analysis_dataset(args.data_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"analysis dataset: {len(rows)} field rows -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
