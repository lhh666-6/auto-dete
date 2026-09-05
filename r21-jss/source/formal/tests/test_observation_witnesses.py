from pathlib import Path
import sys
import unittest


FORMAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORMAL_ROOT))

from observation_witnesses import CLASSES, paired_histories, project  # noqa: E402


class ObservationWitnessTests(unittest.TestCase):
    def test_each_pair_satisfies_the_declared_irredundancy_condition(self) -> None:
        pairs = paired_histories()
        self.assertEqual(set(pairs), set(CLASSES))

        for omitted, (safe, unsafe) in pairs.items():
            with self.subTest(omitted=omitted):
                remaining = tuple(item for item in CLASSES if item != omitted)
                self.assertNotEqual(safe.outcome, unsafe.outcome)
                self.assertEqual(project(safe, remaining), project(unsafe, remaining))
                self.assertNotEqual(project(safe, CLASSES), project(unsafe, CLASSES))

    def test_dual_value_pair_does_not_rewrite_candidate_identity(self) -> None:
        safe, unsafe = paired_histories()["D_V"]
        self.assertEqual(safe.observations["D_C"], unsafe.observations["D_C"])
        self.assertEqual(safe.raw["candidate_id"], unsafe.raw["candidate_id"])
        self.assertEqual(safe.raw["candidate_value"], unsafe.raw["candidate_value"])
        self.assertNotEqual(safe.observations["D_V"], unsafe.observations["D_V"])

    def test_batch_and_source_observations_are_separate(self) -> None:
        batch_safe, batch_unsafe = paired_histories()["D_B"]
        source_safe, source_unsafe = paired_histories()["D_S"]

        self.assertEqual(batch_safe.observations["D_S"], batch_unsafe.observations["D_S"])
        self.assertEqual(source_safe.observations["D_B"], source_unsafe.observations["D_B"])


if __name__ == "__main__":
    unittest.main()
