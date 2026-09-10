from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from analyze_acknowledgment_annotation import (
    agreement_metrics,
    bootstrap_intervals,
    build_exact_text_index,
    load_and_join,
    run_analysis,
)


HERE = Path(__file__).resolve().parent
LATEST = HERE.parents[1]
WORKBOOK = HERE / "completed-blind-annotation.xlsx"
SOURCE_AUDIT = HERE / "frozen-semantic-audit-with-text.csv"
REPAIRED_AUDIT = (
    LATEST
    / "evidence"
    / "r3-audit-verified"
    / "recognition_semantic_audit_v2.csv"
)


class MetricTests(unittest.TestCase):
    def test_agreement_metrics_counts_all_four_cells(self) -> None:
        rows = [
            {"human_label": 0, "rule_label": 0},
            {"human_label": 1, "rule_label": 0},
            {"human_label": 0, "rule_label": 1},
            {"human_label": 1, "rule_label": 1},
        ]
        result = agreement_metrics(rows, "rule_label")
        self.assertEqual(result["n"], 4)
        self.assertEqual(result["rule_0_human_0"], 1)
        self.assertEqual(result["rule_0_human_1"], 1)
        self.assertEqual(result["rule_1_human_0"], 1)
        self.assertEqual(result["rule_1_human_1"], 1)
        self.assertEqual(result["agreement_count"], 2)
        self.assertAlmostEqual(result["percent_agreement"], 0.5)
        self.assertAlmostEqual(result["cohen_kappa"], 0.0)
        self.assertAlmostEqual(result["gwet_ac1"], 0.0)
        self.assertAlmostEqual(result["pabak"], 0.0)

    def test_duplicate_assistant_text_is_rejected(self) -> None:
        rows = [
            {"assistant_text": "same", "run_id": "one"},
            {"assistant_text": "same", "run_id": "two"},
        ]
        with self.assertRaisesRegex(ValueError, "duplicate normalized assistant_text"):
            build_exact_text_index(rows)


class FrozenDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = load_and_join(WORKBOOK, SOURCE_AUDIT, REPAIRED_AUDIT)

    def test_all_325_rows_join_once(self) -> None:
        self.assertEqual(len(self.rows), 325)
        self.assertEqual(len({row["case_id"] for row in self.rows}), 325)
        self.assertEqual(sum(row["human_label"] for row in self.rows), 241)
        self.assertEqual(sum(row["v2_label"] for row in self.rows), 272)

    def test_known_v2_headline_values(self) -> None:
        overall = agreement_metrics(self.rows, "v2_label")
        self.assertEqual(overall["agreement_count"], 286)
        self.assertEqual(overall["rule_0_human_0"], 49)
        self.assertEqual(overall["rule_0_human_1"], 4)
        self.assertEqual(overall["rule_1_human_0"], 35)
        self.assertEqual(overall["rule_1_human_1"], 237)
        self.assertAlmostEqual(overall["percent_agreement"], 0.88)
        self.assertAlmostEqual(overall["cohen_kappa"], 0.6441705735380815)

        expected = {"A2": (81, 86), "A3": (56, 88), "A6": (69, 69), "B4": (80, 82)}
        for scenario, (agree, denominator) in expected.items():
            subset = [row for row in self.rows if row["scenario_id"] == scenario]
            metrics = agreement_metrics(subset, "v2_label")
            self.assertEqual((metrics["agreement_count"], metrics["n"]), (agree, denominator))

    def test_bootstrap_is_deterministic(self) -> None:
        first = bootstrap_intervals(self.rows, "v2_label", "case", 50, 20260910)
        second = bootstrap_intervals(self.rows, "v2_label", "case", 50, 20260910)
        self.assertEqual(first, second)
        self.assertEqual(first["replicates"], 50)

    def test_run_analysis_writes_required_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            latex_table = output_dir / "acknowledgment_human_rule.tex"
            report = run_analysis(
                WORKBOOK,
                SOURCE_AUDIT,
                REPAIRED_AUDIT,
                output_dir,
                bootstrap_replicates=10,
                bootstrap_seed=20260910,
                latex_table_path=latex_table,
            )
            self.assertEqual(report["primary_comparison"]["overall"]["agreement_count"], 286)
            for filename in (
                "normalized-labels.csv",
                "agreement-summary.csv",
                "disagreements-v2.csv",
                "bootstrap-intervals.csv",
                "analysis-report.json",
                "analysis-report.md",
            ):
                self.assertTrue((output_dir / filename).is_file(), filename)
            latex = latex_table.read_text(encoding="utf-8")
            self.assertIn("Cohen's $\\kappa$", latex)
            self.assertIn("Rule 0/H 0", latex)
            self.assertIn("Case resampling", latex)
            self.assertIn("\\setlength{\\tabcolsep}{4pt}", latex)
            self.assertIn("\\begin{tabular}{@{}lrrrrrrr@{}}", latex)


if __name__ == "__main__":
    unittest.main()
