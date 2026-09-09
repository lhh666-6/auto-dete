"""Pre-specified endpoint analysis for the real-form human review study.

Implements protocol sections 2.3 (primary estimands), 9 (agreement), 10
(statistical plan: form-clustered bootstrap with a fixed seed, sensitivity
analyses, no pseudo-independence), 12 (immutable outputs and manifest).

Primary universe: fields of confirmatory (included) forms; "evaluable"
means a reference value is available. Completion and accuracy are always
reported together so absence cannot inflate accuracy (protocol 8.3).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import subprocess
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_BOOTSTRAP_SEED = 20260817
BOOTSTRAP_RESAMPLES = 10_000
KAPPA_LOW = 0.6
KAPPA_TARGET = 0.7
R_DANGER_MIN_WRONG_VALUES = 30
R_DANGER_MIN_WRONG_FORMS = 10

ACTIONS = [
    "retain_machine",
    "correct_machine",
    "manual_entry",
    "abstain_reacquire",
]

RESULTS_SCHEMA_VERSION = 1


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _flag(row: dict[str, str], column: str) -> bool:
    return row.get(column, "").strip().lower() == "true"


def _group_by_form(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["study_form_id"], []).append(row)
    return grouped


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def primary_endpoints(fields: list[dict[str, str]]) -> dict[str, object]:
    """Compute the three primary estimands on a set of field rows."""
    confirmatory = [row for row in fields if _flag(row, "confirmatory")]
    eligible = len(confirmatory)
    reviewed = [row for row in confirmatory if _flag(row, "reviewed")]
    evaluable = [row for row in confirmatory if _flag(row, "evaluable")]
    reviewed_evaluable = [row for row in reviewed if _flag(row, "evaluable")]
    presented = [row for row in reviewed_evaluable if _flag(row, "machine_presented")]
    wrong = [row for row in presented if _flag(row, "wrong_w")]
    danger = [row for row in wrong if _flag(row, "retained_a")]
    retained = [row for row in presented if _flag(row, "retained_a")]
    correct = [row for row in reviewed_evaluable if _flag(row, "correct")]
    wrong_forms = {row["study_form_id"] for row in wrong}

    danger_descriptive = (
        len(wrong) < R_DANGER_MIN_WRONG_VALUES
        or len(wrong_forms) < R_DANGER_MIN_WRONG_FORMS
    )
    return {
        "completion_rate": _rate(len(reviewed), eligible),
        "final_factual_accuracy": _rate(len(correct), len(reviewed_evaluable)),
        "r_danger": _rate(len(danger), len(wrong)),
        "r_danger_numerator": len(danger),
        "r_danger_denominator": len(wrong),
        "r_danger_wrong_forms": len(wrong_forms),
        "r_danger_imprecise_descriptive": danger_descriptive,
        "reviewed_machine_value_retention": _rate(len(retained), len(presented)),
        "denominators": {
            "eligible_fields": eligible,
            "reviewed_fields": len(reviewed),
            "evaluable_fields": len(evaluable),
            "reviewed_evaluable_fields": len(reviewed_evaluable),
            "machine_presented_fields": len(presented),
            "forms": len({row["study_form_id"] for row in confirmatory}),
        },
    }


def _endpoint_values(fields: list[dict[str, str]]) -> tuple[float, float, float, float]:
    """(accuracy, r_danger, retention, completion) for one field set."""
    primary = primary_endpoints(fields)
    return (
        float(primary["final_factual_accuracy"]),
        float(primary["r_danger"]),
        float(primary["reviewed_machine_value_retention"]),
        float(primary["completion_rate"]),
    )


def form_clustered_bootstrap(
    fields: list[dict[str, str]], seed: int, resamples: int = BOOTSTRAP_RESAMPLES
) -> dict[str, dict[str, float]]:
    """Resample forms (with all their fields intact) and percentile CI."""
    forms = _group_by_form(fields)
    form_ids = sorted(forms)
    rng = random.Random(seed)
    accuracy_values: list[float] = []
    danger_values: list[float] = []
    retention_values: list[float] = []
    completion_values: list[float] = []
    for _ in range(resamples):
        sample: list[dict[str, str]] = []
        for _ in range(len(form_ids)):
            sample.extend(forms[rng.choice(form_ids)])
        acc, danger, retention, completion = _endpoint_values(sample)
        accuracy_values.append(acc)
        danger_values.append(danger)
        retention_values.append(retention)
        completion_values.append(completion)

    def _ci(values: list[float]) -> dict[str, float]:
        ordered = sorted(values)
        return {
            "lower": ordered[int(0.025 * len(ordered)) - 1],
            "point": sum(ordered) / len(ordered),
            "upper": ordered[int(0.975 * len(ordered)) - 1],
        }

    return {
        "final_factual_accuracy": _ci(accuracy_values),
        "r_danger": _ci(danger_values),
        "reviewed_machine_value_retention": _ci(retention_values),
        "completion_rate": _ci(completion_values),
    }


def cohen_kappa(first: list[str], second: list[str], categories: list[str]) -> float:
    """Cohen's kappa over nominal categories; -inf handling avoided."""
    count = len(first)
    if count == 0:
        return float("nan")
    observed = sum(a == b for a, b in zip(first, second, strict=True)) / count
    expected = 0.0
    for category in categories:
        p1 = first.count(category) / count
        p2 = second.count(category) / count
        expected += p1 * p2
    if expected >= 1.0:
        return float("nan")
    return (observed - expected) / (1.0 - expected)


