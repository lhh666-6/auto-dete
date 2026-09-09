"""Build and verify the three separately manifested R21 paper inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPRODUCED = ROOT / "evidence" / "reproduced" / "r21"
INPUTS = ROOT / "evidence" / "paper-inputs"
MANIFEST = ROOT / "evidence" / "r21-paper-input-manifest.json"
TABLES = ROOT / "paper" / "tables" / "generated"


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def _encode(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _live_input() -> dict[str, Any]:
    root = REPRODUCED / "live-agent-run-4"
    receipt = _read(root / "receipt.json")
    metadata = _read(root / "run_metadata.json")
    scenarios = []
    token_totals = {
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "reasoning_output_tokens": 0,
    }
    transport_errors = 0
    for outcome in receipt["scenarios"]:
        scenario_id = outcome["scenario_id"]
        parsed = _read(root / "scenarios" / scenario_id / "parsed.json")
        usage = parsed.get("usage", {})
        for key in token_totals:
            token_totals[key] += int(usage.get(key, 0))
        transport_errors += len(parsed.get("transport_errors", []))
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "kind": outcome["kind"],
                "tool_names": outcome["tool_names"],
                "tool_completion": outcome["tool_completion"],
                "authority_safety": outcome["authority_safety"],
                "passed": outcome["passed"],
                "codex_returncode": outcome["codex_returncode"],
                "post_fact_version": outcome["post_fact_version"],
                "digest_unchanged": outcome["before_digest"] == outcome["after_digest"],
                "verification": outcome.get("verification"),
                "host_confirmation": outcome.get("host_confirmation"),
                "reported_unavailable": outcome.get("reported_unavailable"),
            }
        )
    return {
        "schema": "auto-decte.r21-live-agent-paper-input.v1",
        "requested_model": metadata["requested_model"],
        "codex_version": metadata["codex_version"],
        "reasoning_effort": metadata["model_reasoning_effort"],
        "enabled_tools": metadata["enabled_tools"],
        "approval_policy": metadata["approval_policy"],
        "mcp_tools_approval_mode": metadata["mcp_default_tools_approval_mode"],
        "sandbox": metadata["sandbox"],
        "denominator": receipt["denominator"],
        "tool_completion_count": receipt["tool_completion_count"],
        "authority_safety_count": receipt["authority_safety_count"],
        "passed_count": receipt["passed_count"],
        "all_passed": receipt["all_passed"],
        "sources_unchanged_during_run": receipt["sources_unchanged_during_run"],
        "raw_events_modified": False,
        "authority_receipts_modified": False,
        "token_totals": token_totals,
        "transport_error_events": transport_errors,
        "scenarios": scenarios,
    }


def _feature_input() -> dict[str, Any]:
    root = REPRODUCED / "feature-baseline-run-1"
    receipt = _read(root / "receipt.json")
    summary = _read(root / "feature_baseline_summary.json")
    return {
        "schema": "auto-decte.r21-feature-baseline-paper-input.v1",
        "status": receipt["status"],
        "command_failures": receipt["command_failures"],
        "config": receipt["config"],
        "environment": receipt["environment"],
        "cells": receipt["cells"],
        "observations": receipt["observations"],
        "equivalence_verified_cells": receipt["equivalence_verified_cells"],
        "comparison": summary["comparison"],
        "results": summary["cells"],
    }


def _trace_input() -> dict[str, Any]:
    root = REPRODUCED / "trace-optimization-comparison-3"
    receipt = _read(root / "receipt.json")
    summary = _read(root / "trace_optimization_summary.json")
    return {
        "schema": "auto-decte.r21-trace-optimization-paper-input.v1",
        "status": receipt["status"],
        "command_failures": receipt["command_failures"],
        "baseline_observations": receipt["baseline_observations"],
        "current_observations": receipt["current_observations"],
        "cells": receipt["cells"],
        "statement_budget": receipt["statement_budget"],
        "baseline_sha256": receipt["baseline_sha256"],
        "config_sha256": receipt["config_sha256"],
        "comparison_only": receipt["comparison_only"],
        "current_measurement_source_sha256": receipt[
            "current_measurement_source_sha256"
        ],
        "current_measurement_receipt_sha256": receipt[
            "current_measurement_receipt_sha256"
        ],
        "environment": receipt["environment"],
        "comparison": summary["comparison"],
        "complexity": summary["complexity"],
        "results": summary["cells"],
    }


def generated() -> dict[Path, bytes]:
    return {
        INPUTS / "r21_live_agent_summary.json": _encode(_live_input()),
        INPUTS / "r21_feature_baseline_summary.json": _encode(_feature_input()),
        INPUTS / "r21_trace_optimization_summary.json": _encode(_trace_input()),
    }


def generated_tables() -> dict[Path, bytes]:
    feature = _feature_input()["results"]
    feature_rows = "\n".join(
        f"{cell['fields']:<3} & {cell['changed']:<3} & "
        f"{cell['full_p50_ms']:.3f} & {cell['materialization_p50_ms']:.3f} & "
        f"{cell['paired_mean_validation_and_planning_delta_ms']:.3f} \\\\"
        for cell in feature
    )
    feature_text = f"""\\begin{{table}}[t]
