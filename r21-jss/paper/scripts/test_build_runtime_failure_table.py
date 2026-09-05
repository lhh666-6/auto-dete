"""Regression tests for the runtime-failure table generator.

The committed table must byte-for-byte equal a fresh rendering of the frozen
Final statistical_analysis.json, and its embedded source hash must match the
actual staged input.
"""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from build_runtime_failure_table import build_table

SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_DIR = SCRIPT_DIR.parent
STAGED_INPUT = (
    PAPER_DIR
    / "../evidence/agent-authority-benchmark-v2/manuscript-input/"
    / "2026-09-03-three-config-10x/statistical_analysis.json"
).resolve()
COMMITTED = PAPER_DIR / "tables/generated/runtime_failure_table.tex"


class RuntimeFailureTableTests(unittest.TestCase):
    def test_committed_table_matches_fresh_render(self) -> None:
        fresh = build_table(STAGED_INPUT)
        committed = COMMITTED.read_text(encoding="utf-8")
        self.assertEqual(fresh, committed)

    def test_embedded_source_hash_matches_staged_input(self) -> None:
        digest = hashlib.sha256(STAGED_INPUT.read_bytes()).hexdigest()
        committed = COMMITTED.read_text(encoding="utf-8")
        self.assertIn(f"source_sha256: {digest}", committed)

    def test_locked_totals_are_present(self) -> None:
        committed = COMMITTED.read_text(encoding="utf-8")
        for token in (
            "MODEL\\_API\\_FAILURE & 44 & 35 & 0 & 9",
            "INVALID\\_OUTPUT & 37 & 37 & 0 & 0",
            "HARNESS\\_FAILURE & 11 & 4 & 4 & 3",
            "TIMEOUT & 1 & 0 & 0 & 1",
            "Total & 93 & 76 & 4 & 13",
        ):
            self.assertIn(token, committed)

    def test_failure_class_sum_is_enforced(self) -> None:
        # A tampered input whose class counts no longer sum to runtime_failures
        # must be rejected by the generator's validation entry point.
        import json
        from build_runtime_failure_table import _load_and_validate

        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(STAGED_INPUT.read_text(encoding="utf-8"))
            data["primary"]["terminal_classes"]["MODEL_API_FAILURE"] += 1
            tampered = Path(tmp) / "statistical_analysis.json"
            tampered.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                _load_and_validate(tampered)


if __name__ == "__main__":
    unittest.main()
