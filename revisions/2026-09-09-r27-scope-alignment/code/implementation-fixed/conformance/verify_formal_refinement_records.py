"""Verify the active R2 projection freeze and every recorded Alloy receipt."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    conformance_root = Path(__file__).resolve().parent
    freeze_id = (
        (conformance_root / "ACTIVE_REFINEMENT_FREEZE.txt").read_text(encoding="ascii").strip()
    )
    if not freeze_id or any(
        char not in "-._abcdefghijklmnopqrstuvwxyz0123456789" for char in freeze_id.lower()
    ):
        raise RuntimeError("invalid active refinement freeze id")
    freeze_root = conformance_root / "raw-results" / freeze_id
    manifest = json.loads((freeze_root / "manifest.json").read_text(encoding="utf-8"))
    if manifest["freeze_id"] != freeze_id:
        raise RuntimeError("active marker and manifest freeze id differ")
    rows = manifest["cases"]
    if len(rows) != manifest["case_count"]:
        raise RuntimeError("manifest case count differs from row count")
    if len({row["case"] for row in rows}) != len(rows):
        raise RuntimeError("manifest contains duplicate case paths")

    sat_count = 0
    unsat_count = 0
    for row in rows:
        case_root = freeze_root / row["case"]
        projection_path = case_root / "projection.json"
        wrapper_path = case_root / "concrete_projection.als"
        receipt_path = case_root / "alloy-result" / "receipt.json"
        expected_hashes = {
            projection_path: row["projection_sha256"],
            wrapper_path: row["wrapper_sha256"],
            receipt_path: row["receipt_sha256"],
        }
        for path, expected in expected_hashes.items():
            if not path.is_file():
                raise RuntimeError(f"missing refinement artifact: {path}")
            if _sha256(path) != expected:
                raise RuntimeError(f"refinement artifact hash mismatch: {path}")

        projection = json.loads(projection_path.read_text(encoding="utf-8"))
        if projection["outcome"] != row["projection_outcome"]:
            raise RuntimeError(f"projection outcome mismatch: {row['case']}")
        wrapper = wrapper_path.read_text(encoding="utf-8")
        if "open auto_decte_batch" not in wrapper:
            raise RuntimeError(f"wrapper does not open batch model: {row['case']}")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        command = receipt["commands"]["ConcreteRefinement"]
        actual = "SAT" if command.get("solution") else "UNSAT"
        if actual != row["alloy_outcome"]:
            raise RuntimeError(f"receipt outcome mismatch: {row['case']}")
        if actual == "SAT":
            sat_count += 1
        else:
            unsat_count += 1

    if sat_count != manifest["sat_count"] or unsat_count != manifest["unsat_count"]:
        raise RuntimeError("manifest SAT/UNSAT totals differ from receipts")
    if (sat_count, unsat_count) != (9, 20):
        raise RuntimeError("active R2 freeze must contain 9 SAT and 20 UNSAT cases")
    print(
        f"FORMAL_REFINEMENT_VERIFY_PASS {freeze_id} "
        f"CASES={len(rows)} SAT={sat_count} UNSAT={unsat_count}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"FORMAL_REFINEMENT_VERIFY_FAIL {error}", file=sys.stderr)
        raise
