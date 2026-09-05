from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


EXPECTED_INPUTS = frozenset(
    {
        "alloy_results.json",
        "conformance_summary.json",
        "correctness_environment.json",
        "cost_run_metadata.json",
        "cost_summary.json",
        "formal_refinement_summary.json",
        "lifecycle_summary.json",
        "performance_environment.json",
        "quality_summary.json",
        "run_summary.json",
    }
)

SCHEMA = "auto-decte-jss-evidence-digest-v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_source(input_root: Path) -> str:
    parts = input_root.resolve().parts
    try:
        release_index = parts.index("release-staging")
    except ValueError:
        return input_root.as_posix()
    return Path(*parts[release_index:]).as_posix()


def load_inputs(input_root: Path) -> dict[str, Any]:
    input_root = input_root.resolve()
    if not input_root.is_dir():
        raise ValueError(f"paper input directory does not exist: {input_root}")

    actual = {path.name for path in input_root.iterdir() if path.is_file()}
    missing = sorted(EXPECTED_INPUTS - actual)
    extra = sorted(actual - EXPECTED_INPUTS)
    if missing or extra:
        details: list[str] = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("extra=" + ",".join(extra))
        raise ValueError("paper input set mismatch: " + "; ".join(details))

    loaded: dict[str, Any] = {}
    for name in sorted(EXPECTED_INPUTS):
        with (input_root / name).open("r", encoding="utf-8") as stream:
            loaded[name] = json.load(stream)
    return loaded


def _quality_value(commands: dict[str, dict[str, Any]], command_id: str, field: str) -> int:
    command = commands[command_id]
    if command.get("exit_code") != 0:
        raise ValueError(f"quality command did not pass: {command_id}")
    return int(command[field])


