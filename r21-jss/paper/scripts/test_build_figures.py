"""Regression tests for deterministic JSS figure construction."""

from __future__ import annotations

import json
import hashlib
import tempfile
import unittest
from html import unescape
from pathlib import Path

from build_figures import (
    build_all_figures,
    validate_agent_statistics,
    validate_cost_summary,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
COST_INPUT = (
    PACKAGE_ROOT
    / "evidence"
    / "final-rerun-paper"
    / "paper_inputs"
    / "cost_summary.json"
)
AGENT_STATS_INPUT = (
    PACKAGE_ROOT
    / "evidence"
    / "agent-authority-benchmark-v2"
    / "analysis"
    / "2026-09-05-recognition-semantic-audit"
    / "statistical_analysis_semantic.json"
)
APPROVED_WORKFLOW_PNG_SHA256 = (
    "1bf03fd87c9b10edad196f8ce703b93ec1ae9af6d80d03300160cc9b4de68eb7"
)


class FigureDataTests(unittest.TestCase):
    def test_frozen_agent_statistics_match_the_manuscript_contract(self) -> None:
        data = json.loads(AGENT_STATS_INPUT.read_text(encoding="utf-8"))

        stats = validate_agent_statistics(data)

        self.assertEqual(stats["planned_executions"], 1_260)
        self.assertEqual(stats["runtime_failures"], 93)
        self.assertEqual(stats["benign_completion"], (320, 335))
        self.assertEqual(stats["unauthorized_mutation"], (0, 899))
        self.assertAlmostEqual(stats["pooled_zero_event_upper"], 0.003326748034310656)
        self.assertEqual(
            stats["behavior_counts"],
            {
                "D1": ("101/108", "32/54", "18/24", "32/33"),
                "G1": ("114/119", "44/60", "29/30", "60/60"),
                "G2": ("105/108", "41/60", "28/28", "58/58"),
            },
        )

    def test_frozen_cost_grid_is_complete_and_unabridged(self) -> None:
        data = json.loads(COST_INPUT.read_text(encoding="utf-8"))

        stats = validate_cost_summary(data)

        self.assertEqual(stats["admission_cells"], 10)
        self.assertEqual(stats["admission_observations"], 2_000)
        self.assertEqual(stats["negative_delta_cells"], 2)
        self.assertAlmostEqual(stats["admission_p50_min_ms"], 16.5731)
        self.assertAlmostEqual(stats["admission_p50_max_ms"], 185.53185)
        self.assertAlmostEqual(stats["paired_delta_min_ms"], -5.7987845)
        self.assertAlmostEqual(stats["paired_delta_max_ms"], 160.680826)
        self.assertEqual(stats["trace_cells"], 36)
        self.assertEqual(stats["trace_observations"], 7_200)
        self.assertAlmostEqual(stats["trace_p50_min_ms"], 5.32725)
        self.assertAlmostEqual(stats["trace_p50_max_ms"], 7857.31275)
        self.assertAlmostEqual(stats["trace_p95_max_ms"], 8046.9595)
        self.assertEqual(stats["storage_populations"], 3)
        self.assertEqual(
            stats["storage_incremental_bytes"],
            [1_085_440, 10_772_480, 111_230_976],
        )

    def test_all_figures_export_editable_svg_vector_pdf_and_png(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir)
            manifest = build_all_figures(COST_INPUT, AGENT_STATS_INPUT, output_root)

            expected = {
                "vector/admission-workflow.svg",
                "vector/admission-workflow.pdf",
                "vector/admission-workflow.png",
                "vector/evidence-chain.svg",
                "vector/evidence-chain.pdf",
                "vector/evidence-chain.png",
                "generated/cost-characterization.svg",
                "generated/cost-characterization.pdf",
                "generated/cost-characterization.png",
                "generated/behavior-vs-authority.svg",
                "generated/behavior-vs-authority.pdf",
                "generated/behavior-vs-authority.png",
            }
            self.assertEqual(set(manifest["outputs"]), expected)
            for relative in expected:
                path = output_root / relative
                self.assertTrue(path.is_file(), relative)
                self.assertGreater(path.stat().st_size, 1_000, relative)

            for relative in [item for item in expected if item.endswith(".svg")]:
                svg = (output_root / relative).read_text(encoding="utf-8")
                self.assertIn("<text", svg, relative)
                self.assertNotIn("<image", svg, relative)

            for relative in [item for item in expected if item.endswith(".pdf")]:
                self.assertTrue((output_root / relative).read_bytes().startswith(b"%PDF"))

            self.assertEqual(manifest["source_sha256"], "705c4e647447d4aea8bf28f15f002d62ea80bee3f15aa4df4dc6ea79fb3fdd3b")
            self.assertEqual(manifest["data_stats"]["trace_cells"], 36)

    def test_redesigned_figures_expose_locked_semantics_and_panel_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir)
            build_all_figures(COST_INPUT, AGENT_STATS_INPUT, output_root)

            workflow = (output_root / "vector/admission-workflow.svg").read_text(encoding="utf-8")
            workflow_png = output_root / "vector/admission-workflow.png"
            self.assertEqual(
                hashlib.sha256(workflow_png.read_bytes()).hexdigest(),
                APPROVED_WORKFLOW_PNG_SHA256,
                "Figure 1 differs from the author-approved workflow artwork",
            )
            self.assertIn("Accept", workflow)
            self.assertIn("Correction", workflow)
            self.assertIn("x_a ≠ x_c", workflow)
            self.assertIn("candidate retained", workflow)
            self.assertIn("Reject", workflow)

            evidence = unescape(
                (output_root / "vector/evidence-chain.svg").read_text(encoding="utf-8")
            )
            self.assertIn("Abstraction → Characterization → Realization → Behavioral validation", evidence)
            self.assertIn(">C1<", evidence)
            self.assertIn("Correction-aware", evidence)
            self.assertIn("admission semantics", evidence)
            self.assertIn("x_c ≠ x_a under Correction", evidence)
            self.assertIn("C2 · Failure-distinguishability", evidence)
            self.assertIn("five information classes", evidence)
            self.assertIn("paired safe/unsafe histories", evidence)
            self.assertIn("C3 · Formal & transactional realization", evidence)
            self.assertIn("C4", evidence)
            self.assertIn("Admission-boundary", evidence)
            self.assertIn("Repeated live-agent", evidence)
            self.assertIn("evidence", evidence)
            self.assertIn("1,260 planned", evidence)
            self.assertIn("Runtime reliability: 93 failures", evidence)
            self.assertIn("reported separately", evidence)
            for provenance_stage in (
                "Frozen source",
                "Raw receipts",
                "Normalized inputs",
                "Final manifest",
            ):
                self.assertIn(provenance_stage, evidence)
            self.assertIn("Evidence lineage backbone", evidence)
            self.assertIn("conditional on the declared five failure families", evidence)
            self.assertIn("bounded / finite / implementation-specific", evidence)
            self.assertIn("executed benchmark population", evidence)

            cost = (output_root / "generated/cost-characterization.svg").read_text(encoding="utf-8")
            for title in (
                "Absolute admission latency",
                "Paired incremental latency",
                "Reverse-trace latency",
                "Storage scaling",
            ):
                self.assertIn(title, cost)

            behavior = (output_root / "generated/behavior-vs-authority.svg").read_text(encoding="utf-8")
            self.assertIn("Behavioral variation", behavior)
            self.assertIn("Authority outcome", behavior)
            self.assertIn("0/899", behavior)


if __name__ == "__main__":
    unittest.main()
