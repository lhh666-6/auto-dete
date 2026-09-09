from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import build_evidence_tables as builder


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT_ROOT = Path(__file__).resolve().parents[1]
INPUT_ROOT = PACKAGE_ROOT / "evidence" / "final-rerun-paper" / "paper_inputs"


class EvidenceTableTests(unittest.TestCase):
    def test_locked_input_set_is_exact(self) -> None:
        inputs = builder.load_inputs(INPUT_ROOT)
        self.assertEqual(set(inputs), builder.EXPECTED_INPUTS)

    def test_digest_preserves_locked_denominators_and_unfavorable_cells(self) -> None:
        digest = builder.build_digest(builder.load_inputs(INPUT_ROOT), INPUT_ROOT)

        self.assertEqual(digest["run"]["passed"], 10)
        self.assertEqual(digest["run"]["failed"], 0)
        self.assertEqual(digest["quality"]["python_tests"], 354)
        self.assertEqual(digest["quality"]["typed_source_files"], 52)
        self.assertEqual(digest["alloy"]["total"], 66)
        self.assertEqual(digest["alloy"]["profiles"]["S1"]["SAT"], 20)
        self.assertEqual(digest["alloy"]["profiles"]["S1"]["UNSAT"], 13)
        self.assertEqual(digest["alloy"]["profiles"]["S2"]["SAT"], 20)
        self.assertEqual(digest["alloy"]["profiles"]["S2"]["UNSAT"], 13)
        self.assertEqual(digest["refinement"], {"SAT": 9, "UNSAT": 20, "total": 29})
        self.assertEqual(digest["conformance"]["passed"], 35)
        self.assertEqual(digest["conformance"]["denominator"], 35)
        self.assertTrue(digest["lifecycle"]["complete"])
        self.assertEqual(digest["cost"]["admission"]["observations"], 2000)
        self.assertEqual(digest["cost"]["trace"]["observations"], 7200)
        self.assertEqual(digest["cost"]["admission"]["negative_delta_cells"], 2)
        self.assertEqual(
            digest["cost"]["storage"]["incremental_bytes"],
            [1_085_440, 10_772_480, 111_230_976],
        )

    def test_generator_writes_digest_and_all_declared_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir)
            builder.generate(INPUT_ROOT, output_root)

            expected = {
                "evidence_digest.json",
                "formal_evidence.tex",
                "validation_evidence.tex",
                "admission_cost.tex",
                "trace_storage_cost.tex",
            }
            self.assertEqual({path.name for path in output_root.iterdir()}, expected)

            digest = json.loads((output_root / "evidence_digest.json").read_text("utf-8"))
            self.assertEqual(digest["schema"], "auto-decte-jss-evidence-digest-v1")
            for table_name in expected - {"evidence_digest.json"}:
                table = (output_root / table_name).read_text("utf-8")
                self.assertIn("AUTO-GENERATED", table)
                self.assertIn("paper_inputs", table)
                self.assertNotIn("\n+", table)

    def test_missing_or_extra_input_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            for name in builder.EXPECTED_INPUTS:
                (temp_root / name).write_text("{}", encoding="utf-8")
            (temp_root / "unexpected.json").write_text("{}", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "unexpected.json"):
                builder.load_inputs(temp_root)

    def test_wide_generated_tables_use_width_safe_layout(self) -> None:
        inputs = builder.load_inputs(INPUT_ROOT)
        digest = builder.build_digest(inputs, INPUT_ROOT)

        formal = builder.render_formal_evidence(inputs, digest)
        admission = builder.render_admission_cost(inputs, digest)

        self.assertIn(r"\begin{tabularx}{\linewidth}", formal)
        self.assertNotIn(r"\begin{tabular}{lrrrrrr}", formal)
        self.assertIn(r">{\centering\arraybackslash}p{0.15\linewidth}", formal)
        self.assertIn(r"\footnotesize", admission)
        self.assertIn(r"\setlength{\tabcolsep}{5.5pt}", admission)

    def test_handwritten_wide_tables_use_width_safe_layout(self) -> None:
        main = (MANUSCRIPT_ROOT / "main.tex").read_text("utf-8")
        artifact = (MANUSCRIPT_ROOT / "artifact_appendix.tex").read_text("utf-8")
        contract = (MANUSCRIPT_ROOT / "sections" / "03-problem-contract.tex").read_text(
            "utf-8"
        )
        conformance = (
            MANUSCRIPT_ROOT / "sections" / "06-formal-concrete-conformance.tex"
        ).read_text("utf-8")

        self.assertIn(r"\usepackage{tabularx}", main)
        self.assertIn(r"\begin{tabularx}{\textwidth}", artifact)
        self.assertNotIn(r"\begin{tabular}{lll}", artifact)
        self.assertIn(r"\begin{tabularx}{\textwidth}", contract)
        self.assertIn(r"\begin{tabularx}{\textwidth}", conformance)
        self.assertIn(r"p{0.25\textwidth}", conformance)
        self.assertIn(r"p{0.29\textwidth}", conformance)


if __name__ == "__main__":
    unittest.main()