def build_digest(inputs: dict[str, Any], input_root: Path) -> dict[str, Any]:
    if set(inputs) != EXPECTED_INPUTS:
        raise ValueError("build_digest requires the exact locked paper-input set")

    run = inputs["run_summary.json"]
    if run["total"] != 10 or run["passed"] != 10 or run["failed"] != 0:
        raise ValueError("locked run denominator or result changed")

    quality_commands = {
        command["command_id"]: command for command in inputs["quality_summary.json"]["commands"]
    }

    alloy_results = inputs["alloy_results.json"]
    if len(alloy_results) != 66:
        raise ValueError("locked Alloy denominator changed")
    if any(
        row["status"] != "PASS" or row["actual"] != row["expected"]
        for row in alloy_results
    ):
        raise ValueError("one or more Alloy outcomes do not match the locked expectation")

    profile_outcomes: dict[str, Counter[str]] = defaultdict(Counter)
    profile_classes: dict[str, Counter[str]] = defaultdict(Counter)
    for row in alloy_results:
        profile_outcomes[row["profile"]][row["actual"]] += 1
        profile_classes[row["profile"]][row["class"]] += 1

    refinement = inputs["formal_refinement_summary.json"]
    if refinement["case_count"] != refinement["sat_count"] + refinement["unsat_count"]:
        raise ValueError("formal-refinement denominator is inconsistent")

    conformance = inputs["conformance_summary.json"]
    if (
        conformance["declared_denominator"] != conformance["executed_denominator"]
        or conformance["passed"] != conformance["declared_denominator"]
        or conformance["failed"] != 0
    ):
        raise ValueError("conformance catalogue is incomplete or failing")

    lifecycle = inputs["lifecycle_summary.json"]
    lifecycle_complete = (
        lifecycle["status"] == "complete"
        and lifecycle["trace_status"] == "complete"
        and lifecycle["export_values_equal_final"] is True
    )
    if not lifecycle_complete:
        raise ValueError("lifecycle evidence is incomplete")

    cost = inputs["cost_summary.json"]
    cost_metadata = inputs["cost_run_metadata.json"]
    if cost_metadata["status"] != "complete":
        raise ValueError("cost run is not complete")

    admission = cost["admission"]
    trace = cost["trace"]
    storage = cost["storage"]
    negative_cells = [row for row in admission if row["paired_mean_delta_ms"] < 0]
    max_trace_p95 = max(trace, key=lambda row: row["p95_ms"])

    correctness_environment = inputs["correctness_environment.json"]
    performance_environment = inputs["performance_environment.json"]
    bound_fields = ("source_manifest_sha256", "config_sha256", "dependency_lock_sha256")
    for field in bound_fields:
        if correctness_environment[field] != performance_environment[field]:
            raise ValueError(f"correctness/performance environment mismatch: {field}")

    source_root = _display_source(input_root)
    input_hashes = {
        name: _sha256(input_root / name)
        for name in sorted(EXPECTED_INPUTS)
    }

    return {
        "schema": SCHEMA,
        "source_root": source_root,
        "input_count": len(EXPECTED_INPUTS),
        "input_sha256": input_hashes,
        "bindings": {
            "source_manifest_sha256": correctness_environment["source_manifest_sha256"],
            "config_sha256": correctness_environment["config_sha256"],
            "dependency_lock_sha256": correctness_environment["dependency_lock_sha256"],
        },
        "environment": cost_metadata["environment"],
        "run": {
            "total": int(run["total"]),
            "passed": int(run["passed"]),
            "failed": int(run["failed"]),
        },
        "quality": {
            "python_tests": _quality_value(quality_commands, "python-full-tests", "passed_tests"),
            "stateful_tests": _quality_value(quality_commands, "paper-stateful", "passed_tests"),
            "rollback_concurrency_tests": _quality_value(
                quality_commands, "paper-rollback-concurrency", "passed_tests"
            ),
            "typed_source_files": _quality_value(
                quality_commands, "python-types", "typed_source_files"
            ),
            "ruff_exit_code": int(quality_commands["python-static"]["exit_code"]),
            "mypy_exit_code": int(quality_commands["python-types"]["exit_code"]),
        },
        "alloy": {
            "total": len(alloy_results),
            "profiles": {
                profile: {
                    "SAT": profile_outcomes[profile]["SAT"],
                    "UNSAT": profile_outcomes[profile]["UNSAT"],
                    "classes": dict(sorted(profile_classes[profile].items())),
                }
                for profile in sorted(profile_outcomes)
            },
        },
        "refinement": {
            "SAT": int(refinement["sat_count"]),
            "UNSAT": int(refinement["unsat_count"]),
            "total": int(refinement["case_count"]),
        },
        "conformance": {
            "passed": int(conformance["passed"]),
            "failed": int(conformance["failed"]),
            "denominator": int(conformance["declared_denominator"]),
            "catalogue_version": conformance["catalogue_version"],
        },
        "lifecycle": {
            "complete": lifecycle_complete,
            "versions": lifecycle["versions"],
            "machine_candidate": lifecycle["correction"]["machine_candidate"],
            "authorized_value": lifecycle["correction"]["authorized_value"],
            "copy_forward_fields": lifecycle["copy_forward_fields"],
        },
        "cost": {
            "config": cost_metadata["config"],
            "admission": {
                "cells": len(admission),
                "observations": sum(int(row["trials"]) for row in admission),
                "full_p50_min_ms": min(row["full_p50_ms"] for row in admission),
                "full_p50_max_ms": max(row["full_p50_ms"] for row in admission),
                "paired_delta_min_ms": min(row["paired_mean_delta_ms"] for row in admission),
                "paired_delta_max_ms": max(row["paired_mean_delta_ms"] for row in admission),
                "negative_delta_cells": len(negative_cells),
                "negative_cells": [
                    {
                        "fields": row["fields"],
                        "changed": row["changed"],
                        "paired_mean_delta_ms": row["paired_mean_delta_ms"],
                    }
                    for row in negative_cells
                ],
            },
            "trace": {
                "cells": len(trace),
                "observations": sum(int(row["trials"]) for row in trace),
                "p50_min_ms": min(row["p50_ms"] for row in trace),
                "p50_max_ms": max(row["p50_ms"] for row in trace),
                "max_p95_ms": max_trace_p95["p95_ms"],
                "max_p95_cell": {
                    "fields": max_trace_p95["fields"],
                    "versions": max_trace_p95["versions"],
                    "records": max_trace_p95["records"],
                },
            },
            "storage": {
                "populations": len(storage),
                "transitions": [int(row["transitions"]) for row in storage],
                "incremental_bytes": [int(row["incremental_bytes"]) for row in storage],
            },
        },
    }


