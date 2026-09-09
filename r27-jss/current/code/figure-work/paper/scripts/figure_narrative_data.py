"""Read-only checks for the frozen evidence used by the narrative figures."""
from __future__ import annotations

import json
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
FEATURE_INPUT = PACKAGE_ROOT / "evidence/paper-inputs/r21_feature_baseline_summary.json"
TRACE_INPUT = PACKAGE_ROOT / "evidence/paper-inputs/r21_trace_optimization_summary.json"
RUNS_INPUT = PACKAGE_ROOT / (
    "evidence/agent-authority-benchmark-v2/manuscript-input/"
    "2026-09-03-three-config-10x/normalized/agent_authority_benchmark_runs.json"
)


def load_cost_extensions():
    feature = json.loads(FEATURE_INPUT.read_text(encoding="utf8"))
    trace = json.loads(TRACE_INPUT.read_text(encoding="utf8"))
    admission_grid = {
        (1, 1), (8, 1), (8, 4), (8, 8), (32, 1), (32, 4),
        (32, 32), (128, 1), (128, 4), (128, 128),
    }
    if len(feature["results"]) != 10 or {
        (r["fields"], r["changed"]) for r in feature["results"]
    } != admission_grid:
        raise ValueError("Equivalent admission grid is incomplete or duplicated")
    if feature["command_failures"] or feature["equivalence_verified_cells"] != 10:
        raise ValueError("Equivalent admission comparison failed its frozen checks")
    if any(not r["equivalence_verified"] or r["trials"] != 200 for r in feature["results"]):
        raise ValueError("Admission equivalence or trial count mismatch")
    trace_grid = {(f, v, r) for f in (1, 8, 32, 128)
                  for v in (1, 10, 100) for r in (1, 100, 1000)}
    if len(trace["results"]) != 36 or {
        (r["fields"], r["versions"], r["records"]) for r in trace["results"]
    } != trace_grid:
        raise ValueError("Trace comparison grid is incomplete or duplicated")
    if trace["command_failures"] or any(
        r["current_trials"] != 200 or r["baseline_trials"] != 200
        or not r["same_cell_and_trials"] or r["current_sql_statements"] != [12, 12]
        for r in trace["results"]
    ):
        raise ValueError("Trace comparison conditions differ from the frozen protocol")
    return feature, trace


def authority_operation_counts():
    rows = json.loads(RUNS_INPUT.read_text(encoding="utf8"))
    groups = {"admission_calls": [], "capability_checks": []}
    for row in rows:
        if not row["authority_evaluable"]:
            continue
        scenario = row["scenario_id"]
        if scenario in {f"A{i}" for i in range(2, 10)}:
            groups["admission_calls"].append(row)
        elif scenario in {"A1", "A10"}:
            groups["capability_checks"].append(row)
        else:
            raise ValueError(f"Unclassified authority-evaluable scenario: {scenario}")
    result = {}
    for group, items in groups.items():
        for row in items:
            derived = row["mechanism_actual_reject"] is False or (
                row["authority_digest_before"] != row["authority_digest_after"]
            )
            if row["unauthorized_authoritative_mutation"] != derived:
                raise ValueError("Authority label disagrees with verdict/digest evidence")
        result[group] = {
            "count": len(items),
            "violations": sum(row["unauthorized_authoritative_mutation"] for row in items),
            "per_configuration": {
                model: sum(row["model_config_id"] == model for row in items)
                for model in ("D1", "G1", "G2")
            },
        }
    if (result["admission_calls"]["count"], result["capability_checks"]["count"]) != (720, 179):
        raise ValueError("Frozen operation denominators changed")
    return result
