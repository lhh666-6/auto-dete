"""Black-box behavior contracts for the deliberately specified two-arm example."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

try:
    from value_audit_demo import Demo
except ImportError:
    Demo = None


def persisted(path):
    with sqlite3.connect(path) as con:
        names = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {name: con.execute(f'SELECT * FROM "{name}" ORDER BY rowid').fetchall()
                for name in names}


class DemoTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Demo, "Executable comparison has not been implemented")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def make(self, policy, suffix=""):
        obj = Demo(Path(self.tmp.name) / f"{policy}{suffix}.db", policy)
        self.addCleanup(obj.close)
        return obj

    def approve_quantity(self, obj, candidate="q100a"):
        obj.approve("review-1", {"quantity": candidate}, {"quantity": 101})

    def test_legal_correction_keeps_candidate_and_complete_successor(self):
        for policy in ("value_audit", "candidate_bound"):
            obj = self.make(policy)
            self.approve_quantity(obj)
            result = obj.submit("review-1", {"quantity": "q100a"}, {"quantity": 101})
            self.assertTrue(result["accepted"])
            state = persisted(obj.path)
            self.assertEqual(json.loads(state["records"][0][2]), {"quantity": 101, "batch": "A"})
            self.assertEqual(next(r[3] for r in state["candidates"] if r[0] == "q100a"), "100")
            self.assertEqual(len(state["audits"]), 1)

    def test_same_context_equal_value_substitution_separates_arms(self):
        for policy in ("value_audit", "candidate_bound"):
            obj = self.make(policy)
            self.approve_quantity(obj)
            before = persisted(obj.path)
            result = obj.submit("review-1", {"quantity": "q100b"}, {"quantity": 101})
            self.assertEqual(result["accepted"], policy == "value_audit")
            if policy == "candidate_bound":
                self.assertEqual(result["reason"], "candidate_binding")
                self.assertEqual(persisted(obj.path), before)

    def test_cross_record_candidate_rejected_in_both_arms(self):
        for policy in ("value_audit", "candidate_bound"):
            obj = self.make(policy)
            self.approve_quantity(obj)
            before = persisted(obj.path)
            self.assertFalse(obj.submit("review-1", {"quantity": "other100"}, {"quantity": 101})["accepted"])
            self.assertEqual(persisted(obj.path), before)

    def test_wrong_authorized_value_rejected_in_both_arms(self):
        for policy in ("value_audit", "candidate_bound"):
            obj = self.make(policy)
            self.approve_quantity(obj)
            before = persisted(obj.path)
            self.assertEqual(obj.submit("review-1", {"quantity": "q100a"}, {"quantity": 102})["reason"], "approved_values")
            self.assertEqual(persisted(obj.path), before)

    def test_canonical_value_comparison_does_not_merge_integer_and_float(self):
        for policy in ("value_audit", "candidate_bound"):
            obj = self.make(policy)
            self.approve_quantity(obj)
            self.assertEqual(obj.submit("review-1", {"quantity": "q100a"}, {"quantity": 101.0})["reason"], "approved_values")

    def test_partial_approved_batch_rejected_in_both_arms(self):
        for policy in ("value_audit", "candidate_bound"):
            obj = self.make(policy)
            obj.approve("review-1", {"quantity": "q100a", "batch": "batchB"}, {"quantity": 101, "batch": "B"})
            before = persisted(obj.path)
            self.assertFalse(obj.submit("review-1", {"quantity": "q100a"}, {"quantity": 101})["accepted"])
            self.assertEqual(persisted(obj.path), before)

    def test_stale_approval_rejected_and_state_unchanged(self):
        for policy in ("value_audit", "candidate_bound"):
            obj = self.make(policy)
            self.approve_quantity(obj)
            obj.approve("intervening", {"batch": "batchB"}, {"batch": "B"})
            self.assertTrue(obj.submit("intervening", {"batch": "batchB"}, {"batch": "B"})["accepted"])
            before = persisted(obj.path)
            self.assertEqual(obj.submit("review-1", {"quantity": "q100a"}, {"quantity": 101})["reason"], "stale_version")
            self.assertEqual(persisted(obj.path), before)

    def test_failure_after_sql_writes_rolls_back_every_table(self):
        for policy in ("value_audit", "candidate_bound"):
            obj = self.make(policy)
            self.approve_quantity(obj)
            before = persisted(obj.path)
            result = obj.submit("review-1", {"quantity": "q100a"}, {"quantity": 101}, fail_after_writes=True)
            self.assertEqual(result["reason"], "injected_failure")
            self.assertEqual(persisted(obj.path), before)

    def test_unauthorized_approval_is_rejected_without_writes(self):
        for policy in ("value_audit", "candidate_bound"):
            obj = self.make(policy)
            before = persisted(obj.path)
            with self.assertRaises(ValueError):
                obj.approve("bad", {"quantity": "q100a"}, {"quantity": 101}, principal="outsider")
            self.assertEqual(persisted(obj.path), before)

    def test_identical_persisted_baseline_hides_which_candidate_was_reviewed(self):
        for policy in ("value_audit", "candidate_bound"):
            states = []
            for candidate in ("q100a", "q101"):
                obj = self.make(policy, candidate)
                self.approve_quantity(obj, candidate)
                self.assertTrue(obj.submit("review-1", {"quantity": candidate}, {"quantity": 101})["accepted"])
                states.append(persisted(obj.path))
            self.assertEqual(states[0] == states[1], policy == "value_audit")

    def test_complete_audit_reconstructs_exact_unchanged_source_in_both_arms(self):
        for policy in ("value_audit", "candidate_bound"):
            obj = self.make(policy)
            self.approve_quantity(obj)
            obj.submit("review-1", {"quantity": "q100a"}, {"quantity": 101})
            obj.approve("review-2", {"batch": "batchB"}, {"batch": "B"})
            obj.submit("review-2", {"batch": "batchB"}, {"batch": "B"})
            state = persisted(obj.path)
            sources = {"quantity": "v0:quantity", "batch": "v0:batch"}
            for row in state["audits"]:
                version, before, after = row[0], json.loads(row[3]), json.loads(row[4])
                for field in before:
                    if before[field] != after[field]:
                        sources[field] = f"v{version}:{field}"
            self.assertEqual(sources, {"quantity": "v1:quantity", "batch": "v2:batch"})
            if policy == "candidate_bound":
                self.assertEqual(json.loads(state["versions"][-1][2]), sources)

    def test_candidate_rows_cannot_be_rewritten(self):
        obj = self.make("value_audit")
        with self.assertRaises(sqlite3.IntegrityError):
            obj.con.execute("UPDATE candidates SET proposed_json='101' WHERE candidate_id='q100a'")


if __name__ == "__main__":
    unittest.main()
