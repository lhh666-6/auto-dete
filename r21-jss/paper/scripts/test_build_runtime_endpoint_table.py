from pathlib import Path
import tempfile
import unittest

from build_runtime_endpoint_table import analyze, build_table


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
RUNS = (
    PACKAGE_ROOT
    / "evidence/agent-authority-benchmark-v2/final/2026-09-01-three-config-10x/normalized/runs.json"
)
COMMITTED = PACKAGE_ROOT / "paper/tables/generated/runtime_endpoint_table.tex"


class RuntimeEndpointTableTests(unittest.TestCase):
    def test_cross_counts_match_frozen_rows(self) -> None:
        result = analyze(RUNS)
        self.assertEqual(result["total"], 93)
        self.assertEqual(result["authority_evaluable"], 64)
        self.assertEqual(result["behavior_evaluable"], 3)
        self.assertEqual(result["behavior_false"], 3)

    def test_committed_table_matches_render(self) -> None:
        self.assertEqual(COMMITTED.read_text(encoding="utf-8"), build_table(RUNS))

    def test_tampered_population_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runs.json"
            path.write_text("[]", encoding="utf-8")
            with self.assertRaises(ValueError):
                analyze(path)


if __name__ == "__main__":
    unittest.main()