def _header(source: str, files: str) -> str:
    return (
        "% AUTO-GENERATED by jss/scripts/build_evidence_tables.py. DO NOT EDIT.\n"
        f"% Source: {source}/{files}\n"
    )


def _f3(value: float) -> str:
    return f"{value:.3f}"


def render_formal_evidence(inputs: dict[str, Any], digest: dict[str, Any]) -> str:
    del inputs
    lines = [
        _header(digest["source_root"], "alloy_results.json"),
        "\\begin{table}[t]\n",
        "\\centering\n",
        "\\caption{Bounded Alloy outcomes in the two declared scopes. SAT denotes a found witness; UNSAT denotes no instance within the encoded scope.}\n",
        "\\label{tab:alloy-outcomes}\n",
        "\\begin{tabularx}{\\linewidth}{@{}l*{5}{>{\\centering\\arraybackslash}X}>{\\centering\\arraybackslash}p{0.15\\linewidth}@{}}\n",
        "\\toprule\n",
        "Profile & Legal SAT & Ablation SAT & Attack SAT & Total SAT & Total UNSAT & Commands \\\\\n",
        "\\midrule\n",
    ]
    for profile, values in digest["alloy"]["profiles"].items():
        classes = values["classes"]
        lines.append(
            f"{profile} & {classes.get('legal-witness', 0)} & "
            f"{classes.get('ablation-witness', 0)} & {classes.get('attack-witness', 0)} & "
            f"{values['SAT']} & {values['UNSAT']} & {values['SAT'] + values['UNSAT']} \\\\\n"
        )
    lines.extend(
        [
            "\\bottomrule\n",
            "\\end{tabularx}\n",
            "\\end{table}\n",
        ]
    )
    return "".join(lines)


def render_validation_evidence(inputs: dict[str, Any], digest: dict[str, Any]) -> str:
    del inputs
    q = digest["quality"]
    r = digest["refinement"]
    c = digest["conformance"]
    rows = [
        ("Full Python suite", f"{q['python_tests']}/{q['python_tests']} passed"),
        ("Static and type checks", f"Ruff exit {q['ruff_exit_code']}; mypy exit {q['mypy_exit_code']} over {q['typed_source_files']} files"),
        ("Stateful profiles", f"{q['stateful_tests']}/{q['stateful_tests']} passed"),
        ("Rollback and concurrency profiles", f"{q['rollback_concurrency_tests']}/{q['rollback_concurrency_tests']} passed"),
        ("Formal--concrete projection", f"{r['SAT']} intended SAT; {r['UNSAT']} mutants UNSAT"),
        ("Independent catalogue", f"{c['passed']}/{c['denominator']} passed"),
        ("Illustrative lifecycle", "complete; reverse trace complete; export equals final values"),
    ]
    lines = [
        _header(
            digest["source_root"],
            "quality_summary.json, formal_refinement_summary.json, conformance_summary.json, lifecycle_summary.json",
        ),
        "\\begin{table}[t]\n",
        "\\centering\n",
        "\\caption{Frozen executable evidence. Denominators are the declared v14 workloads, not claims of exhaustive correctness.}\n",
        "\\label{tab:executable-evidence}\n",
        "\\begin{tabularx}{\\textwidth}{@{}>{\\raggedright\\arraybackslash}p{0.32\\textwidth}>{\\raggedright\\arraybackslash}X@{}}\n",
        "\\toprule\n",
        "Evidence surface & Frozen observation \\\\\n",
        "\\midrule\n",
    ]
    lines.extend(f"{name} & {value} \\\\\n" for name, value in rows)
    lines.extend(["\\bottomrule\n", "\\end{tabularx}\n", "\\end{table}\n"])
    return "".join(lines)


