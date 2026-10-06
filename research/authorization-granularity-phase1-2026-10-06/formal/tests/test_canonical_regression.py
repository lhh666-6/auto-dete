from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from observation_witnesses import CLASSES, FieldValue, paired_histories, project, normative_outcome, validate_history_domain


class CanonicalRegressionTests(unittest.TestCase):
    def test_full_projection_separates_int_float_authorization(self):
        safe, _ = paired_histories()['D_V']
        mutant = replace(safe, authorizations=(replace(safe.authorizations[0], authorized_value=101.0),))
        self.assertEqual(validate_history_domain(mutant), ())
        self.assertNotEqual(normative_outcome(safe), normative_outcome(mutant))
        self.assertNotEqual(project(safe, CLASSES), project(mutant, CLASSES))

    def test_projection_preserves_nested_types(self):
        safe, _ = paired_histories()['D_V']
        for left, right in [(1, True), ({'x': [101]}, {'x': [101.0]})]:
            a = replace(safe, candidates=(replace(safe.candidates[0], proposal_value=left),))
            b = replace(safe, candidates=(replace(safe.candidates[0], proposal_value=right),))
            self.assertNotEqual(project(a, CLASSES), project(b, CLASSES))

    def test_connectivity_rejects_int_float_alias(self):
        safe, _ = paired_histories()['D_V']
        values = tuple(replace(v, value=float(v.value)) for v in safe.commits[0].before)
        mutant = replace(safe, commits=(replace(safe.commits[0], before=values),))
        self.assertIn('disconnected commit sequence', validate_history_domain(mutant))

    def test_endpoint_rejects_int_float_alias(self):
        safe, _ = paired_histories()['D_V']
        values = tuple(replace(v, value=float(v.value)) for v in safe.successor_values)
        mutant = replace(safe, successor_values=values)
        self.assertIn('commit sequence does not reach successor values', validate_history_domain(mutant))

    def test_object_key_order_does_not_change_projection(self):
        safe, _ = paired_histories()['D_V']
        a = replace(safe, candidates=(replace(safe.candidates[0], proposal_value={'x': 1, 'y': 2}),))
        b = replace(safe, candidates=(replace(safe.candidates[0], proposal_value={'y': 2, 'x': 1}),))
        self.assertEqual(project(a, CLASSES), project(b, CLASSES))


if __name__ == '__main__':
    unittest.main()
