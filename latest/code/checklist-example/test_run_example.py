"""Tests for the Claude runner that completes Codex's fixed-case design.

These tests exercise the runner end to end in a temporary directory: the two
declared policies are driven through all nine fixed cases, the resulting
database files are inspected through fresh connections, and the derived table
is checked against the recorded outcomes.
"""

import json
from copy import deepcopy
import tempfile
import unittest
from pathlib import Path

try:
    import run_example
except ImportError:  # pragma: no cover - exercised only without the runner
    run_example = None


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "runs"
        cls.records, cls.summary = run_example.run_all(cls.out)
        cls.table = run_example.derive_table(cls.records)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def by_key(self, case_id, policy):
        for record in self.records:
            if record["case_id"] == case_id and record["policy"] == policy:
                return record
        raise KeyError((case_id, policy))

    def test_all_nine_cases_execute_and_meet_declared_expectations(self):
        self.assertEqual(self.summary["cases"], 9)
        self.assertEqual(self.summary["runs"], 18)
        self.assertTrue(self.summary["all_expected_outcomes_met"])

    def test_only_equal_value_substitution_diverges_in_outcome(self):
        self.assertEqual(
            self.summary["outcome_divergent_cases"], ["equal-value-substitution"])
        # the paired-history case has no single accept/reject outcome, so the
        # agreement list covers the seven remaining single-run cases
        self.assertEqual(len(self.summary["outcome_agreement_cases"]), 7)

    def test_rejection_controls_leave_the_post_approval_state_unchanged(self):
        for case_id in ("cross-record-candidate", "stale-version", "wrong-value",
                        "partial-batch", "injected-failure"):
            for policy in ("value_audit", "candidate_bound"):
                record = self.by_key(case_id, policy)
                self.assertFalse(record["observed"]["accepted"], (case_id, policy))
                self.assertTrue(record["state_unchanged"], (case_id, policy))

    def test_paired_history_separates_the_two_policies(self):
        self.assertEqual(
            self.summary["paired_history_states_equal"],
            {"value_audit": True, "candidate_bound": False})
        cb = self.by_key("paired-reviewed-candidate", "candidate_bound")
        self.assertEqual(cb["observations"]["differing_tables"], ["approvals"])
        self.assertTrue(cb["observations"]["reviewed_candidate_persisted"])

    def test_copy_forward_sources_are_reconstructed_in_both_arms(self):
        expected = {"quantity": "v1:quantity", "batch": "v2:batch"}
        for policy in ("value_audit", "candidate_bound"):
            record = self.by_key("two-step-copy-forward", policy)
            self.assertEqual(record["observations"]["reconstructed_sources"], expected)
        cb = self.by_key("two-step-copy-forward", "candidate_bound")
        self.assertEqual(cb["observations"]["stored_sources"], expected)
        self.assertTrue(cb["observations"]["stored_matches_reconstruction"])
        va = self.by_key("two-step-copy-forward", "value_audit")
        self.assertIsNone(va["observations"]["stored_sources"])

    def test_candidate_bound_reconstructs_both_value_roles_by_join(self):
        cb = self.by_key("legal-correction", "candidate_bound")
        dual = cb["observations"]["dual_value"]
        self.assertTrue(dual["proposal_reconstructable_by_join"])
        self.assertEqual(dual["proposed_value"], {"quantity": 100})
        self.assertEqual(dual["authorized_value"], {"quantity": 101})
        va = self.by_key("legal-correction", "value_audit")
        dual_va = va["observations"]["dual_value"]
        self.assertFalse(dual_va["proposal_reconstructable_by_join"])
        self.assertIsNone(dual_va["proposed_value"])

    def test_raw_inspection_uses_a_fresh_connection(self):
        record = self.by_key("legal-correction", "candidate_bound")
        state = run_example.raw_state(Path(self.out) / record["database_file"])
        records = run_example.rows_as_dicts(state, "records")
        self.assertEqual(records[0]["version"], 1)
        self.assertEqual(json.loads(records[0]["values_json"]),
                         {"quantity": 101, "batch": "A"})
        self.assertEqual(len(state["triggers"]), 8)

    def test_every_record_carries_action_snapshots_and_database_file(self):
        for record in self.records:
            self.assertIn("requested_action", record)
            self.assertTrue(record["database_file"])
            if "runs" in record:
                for run in record["runs"].values():
                    self.assertIn("state", run)
            else:
                self.assertIn("pre_state", record)
                self.assertIn("post_state", record)

    def test_derived_table_covers_every_case_and_marks_divergences(self):
        for spec in run_example.CASE_SPECS.values():
            self.assertIn(spec["label"], self.table)
        self.assertEqual(self.table.count(r"$^\dagger$"), 1)
        self.assertEqual(self.table.count(r"$^\ddagger$"), 1)
        self.assertIn(r"\code{candidate_binding}", self.table)

    def test_runner_refuses_to_overwrite_a_database(self):
        path = Path(self.out) / "db" / "legal-correction__value_audit.db"
        with self.assertRaises(FileExistsError):
            run_example.Demo(path, "value_audit")

    def test_runner_itself_refuses_existing_output_before_modifying_files(self):
        path = self.out / "runs.json"
        before = path.read_bytes()
        with self.assertRaises(FileExistsError):
            run_example.run_all(self.out)
        self.assertEqual(path.read_bytes(), before)

    def test_checker_rejects_failed_paired_branch_even_if_states_match(self):
        records = deepcopy(self.records)
        pair = next(r for r in records if r["case_id"] == "paired-reviewed-candidate")
        pair["runs"]["q100a"]["observed"]["accepted"] = False
        with self.assertRaises(AssertionError):
            run_example.check_expected_outcomes(records)

    def test_checker_rejects_incorrect_legal_successor(self):
        records = deepcopy(self.records)
        legal = next(r for r in records if r["case_id"] == "legal-correction")
        legal["observations"]["successor_values"]["quantity"] = 999
        with self.assertRaises(AssertionError):
            run_example.check_expected_outcomes(records)

    def test_checker_rejects_duplicate_records(self):
        records = deepcopy(self.records)
        records.append(deepcopy(records[0]))
        with self.assertRaises(AssertionError):
            run_example.check_expected_outcomes(records)

    def test_checker_rejects_failed_first_step_of_copy_forward(self):
        records = deepcopy(self.records)
        record = next(r for r in records if r["case_id"] == "two-step-copy-forward")
        record["observations"]["first_step_accepted"] = False
        with self.assertRaises(AssertionError):
            run_example.check_expected_outcomes(records)


if __name__ == "__main__":
    unittest.main()