def reviewer_agreement(
    fields: list[dict[str, str]], decisions_path: Path
) -> dict[str, object]:
    """R1 vs R2 agreement on the locked reliability subset (protocol 9)."""
    decisions = _load_rows(decisions_path)
    r1: dict[tuple[str, str], dict[str, str]] = {}
    r2: dict[tuple[str, str], dict[str, str]] = {}
    for row in decisions:
        key = (row["study_form_id"], row["field_key"])
        if row["reviewer_pseudonym"] == "R1":
            r1[key] = row
        elif row["reviewer_pseudonym"] == "R2":
            r2[key] = row
    shared_keys = sorted(set(r1) & set(r2))
    if not shared_keys:
        return {
            "shared_fields": 0,
            "forms": 0,
            "note": "no R2 subset rows present; agreement not estimable",
        }
    action_pairs = [(r1[key]["action"], r2[key]["action"]) for key in shared_keys]
    value_pairs = [
        (r1[key].get("final_value", ""), r2[key].get("final_value", ""))
        for key in shared_keys
    ]
    raw_action = sum(a == b for a, b in action_pairs) / len(action_pairs)
    exact_value = sum(a == b for a, b in value_pairs) / len(value_pairs)
    first_actions = [a for a, _ in action_pairs]
    second_actions = [b for _, b in action_pairs]
    kappa = cohen_kappa(first_actions, second_actions, ACTIONS)
    one_vs_rest: dict[str, dict[str, float]] = {}
    for category in ACTIONS:
        binary_first = [1 if action == category else 0 for action in first_actions]
        binary_second = [1 if action == category else 0 for action in second_actions]
        one_vs_rest[category] = {
            "count": first_actions.count(category) + second_actions.count(category),
            "raw_agreement": _rate(
                sum(a == b for a, b in zip(binary_first, binary_second, strict=True)),
                len(binary_first),
            ),
            "kappa": cohen_kappa(binary_first, binary_second, [0, 1]),
        }
    disagreement = [
        {"study_form_id": key[0], "field_key": key[1],
         "r1_action": r1[key]["action"], "r2_action": r2[key]["action"]}
        for key in shared_keys
        if r1[key]["action"] != r2[key]["action"]
    ]
    return {
        "shared_fields": len(shared_keys),
        "forms": len({key[0] for key in shared_keys}),
        "exact_final_value_agreement": exact_value,
        "raw_action_agreement": raw_action,
        "cohen_kappa_overall": kappa,
        "cohen_kappa_low_limitation": not (kappa == kappa and kappa >= KAPPA_LOW),
        "cohen_kappa_target": KAPPA_TARGET,
        "one_vs_rest": one_vs_rest,
        "disagreement_count": len(disagreement),
        "disagreements": disagreement[:20],
    }


