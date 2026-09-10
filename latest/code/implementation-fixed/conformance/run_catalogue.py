"""Execute the finite R9 catalogue and retain one raw JSON record per case."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sqlite3
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine  # noqa: E402

from tests.conformance.oracle import (  # noqa: E402
    canonical_database_state,
    relational_authority_violations,
    state_digest,
)

CATALOGUE = ROOT / "conformance" / "case_catalogue.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _row_evidence(database: Path) -> dict[str, object]:
    engine = create_engine(f"sqlite:///{database}")
    try:
        state = canonical_database_state(engine)
    finally:
        engine.dispose()
    tables = state["tables"]
    assert isinstance(tables, dict)
    row_counts = {table: len(rows) for table, rows in tables.items()}
    row_ids: dict[str, list[dict[str, object]]] = {}
    for table, rows in tables.items():
        identities: list[dict[str, object]] = []
        for row in rows:
            identity = {
                key: value for key, value in row.items() if key == "key" or key.endswith("_id")
            }
            if identity:
                identities.append(identity)
        row_ids[table] = identities
    form_rows = tables.get("forms", [])
    trace_details = {
        str(row["form_id"]): list(relational_authority_violations(state, str(row["form_id"])))
        for row in form_rows
    }
    return {
        "path": database.relative_to(ROOT).as_posix()
        if database.is_relative_to(ROOT)
        else database.name,
        "sha256": _sha256(database),
        "state_digest": state_digest(state),
        "user_version": state["user_version"],
        "row_counts": row_counts,
        "row_ids": row_ids,
        "independent_trace_violations": trace_details,
    }


def _environment() -> dict[str, object]:
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "sqlite": sqlite3.sqlite_version,
        "sqlalchemy": importlib.metadata.version("sqlalchemy"),
        "pytest": importlib.metadata.version("pytest"),
        "hypothesis": importlib.metadata.version("hypothesis"),
    }


def run_catalogue(output: Path, selected_case: str | None = None) -> int:
    if output.exists():
        raise FileExistsError(f"output directory already exists: {output}")
    output.mkdir(parents=True)
    case_output = output / "cases"
    temp_root = output / "pytest-temp"
    case_output.mkdir()
    temp_root.mkdir()

    payload = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    cases = payload["cases"]
    if selected_case is not None:
        cases = [case for case in cases if case["id"] == selected_case]
        if not cases:
            raise KeyError(f"unknown case id: {selected_case}")
    environment = _environment()
    results: list[dict[str, object]] = []
    for case in cases:
        case_id = case["id"]
        case_temp = temp_root / case_id
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            case["node_id"],
            "-q",
            "--basetemp",
            str(case_temp),
        ]
        started = datetime.now(UTC)
        monotonic_start = time.monotonic()
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        finished = datetime.now(UTC)
        databases = [_row_evidence(database) for database in sorted(case_temp.rglob("*.db"))]
        result = {
            "schema": "auto-decte-catalogue-case-result-v1",
            "case": case,
            "command": command,
            "started_at": started.isoformat(),
            "finished_at": finished.isoformat(),
            "duration_seconds": round(time.monotonic() - monotonic_start, 6),
            "return_code": completed.returncode,
            "observed_status": "PASS" if completed.returncode == 0 else "FAIL",
            "expected_status_asserted_by_test": case["expected_status"],
            "digest_expectation_asserted_by_test": case["digest_expectation"],
            "databases": databases,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "environment": environment,
            "catalogue_sha256": _sha256(CATALOGUE),
            "test_source_sha256": _sha256(ROOT / case["node_id"].split("::", 1)[0]),
        }
        result_path = case_output / f"{case_id}.json"
        result_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        results.append(
            {
                "case_id": case_id,
                "result_sha256": _sha256(result_path),
                "return_code": completed.returncode,
            }
        )

    summary = {
        "schema": "auto-decte-catalogue-run-v1",
        "catalogue_version": payload["catalogue_version"],
        "declared_denominator": payload["denominator"],
        "executed_denominator": len(results),
        "selected_case": selected_case,
        "passed": sum(result["return_code"] == 0 for result in results),
        "failed": sum(result["return_code"] != 0 for result in results),
        "catalogue_sha256": _sha256(CATALOGUE),
        "environment": environment,
        "results": results,
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0 if summary["failed"] == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case")
    args = parser.parse_args()
    output = args.output.resolve()
    return run_catalogue(output, args.case)


if __name__ == "__main__":
    raise SystemExit(main())