\\centering
\\caption{{Full admission versus prevalidated, relationally equivalent materialization (milliseconds; 200 pairs per cell). Every materialized post-state matched its full-admission reference fingerprint.}}
\\label{{tab:feature-baseline}}
\\small
\\begin{{tabular}}{{rrrrr}}
\\toprule
Fields & Changed & Full p50 & Materialization p50 & Mean paired delta \\\\
\\midrule
{feature_rows}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""

    trace = _trace_input()["results"]
    wanted = {(1, 1, 1), (8, 10, 1), (32, 100, 1), (128, 100, 1000)}
    selected = [
        cell
        for cell in trace
        if (cell["fields"], cell["versions"], cell["records"]) in wanted
    ]
    trace_rows = "\n".join(
        f"{cell['fields']} & {cell['versions']} & {cell['records']} & "
        f"{cell['baseline_p50_ms']:.3f} & {cell['current_p50_ms']:.3f} & "
        f"{cell['baseline_sql_statements'][0]} & {cell['current_sql_statements'][0]} \\\\"
        for cell in selected
    )
    trace_text = f"""\\begin{{table}}[t]
\\centering
\\caption{{Representative cells from the reverse-trace optimization. Latencies are p50 milliseconds; SQL is the fixed statement count in every trial of the cell.}}
\\label{{tab:trace-optimization}}
\\footnotesize
\\begin{{tabular*}}{{\\linewidth}}{{@{{\\extracolsep{{\\fill}}}}rrrrrrr@{{}}}}
\\toprule
Fields & Versions & Records & Base p50 & Opt. p50 & Base SQL & Opt. SQL \\\\
\\midrule
{trace_rows}
\\bottomrule
\\end{{tabular*}}
\\end{{table}}
"""
    return {
        TABLES / "feature_baseline_cost.tex": feature_text.encode("utf-8"),
        TABLES / "trace_optimization.tex": trace_text.encode("utf-8"),
    }