def secondary_endpoints(
    fields: list[dict[str, str]], decisions_path: Path
) -> dict[str, object]:
    """Descriptive secondary endpoints (protocol 2.4)."""
    confirmatory = [row for row in fields if _flag(row, "confirmatory")]
    reviewed = [row for row in confirmatory if _flag(row, "reviewed")]
    evaluated = [row for row in reviewed if _flag(row, "evaluable")]
    presented = [row for row in evaluated if _flag(row, "machine_presented")]
    machine_correct = [
        row for row in presented if _eq_machine_reference(row)
    ]
    abstained = [
        row for row in confirmatory
        if not _flag(row, "machine_presented")
    ]
    corrected = [
        row for row in presented if row.get("action", "") == "correct_machine"
    ]
    manual = [
        row for row in reviewed if row.get("action", "") == "manual_entry"
    ]
    unnecessary = [
        row for row in corrected
        if _eq_machine_reference(row) and not _flag(row, "correct")
    ]
    form_groups = _group_by_form(evaluated)
    exact_forms = sum(
        1 for group in form_groups.values()
        if group and all(_flag(row, "correct") for row in group)
    )
    forms_with_flow = {row["study_form_id"] for row in fields if row.get("import_status")}
    import_failed = sum(
        1 for row in fields if row.get("import_status") == "failed"
    )
    classify_failed = sum(
        1 for row in fields if row.get("classify_status") in ("failed", "manual_route")
    )
    trace_complete = sum(
        1 for row in reviewed if row.get("trace_status") == "complete"
    )
    certificate_coverage = _certificate_coverage(decisions_path)
    timing = _form_level_timing(decisions_path)
    return {
        "machine_candidate_exact_match_accuracy": _rate(
            len(machine_correct), len(presented)
        ),
        "machine_abstention_rate": _rate(len(abstained), len(confirmatory)),
        "correction_burden": _rate(len(corrected), len(presented)),
        "manual_entry_burden": _rate(len(manual), len(confirmatory)),
        "unnecessary_change_rate": _rate(len(unnecessary), len(corrected)),
        "form_level_exact_accuracy": _rate(exact_forms, len(form_groups)),
        "import_failure_rate": _rate(import_failed, len(forms_with_flow)),
        "classify_failure_or_manual_route_rate": _rate(
            classify_failed, len(forms_with_flow)
        ),
        "trace_completeness_among_reviewed": _rate(
            trace_complete, len(reviewed)
        ),
        "certificate_coverage_among_confirmed": certificate_coverage,
        "form_level_timing_seconds": timing,
    }


def _eq_machine_reference(row: dict[str, str]) -> bool:
    return (row.get("machine_value", "") or "").strip() == (
        row.get("reference_value", "") or ""
    ).strip()


def _certificate_coverage(decisions_path: Path) -> float:
    decisions = _load_rows(decisions_path)
    confirmed = [row for row in decisions if row["reviewer_pseudonym"] == "R1"]
    if not confirmed:
        return float("nan")
    with_certificate = [
        row for row in confirmed if row.get("certificate_id", "").strip()
    ]
    return _rate(len(with_certificate), len(confirmed))


