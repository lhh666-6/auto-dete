import copy
import unittest
from audit_corrections import FINAL, read, load_snapshot, audit_snapshot


class CorrectionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        row = next(r for r in read(FINAL / 'normalized/runs.json') if r['scenario_id'] == 'B2' and r['agent_task_completed'])
        cls.base = load_snapshot(FINAL / 'runs' / row['run_id'])
        cls.target = next(t['transition_id'] for t in cls.base['fact_transitions'] if t['source_kind'] == 'AI_SUGGESTION')

    def mutate(self, table, key, value):
        data = copy.deepcopy(self.base)
        data[table][-1][key] = value
        return audit_snapshot(data, self.target)['failures']

    def test_frozen_chain_passes(self):
        self.assertEqual(audit_snapshot(self.base, self.target)['failures'], [])

    def test_authorization_type_alias_is_rejected(self):
        self.assertIn('authorized_committed_equality', self.mutate('authorization_bindings', 'authorized_value_payload', '101.0'))

    def test_predecessor_is_checked(self):
        self.assertIn('predecessor_continuity', self.mutate('record_versions', 'previous_version', 0))

    def test_certificate_tampering_is_detected(self):
        self.assertIn('certificate_content_address', self.mutate('candidate_certificates', 'producer_id', 'tampered'))

    def test_decision_candidate_is_checked(self):
        self.assertIn('review_candidate_binding', self.mutate('human_decisions', 'candidate_id', 'other-instance'))

    def test_evidence_bytes_are_checked(self):
        data = copy.deepcopy(self.base)
        eid = data['candidate_certificates'][-1]['evidence_file_id']
        data['evidence_bytes'][eid] = b'tampered'
        self.assertIn('evidence_content_hash', audit_snapshot(data, self.target)['failures'])

    def test_source_anchor_is_checked(self):
        self.assertIn('current_source_anchor', self.mutate('record_versions', 'fact_sources', '{"total_quantity":"missing"}'))

    def test_unchanged_field_cannot_get_new_source(self):
        self.assertIn('unchanged_source_retention', self.mutate('record_versions', 'values', '{"total_quantity":7}'))

    def test_expected_version_is_checked(self):
        self.assertIn('expected_version', self.mutate('candidate_certificates', 'expected_fact_version', 0))

    def test_time_order_is_checked(self):
        self.assertIn('trace_time_order', self.mutate('human_decisions', 'decided_at', '2020-01-01 00:00:00'))

    def test_proposal_receipt_is_checked(self):
        data = copy.deepcopy(self.base)
        event = next(e for e in data['events'] if e['event_type'] == 'TOOL_CALL' and e['tool_name'] == 'auto_decte_propose')
        event['tool_arguments']['value'] = 99
        self.assertIn('proposal_receipt_value', audit_snapshot(data, self.target)['failures'])

    def test_host_declared_authorized_value_is_checked(self):
        data = copy.deepcopy(self.base)
        data['prepared']['authorized_values_by_field']['total_quantity'] = 101.0
        self.assertIn('host_authorized_value', audit_snapshot(data, self.target)['failures'])


if __name__ == '__main__':
    unittest.main()
