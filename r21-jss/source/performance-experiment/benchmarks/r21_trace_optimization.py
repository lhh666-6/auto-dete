"""R21 reverse-trace rerun against the frozen pre-optimization observations."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import sqlite3
import statistics
import sys
from pathlib import Path
from typing import Any

from benchmarks.authority_cost import _percentile, _trace_experiment


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _key(row: dict[str, Any]) -> tuple[int, int, int]:
    return int(row["fields"]), int(row["versions"]), int(row["records"])


def _group(rows: list[dict[str, Any]]) -> dict[tuple[int, int, int], list[dict[str, Any]]]:
    grouped: dict[tuple[int, int, int], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(_key(row), []).append(row)
    return grouped


def _summarize(
    baseline_rows: list[dict[str, Any]], current_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    baseline = _group(baseline_rows)
    current = _group(current_rows)
    if set(baseline) != set(current):
        raise ValueError("baseline and current trace grids differ")
    cells = []
    for fields, versions, records in sorted(baseline):
        old_rows = baseline[(fields, versions, records)]
        new_rows = current[(fields, versions, records)]
        old_ms = [float(row["latency_ns"]) / 1e6 for row in old_rows]
        new_ms = [float(row["latency_ns"]) / 1e6 for row in new_rows]
        old_statements = [int(row["sql_statements"]) for row in old_rows]
        new_statements = [int(row["sql_statements"]) for row in new_rows]
        old_p50 = statistics.median(old_ms)
        new_p50 = statistics.median(new_ms)
        cells.append(
            {
                "fields": fields,
                "versions": versions,
                "records": records,
                "baseline_trials": len(old_rows),
                "current_trials": len(new_rows),
                "same_cell_and_trials": len(old_rows) == len(new_rows),
                "baseline_p50_ms": old_p50,
                "baseline_p95_ms": _percentile(old_ms, 0.95),
                "current_p50_ms": new_p50,
                "current_p95_ms": _percentile(new_ms, 0.95),
                "p50_speedup": old_p50 / new_p50,
                "baseline_sql_statements": [min(old_statements), max(old_statements)],
                "current_sql_statements": [min(new_statements), max(new_statements)],
            }
        )
    return {
        "schema_version": 1,
        "comparison": "frozen_preoptimization_vs_form_scoped_snapshot",
        "complexity": {
            "database_round_trips": "constant in versions and fields (12 in this implementation)",
            "in_memory_work": "O(V*F + T + C + E)",
            "symbols": {
                "V": "selected history versions",
                "F": "declared fields",
                "T": "form transitions",
                "C": "form certificates",
                "E": "form evidence rows",
            },
        },
        "cells": cells,
    }


def run_trace_optimization(
    config_path: Path, baseline_path: Path, output: Path
) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError(output)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1 or baseline.get("schema_version") != 1:
        raise ValueError("unsupported trace experiment schema")
    output.mkdir(parents=True)
    shutil.copy2(baseline_path, output / "baseline.json")
    current = _trace_experiment(config)
    baseline_rows = baseline.get("observations", [])
    current_rows = current.get("observations", [])
    summary = _summarize(baseline_rows, current_rows)
    if not all(cell["same_cell_and_trials"] for cell in summary["cells"]):
        raise ValueError("baseline and current trial counts differ")
    if any(int(row["sql_statements"]) > 12 for row in current_rows):
        raise RuntimeError("optimized trace exceeded the locked 12-statement budget")
    _write_json(output / "raw.json", current)
    _write_json(output / "trace_optimization_summary.json", summary)
    receipt = {
        "schema_version": 1,
        "status": "complete",
        "command_failures": 0,
        "baseline_observations": len(baseline_rows),
        "current_observations": len(current_rows),
        "cells": len(summary["cells"]),
        "statement_budget": 12,
        "baseline_sha256": _sha256(baseline_path),
        "config_sha256": _sha256(config_path),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "sqlite": sqlite3.sqlite_version,
        },
    }
    _write_json(output / "receipt.json", receipt)
    return receipt


def recompare_existing(
    config_path: Path,
    baseline_path: Path,
    current_run: Path,
    output: Path,
) -> dict[str, Any]:
    """Bind an existing clean measurement to the paper's exact baseline execution."""
    if output.exists():
        raise FileExistsError(output)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    current_path = current_run / "raw.json"
    current_receipt_path = current_run / "receipt.json"
    current = json.loads(current_path.read_text(encoding="utf-8"))
    current_receipt = json.loads(current_receipt_path.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise ValueError("unsupported trace experiment config")
    summary = _summarize(baseline["observations"], current["observations"])
    if not all(cell["same_cell_and_trials"] for cell in summary["cells"]):
        raise ValueError("baseline and current trial counts differ")
    if any(int(row["sql_statements"]) > 12 for row in current["observations"]):
        raise RuntimeError("optimized trace exceeded the locked 12-statement budget")
    output.mkdir(parents=True)
    shutil.copy2(baseline_path, output / "baseline.json")
    shutil.copy2(current_path, output / "raw.json")
    _write_json(output / "trace_optimization_summary.json", summary)
    receipt = {
        "schema_version": 1,
        "status": "complete",
        "command_failures": 0,
        "comparison_only": True,
        "baseline_observations": len(baseline["observations"]),
        "current_observations": len(current["observations"]),
        "cells": len(summary["cells"]),
        "statement_budget": 12,
        "baseline_sha256": _sha256(baseline_path),
        "config_sha256": _sha256(config_path),
        "current_measurement_source_sha256": _sha256(current_path),
        "current_measurement_receipt_sha256": _sha256(current_receipt_path),
        "current_measurement_source": str(current_run.resolve()),
        "environment": current_receipt["environment"],
    }
    _write_json(output / "receipt.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_trace_optimization(args.config, args.baseline, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