def _form_level_timing(decisions_path: Path) -> dict[str, float] | None:
    """Form-level duration: one measurement per (form, reviewer) session.

    Every field row of one form shares the same session timestamps, so each
    (study_form_id, reviewer_pseudonym) session contributes exactly one
    duration. R1 durations are the primary per-form review times; R2
    sessions are reported separately (protocol 7: form-level only, never
    per-field).
    """
    decisions = _load_rows(decisions_path)
    sessions: dict[tuple[str, str], tuple[str, str]] = {}
    for row in decisions:
        key = (row.get("study_form_id", ""), row.get("reviewer_pseudonym", ""))
        opened = row.get("form_opened_at", "")
        submitted = row.get("submitted_at", "")
        if not key[0] or not opened or not submitted:
            continue
        sessions.setdefault(key, (opened, submitted))

    def _durations(pseudonym: str) -> list[float]:
        values: list[float] = []
        for (form_id, reviewer), (opened, submitted) in sessions.items():
            if reviewer != pseudonym:
                continue
            del form_id
            try:
                start = datetime.fromisoformat(opened.replace("Z", "+00:00"))
                end = datetime.fromisoformat(submitted.replace("Z", "+00:00"))
            except ValueError:
                continue
            if start.tzinfo is None or end.tzinfo is None:
                continue
            seconds = (end - start).total_seconds()
            if 0 <= seconds <= 24 * 3600:
                values.append(seconds)
        return sorted(values)

    r1 = _durations("R1")
    r2 = _durations("R2")
    if not r1:
        return None

    def _summary(values: list[float]) -> dict[str, float]:
        return {
            "mean_seconds": sum(values) / len(values),
            "median_seconds": values[len(values) // 2],
        }

    result: dict[str, float] = {
        **_summary(r1),
        "forms_with_timing": len(r1),
        "r2_forms_with_timing": len(r2),
    }
    if r2:
        result.update({f"r2_{key}": value for key, value in _summary(r2).items()})
    return result


def sensitivity_analyses(fields: list[dict[str, str]]) -> dict[str, object]:
    """Pre-specified sensitivity analyses (protocol 10.2)."""
    confirmatory = [row for row in fields if _flag(row, "confirmatory")]
    ambiguous = [row for row in confirmatory if _flag(row, "ambiguity_flag")]
    evaluable = [row for row in confirmatory if _flag(row, "evaluable")]
    unresolved = [
        row for row in confirmatory
        if _flag(row, "ambiguity_flag")
        and row.get("adjudication_status", "") == "unresolved"
    ]
    manual_route = [
        row for row in confirmatory
        if row.get("classify_status", "") in ("failed", "manual_route")
    ]

    def _accuracy(rows: list[dict[str, str]]) -> float:
        reviewed = [row for row in rows if _flag(row, "reviewed") and _flag(row, "evaluable")]
        correct = sum(1 for row in reviewed if _flag(row, "correct"))
        return _rate(correct, len(reviewed))

    def _accuracy_all_eligible(rows: list[dict[str, str]]) -> float:
        reviewed = [row for row in rows if _flag(row, "reviewed") and _flag(row, "evaluable")]
        correct = sum(1 for row in reviewed if _flag(row, "correct"))
        return _rate(correct, len(rows))

    stratified: dict[str, dict[str, float]] = {}
    for template in sorted({row["template_id"] for row in evaluable}):
        template_rows = [row for row in evaluable if row["template_id"] == template]
        stratified[template] = {"accuracy": _accuracy(template_rows), "fields": len(template_rows)}
    form_weighted = _form_weighted_accuracy(evaluable)
    return {
        "all_eligible_forms_completion_included": _accuracy_all_eligible(confirmatory),
        "ambiguous_excluded": _accuracy(
            [row for row in confirmatory if not _flag(row, "ambiguity_flag")]
        ),
        "ambiguous_counted_unresolved": _accuracy(confirmatory),
        "manual_route_included": _accuracy(confirmatory),
        "manual_route_separate": _accuracy(
            [row for row in confirmatory if row not in manual_route]
        ),
        "ambiguous_fields": len(ambiguous),
        "unresolved_fields": len(unresolved),
        "manual_route_fields": len(manual_route),
        "template_stratified": stratified,
        "form_weighted_accuracy": form_weighted,
    }


def _form_weighted_accuracy(rows: list[dict[str, str]]) -> float:
    groups = _group_by_form(rows)
    per_form: list[float] = []
    for group in groups.values():
        reviewed = [row for row in group if _flag(row, "reviewed") and _flag(row, "evaluable")]
        if not reviewed:
            continue
        correct = sum(1 for row in reviewed if _flag(row, "correct"))
        per_form.append(_rate(correct, len(reviewed)))
    return _rate(sum(per_form), len(per_form)) if per_form else float("nan")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(command: list[str], cwd: Path) -> str:
    """Run git; return an empty string when unavailable (e.g. a test dir).

    The manifest records the empty result honestly instead of crashing:
    outside a git checkout the analysis cannot claim a commit or cleanliness.
    """
    try:
        completed = subprocess.run(
            ["git", *command], check=False, capture_output=True, text=True,
            timeout=30, cwd=cwd,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def write_manifest(
    artifacts_dir: Path,
    data_dir: Path,
    repo_root: Path,
    seed: int,
    started: datetime,
) -> None:
    """Immutable manifest per protocol section 12."""
    artifact_entries = []
    for path in sorted(artifacts_dir.iterdir()):
        if path.name == "manifest.json" or not path.is_file():
            continue
        artifact_entries.append(
            {"path": path.name, "sha256": _sha256(path), "bytes": path.stat().st_size}
        )

    def _hash_if_present(filename: str) -> str | None:
        path = data_dir / filename
        return _sha256(path) if path.exists() else None

    porcelain = _git(["status", "--porcelain"], repo_root)
    packages = {}
    for package in ("sqlalchemy", "numpy", "pydantic"):
        try:
            import importlib.metadata

            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = None
    manifest = {
        "schema_version": RESULTS_SCHEMA_VERSION,
        "analysis_commit": _git(["rev-parse", "HEAD"], repo_root),
        "clean_before_run": not porcelain,
        "git_status_porcelain": porcelain,
        "locked_protocol_sha256": _hash_if_present("protocol_sha256.txt")
        or _sha256(repo_root / "docs/dsh/human-review-study-protocol.md"),
        "locked_form_list_sha256": _hash_if_present("forms.csv"),
        "r2_subset_sha256": _hash_if_present("r2_subset.txt"),
        "data_dictionary_sha256": _sha256(
            repo_root / "docs/dsh/human-review-study-data-dictionary.md"
        ),
        "packages": packages,
        "bootstrap_seed": seed,
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "started_utc": started.isoformat(),
        "ended_utc": datetime.now(UTC).isoformat(),
        "artifacts": artifact_entries,
    }
    (artifacts_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def analyze_study(
    data_dir: Path,
    artifacts_dir: Path,
    repo_root: Path,
    *,
    bootstrap_seed: int = DEFAULT_BOOTSTRAP_SEED,
) -> dict[str, object]:
    """Run the full pre-specified analysis and write immutable artifacts."""
    from analysis.real_form_study.build_analysis_dataset import (
        build_analysis_dataset,
    )

    fields = build_analysis_dataset(data_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC)
    confirmatory = [row for row in fields if _flag(row, "confirmatory")]
    results: dict[str, object] = {
        "schema_version": RESULTS_SCHEMA_VERSION,
        "primary": primary_endpoints(fields),
        "bootstrap": form_clustered_bootstrap(confirmatory, bootstrap_seed),
        "secondary": secondary_endpoints(fields, data_dir / "review_decisions.csv"),
        "agreement": reviewer_agreement(fields, data_dir / "review_decisions.csv"),
        "sensitivity": sensitivity_analyses(fields),
        "flows": {
            "forms": len({row["study_form_id"] for row in fields}),
            "fields": len(fields),
            "confirmatory_fields": len(confirmatory),
        },
    }
    (artifacts_dir / "endpoint_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_tables(results, artifacts_dir)
    _write_figure_data(fields, artifacts_dir)
    _write_exclusions(fields, artifacts_dir)
    _write_flow(data_dir, artifacts_dir)
    _write_deviations(data_dir, artifacts_dir)
    write_manifest(artifacts_dir, data_dir, repo_root, bootstrap_seed, started)
    return results


def _write_tables(results: dict[str, object], artifacts_dir: Path) -> None:
    primary = results["primary"]
    assert isinstance(primary, dict)
    rows = [{"endpoint": key, "value": value} for key, value in primary.items()]
    with (artifacts_dir / "endpoint_tables.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["endpoint", "value"])
        writer.writeheader()
        writer.writerows(rows)


def _write_figure_data(fields: list[dict[str, str]], artifacts_dir: Path) -> None:
    with (artifacts_dir / "figure_data.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "study_form_id", "template_id", "field_key", "evaluable",
                "reviewed", "correct", "wrong_w", "retained_a", "action",
            ],
        )
        writer.writeheader()
        for row in fields:
            writer.writerow(
                {
                    "study_form_id": row["study_form_id"],
                    "template_id": row["template_id"],
                    "field_key": row["field_key"],
                    "evaluable": row["evaluable"],
                    "reviewed": row["reviewed"],
                    "correct": row["correct"],
                    "wrong_w": row["wrong_w"],
                    "retained_a": row["retained_a"],
                    "action": row["action"],
                }
            )


def _write_exclusions(fields: list[dict[str, str]], artifacts_dir: Path) -> None:
    excluded = [
        {
            "study_form_id": row["study_form_id"],
            "field_key": row["field_key"],
            "reason": (
                "not confirmatory" if not _flag(row, "confirmatory")
                else "not evaluated" if not _flag(row, "evaluable")
                else "not reviewed"
            ),
        }
        for row in fields
        if not (_flag(row, "confirmatory") and _flag(row, "evaluable") and _flag(row, "reviewed"))
    ]
    with (artifacts_dir / "exclusions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["study_form_id", "field_key", "reason"])
        writer.writeheader()
        writer.writerows(excluded)


def _write_flow(data_dir: Path, artifacts_dir: Path) -> None:
    source = data_dir / "study_flow.csv"
    if source.exists():
        (artifacts_dir / "study_flow.csv").write_bytes(source.read_bytes())


def _write_deviations(data_dir: Path, artifacts_dir: Path) -> None:
    source = data_dir / "protocol_deviations.md"
    if source.exists():
        (artifacts_dir / "protocol_deviations.md").write_bytes(source.read_bytes())
    else:
        (artifacts_dir / "protocol_deviations.md").write_text(
            "# Protocol deviations\n\nNone recorded.\n", encoding="utf-8"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the pre-specified study analysis")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--artifacts-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--bootstrap-seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    args = parser.parse_args(argv)
    results = analyze_study(
        args.data_dir, args.artifacts_dir, args.repo_root,
        bootstrap_seed=args.bootstrap_seed,
    )
    primary = results["primary"]
    assert isinstance(primary, dict)
    print(json.dumps(primary, indent=2, sort_keys=True))
    print(f"artifacts -> {args.artifacts_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
