import unittest
from dataclasses import replace
import observation_witnesses as witness


class CandidateIdentityWitnessTests(unittest.TestCase):
    def test_identity_pair_preserves_pool_context_and_values(self):
        safe, unsafe = witness.candidate_identity_pair()
        self.assertEqual(safe.candidates, unsafe.candidates)
        self.assertEqual(safe.authorizations, unsafe.authorizations)
        self.assertNotEqual(safe.batch_items[0].candidate_id, unsafe.batch_items[0].candidate_id)
        first, second = safe.candidates
        self.assertEqual(replace(first, candidate_id=second.candidate_id), second)

    def test_identity_pair_changes_only_context_class_and_outcome(self):
        safe, unsafe = witness.candidate_identity_pair()
        for h in (safe, unsafe):
            self.assertEqual(witness.validate_history_domain(h), ())
        self.assertEqual(witness.normative_outcome(safe)[0], 'admissible')
        self.assertEqual(witness.normative_outcome(unsafe)[0], 'inadmissible')
        self.assertEqual([c for c in witness.CLASSES if witness.observe(safe,c)!=witness.observe(unsafe,c)], ['D_C'])

    def test_identity_report_contains_raw_derived_pair(self):
        report = witness.build_report()['candidate_identity_pair']
        self.assertTrue(report['reduced_projection_equal'])
        self.assertTrue(report['normative_outcomes_differ'])
        self.assertEqual(report['changed_observation_classes'], ['D_C'])
        self.assertIn('history', report['unsafe'])


if __name__ == '__main__':
    unittest.main()