def render_admission_cost(inputs: dict[str, Any], digest: dict[str, Any]) -> str:
    rows = inputs["cost_summary.json"]["admission"]
    lines = [
        _header(digest["source_root"], "cost_summary.json"),
        "\\begin{table}[t]\n",
        "\\centering\n",
        "\\caption{Paired admission measurements on the frozen configuration (200 measured pairs per cell). Negative deltas are retained.}\n",
        "\\label{tab:admission-cost}\n",
        "\\footnotesize\n",
        "\\setlength{\\tabcolsep}{5.5pt}\n",
        "\\begin{tabular}{rrrrrrr}\n",
        "\\toprule\n",
        "Fields & Changed & Lower p50 & Full p50 & Full p95 & Mean delta & 95\\% CI \\\\\n",
        " & & \\multicolumn{5}{c}{milliseconds} \\\\\n",
        "\\midrule\n",
    ]
    for row in rows:
        low, high = row["paired_mean_delta_95ci_ms"]
        lines.append(
            f"{row['fields']} & {row['changed']} & {_f3(row['lower_p50_ms'])} & "
            f"{_f3(row['full_p50_ms'])} & {_f3(row['full_p95_ms'])} & "
            f"{_f3(row['paired_mean_delta_ms'])} & "
            f"[{_f3(low)}, {_f3(high)}] \\\\\n"
        )
    lines.extend(["\\bottomrule\n", "\\end{tabular}\n", "\\end{table}\n"])
    return "".join(lines)


def render_trace_storage_cost(inputs: dict[str, Any], digest: dict[str, Any]) -> str:
    trace_rows = inputs["cost_summary.json"]["trace"]
    storage_rows = inputs["cost_summary.json"]["storage"]
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in trace_rows:
        grouped[(int(row["fields"]), int(row["versions"]))].append(row)

    lines = [
        _header(digest["source_root"], "cost_summary.json"),
        "\\begin{table}[t]\n",
        "\\centering\n",
        "\\caption{Reverse-trace latency summarized over the three record populations. Each underlying cell has 200 trials.}\n",
        "\\label{tab:trace-cost}\n",
        "\\begin{tabular}{rrrr}\n",
        "\\toprule\n",
        "Fields & Versions & p50 range (ms) & Maximum p95 (ms) \\\\\n",
        "\\midrule\n",
    ]
    for (fields, versions), group in sorted(grouped.items()):
        p50_min = min(row["p50_ms"] for row in group)
        p50_max = max(row["p50_ms"] for row in group)
        p95_max = max(row["p95_ms"] for row in group)
        lines.append(
            f"{fields} & {versions} & {_f3(p50_min)}--{_f3(p50_max)} & {_f3(p95_max)} \\\\\n"
        )
    lines.extend(
        [
            "\\bottomrule\n",
            "\\end{tabular}\n",
            "\\end{table}\n\n",
            "\\begin{table}[t]\n",
            "\\centering\n",
            "\\caption{SQLite main-database storage under the frozen measurement protocol.}\n",
            "\\label{tab:storage-cost}\n",
            "\\begin{tabular}{rrrr}\n",
            "\\toprule\n",
            "Transitions & Lower bytes & Full bytes & Incremental bytes \\\\\n",
            "\\midrule\n",
        ]
    )
    for row in storage_rows:
        lines.append(
            f"{row['transitions']:,} & {row['lower']['bytes']:,} & {row['full']['bytes']:,} & "
            f"{row['incremental_bytes']:,} \\\\\n"
        )
    lines.extend(["\\bottomrule\n", "\\end{tabular}\n", "\\end{table}\n"])
    return "".join(lines)


def generate(input_root: Path, output_root: Path) -> None:
    inputs = load_inputs(input_root)
    digest = build_digest(inputs, input_root)
    output_root.mkdir(parents=True, exist_ok=True)

    outputs = {
        "formal_evidence.tex": render_formal_evidence(inputs, digest),
        "validation_evidence.tex": render_validation_evidence(inputs, digest),
        "admission_cost.tex": render_admission_cost(inputs, digest),
        "trace_storage_cost.tex": render_trace_storage_cost(inputs, digest),
    }
    for name, content in outputs.items():
        (output_root / name).write_text(content, encoding="utf-8", newline="\n")
    (output_root / "evidence_digest.json").write_text(
        json.dumps(digest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _default_input_root() -> Path:
    package_root = Path(__file__).resolve().parents[2]
    return package_root / "evidence" / "frozen" / "paper-final" / "paper_inputs"


def _default_output_root() -> Path:
    return Path(__file__).resolve().parents[1] / "tables" / "generated"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate evidence-locked JSS tables.")
    parser.add_argument("--input-root", type=Path, default=_default_input_root())
    parser.add_argument("--output-root", type=Path, default=_default_output_root())
    args = parser.parse_args()
    generate(args.input_root, args.output_root)


if __name__ == "__main__":
    main()