def _manifest(outputs: dict[Path, bytes]) -> dict[str, Any]:
    live_root = REPRODUCED / "live-agent-run-4"
    source_paths = [
        ROOT / "scripts" / "build_r21_inputs.py",
        REPRODUCED / "feature-baseline-run-1" / "receipt.json",
        REPRODUCED / "feature-baseline-run-1" / "feature_baseline_summary.json",
        REPRODUCED / "feature-baseline-run-1" / "raw.json",
        REPRODUCED / "trace-optimization-comparison-3" / "receipt.json",
        REPRODUCED / "trace-optimization-comparison-3" / "trace_optimization_summary.json",
        REPRODUCED / "trace-optimization-comparison-3" / "baseline.json",
        REPRODUCED / "trace-optimization-comparison-3" / "raw.json",
        REPRODUCED / "trace-optimization-run-2" / "receipt.json",
        ROOT / "source" / "performance-experiment" / "config" / "r21-feature-baseline.json",
        ROOT / "source" / "performance-experiment" / "config" / "r21-trace-optimization.json",
        ROOT / "source" / "performance-experiment" / "benchmarks" / "r21_feature_baseline.py",
        ROOT / "source" / "performance-experiment" / "benchmarks" / "r21_trace_optimization.py",
        ROOT / "source" / "performance-experiment" / "benchmarks" / "authority_cost.py",
        ROOT / "source" / "implementation" / "app" / "application" / "query_forms.py",
        ROOT / "source" / "implementation" / "app" / "adapters" / "database" / "repositories.py",
        ROOT / "source" / "implementation" / "app" / "integrations" / "dsh_bridge.py",
        ROOT / "source" / "implementation" / "tests" / "conformance" / "oracle.py",
        ROOT / "source" / "implementation" / "tests" / "integration" / "test_dsh_bridge.py",
        ROOT / "source" / "implementation" / "tests" / "integration" / "test_query_and_trace.py",
        ROOT / "source" / "implementation" / "tests" / "benchmarks" / "test_authority_cost.py",
        ROOT / "source" / "live-agent-experiment" / "auto_decte_live_agent" / "experiment.py",
        ROOT / "source" / "live-agent-experiment" / "auto_decte_live_agent" / "runner.py",
        ROOT / "source" / "live-agent-experiment" / "auto_decte_live_agent" / "server.py",
        ROOT / "source" / "live-agent-experiment" / "auto_decte_live_agent" / "state_probe.py",
        ROOT / "source" / "live-agent-experiment" / "pyproject.toml",
        ROOT / "source" / "live-agent-experiment" / "uv.lock",
    ]
    source_paths.extend(
        path
        for path in (ROOT / "source" / "live-agent-experiment" / "tests").glob("test_*.py")
        if path.is_file()
    )
    source_paths.extend(path for path in live_root.rglob("*") if path.is_file())
    source_paths = sorted(set(source_paths), key=lambda path: path.relative_to(ROOT).as_posix())
    table_outputs = generated_tables()
    return {
        "schema": "auto-decte.r21-paper-input-manifest.v1",
        "algorithm": "sha256",
        "non_self_referential": True,
        "paper_inputs": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": len(content),
                "sha256": _sha256_bytes(content),
            }
            for path, content in sorted(outputs.items())
        ],
        "generated_tables": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": len(content),
                "sha256": _sha256_bytes(content),
            }
            for path, content in sorted(table_outputs.items())
        ],
        "source_evidence": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            for path in source_paths
        ],
    }


def build() -> None:
    outputs = generated()
    tables = generated_tables()
    INPUTS.mkdir(parents=True, exist_ok=True)
    for path, content in {**outputs, **tables}.items():
        path.write_bytes(content)
    MANIFEST.write_bytes(_encode(_manifest(outputs)))


def verify() -> list[str]:
    failures: list[str] = []
    outputs = generated()
    tables = generated_tables()
    for path, expected in {**outputs, **tables}.items():
        if not path.is_file():
            failures.append(f"missing:{path.relative_to(ROOT).as_posix()}")
        elif path.read_bytes() != expected:
            failures.append(f"content:{path.relative_to(ROOT).as_posix()}")
    expected_manifest = _encode(_manifest(outputs))
    if not MANIFEST.is_file():
        failures.append(f"missing:{MANIFEST.relative_to(ROOT).as_posix()}")
    elif MANIFEST.read_bytes() != expected_manifest:
        failures.append(f"content:{MANIFEST.relative_to(ROOT).as_posix()}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("build", "verify"))
    args = parser.parse_args()
    if args.operation == "build":
        build()
    failures = verify()
    print(json.dumps({"verified": not failures, "failures": failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
