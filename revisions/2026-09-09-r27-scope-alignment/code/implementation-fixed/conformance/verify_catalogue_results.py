"""Verify the retained R9 finite-catalogue development run."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(run: Path) -> None:
    catalogue = ROOT / "conformance" / "case_catalogue.json"
    declared = json.loads(catalogue.read_text(encoding="utf-8"))
    summary_path = run / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary["catalogue_sha256"] != _sha256(catalogue):
        raise ValueError("catalogue hash mismatch")
    if summary["executed_denominator"] != declared["denominator"]:
        raise ValueError("executed denominator mismatch")
    if summary["passed"] != declared["denominator"] or summary["failed"] != 0:
        raise ValueError("catalogue run is not fully passing")
    declared_ids = {case["id"] for case in declared["cases"]}
    result_ids = {result["case_id"] for result in summary["results"]}
    if result_ids != declared_ids:
        raise ValueError("case result ids do not equal the declared denominator")
    for result in summary["results"]:
        case_path = run / "cases" / f"{result['case_id']}.json"
        if _sha256(case_path) != result["result_sha256"]:
            raise ValueError(f"case result hash mismatch: {result['case_id']}")
        payload = json.loads(case_path.read_text(encoding="utf-8"))
        if payload["return_code"] != 0 or payload["observed_status"] != "PASS":
            raise ValueError(f"case did not pass: {result['case_id']}")
        for database in payload["databases"]:
            required = {
                "state_digest",
                "row_counts",
                "row_ids",
                "independent_trace_violations",
            }
            if not required <= set(database):
                raise ValueError(f"database evidence incomplete: {result['case_id']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    verify(args.run.resolve())
    print("catalogue verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
