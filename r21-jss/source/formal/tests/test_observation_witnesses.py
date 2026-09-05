from dataclasses import fields, replace
import json
from pathlib import Path
import sys
import unittest


FORMAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORMAL_ROOT))

from observation_witnesses import (  # noqa: E402
    CLASSES,
    BatchItem,
    build_report,
    History,
    normative_outcome,
    observe,
    paired_histories,
    project,
    validate_history_domain,
)


class ObservationWitnessTests(unittest.TestCase):
    def test_observations_and_outcomes_are_derived_not_stored(self) -> None:
        stored_fields = {field.name for field in fields(History)}
        self.assertNotIn("observations", stored_fields)
        self.assertNotIn("outcome", stored_fields)

    def test_each_pair_is_realizable_and_satisfies_irredundancy(self) -> None:
        pairs = paired_histories()
        self.assertEqual(set(pairs), set(CLASSES))

        for omitted, (safe, unsafe) in pairs.items():
            with self.subTest(omitted=omitted):
                self.assertEqual(validate_history_domain(safe), ())
                self.assertEqual(validate_history_domain(unsafe), ())
                self.assertNotEqual(safe, unsafe)

                remaining = tuple(item for item in CLASSES if item != omitted)
                self.assertNotEqual(
                    normative_outcome(safe), normative_outcome(unsafe)
                )
                self.assertEqual(project(safe, remaining), project(unsafe, remaining))
                self.assertNotEqual(project(safe, CLASSES), project(unsafe, CLASSES))

    def test_dual_value_pair_retains_candidate_identity_and_value(self) -> None:
        safe, unsafe = paired_histories()["D_V"]
        safe_candidates = {item.candidate_id: item for item in safe.candidates}
        unsafe_candidates = {item.candidate_id: item for item in unsafe.candidates}

        self.assertEqual(observe(safe, "D_C"), observe(unsafe, "D_C"))
        self.assertEqual(safe_candidates, unsafe_candidates)
        self.assertNotEqual(observe(safe, "D_V"), observe(unsafe, "D_V"))

    def test_batch_and_source_observations_are_separate(self) -> None:
        batch_safe, batch_unsafe = paired_histories()["D_B"]
        source_safe, source_unsafe = paired_histories()["D_S"]

        self.assertEqual(observe(batch_safe, "D_S"), observe(batch_unsafe, "D_S"))
        self.assertEqual(observe(source_safe, "D_B"), observe(source_unsafe, "D_B"))

    def test_domain_validator_rejects_an_unrealizable_reference(self) -> None:
        safe, _ = paired_histories()["D_B"]
        malformed = replace(
            safe,
            batch_items=(
                BatchItem("missing-candidate", safe.batch_items[0].authorization_id),
                safe.batch_items[1],
            ),
        )
        self.assertTrue(validate_history_domain(malformed))

    def test_audit_report_is_json_serializable(self) -> None:
        json.dumps(build_report())


if __name__ == "__main__":
    unittest.main()
