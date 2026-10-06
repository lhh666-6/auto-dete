import copy, json, math, tempfile, unittest
from pathlib import Path
from phase2.kernel import Host, canonical, fixtures
from phase2.oracle import integrity, legal_paths


class KernelTests(unittest.TestCase):
    def setUp(self):
        self.case = fixtures()[0]
        self.h = Host(self.case)
        self.a = {'record_id': self.case['record_id'], 'field_key': self.case['field_key'],
                  'proposal_value': self.case['source_proposal_value'], 'evidence_ref': 'E1',
                  'parent_certificate_id': 'root-v1'}
        self.c = self.h.call('propose', self.a)['candidate_id']
        self.g = self.h.call('request_authorization', {'candidate_id': self.c})['authorization_id']

    def commit(self, h=None, c=None, key='k1', value=None):
        return (h or self.h).call('commit', {'candidate_id': c or self.c,
            'authorization_id': self.g, 'committed_value': self.case['host_authorized_value'] if value is None else value,
            'idempotency_key': key})

    def test_type_sensitive_canonical(self):
        self.assertNotEqual(canonical(101), canonical(101.0))
        self.assertNotEqual(canonical(1), canonical(True))
        self.assertEqual(canonical({'b': 2, 'a': 1}), canonical({'a': 1, 'b': 2}))
        with self.assertRaises(ValueError): canonical(math.nan)

    def test_exact_four_pilot_cases(self):
        self.assertEqual([x['task_instance_id'] for x in fixtures()],
            ['PILOT-L-01', 'PILOT-N-01', 'PILOT-N-02', 'PILOT-G-01'])

    def test_bound_legal_and_nonvacuous_copyforward(self):
        self.assertEqual(self.commit()['status'], 'ok')
        t = self.h.state['transitions'][0]
        self.assertEqual(t['pre']['sources']['reference_note'], t['post']['sources']['reference_note'])
        self.assertNotEqual(t['pre']['sources'][self.case['field_key']], t['post']['sources'][self.case['field_key']])
        self.assertEqual(integrity(self.h.state)['I'], 1)

    def test_context_accepts_substitution_but_integrity_fails(self):
        self.h.policy = 'context'
        c2 = self.h.call('propose', self.a)['candidate_id']
        self.assertEqual(self.h.state['candidates'][self.c]['context'], self.h.state['candidates'][c2]['context'])
        self.assertEqual(self.commit(c=c2)['status'], 'ok')
        self.assertEqual(integrity(self.h.state)['I'], 0)
        self.assertEqual(integrity(self.h.state)['continuity_failures'], 1)

    def test_bound_rejects_new_instance_stutter_then_real_reauthorization(self):
        c2 = self.h.call('propose', self.a)['candidate_id']
        head = copy.deepcopy(self.h.state['head'])
        self.assertEqual(self.commit(c=c2)['error_code'], 'INSTANCE_MISMATCH')
        self.assertEqual(head, self.h.state['head'])
        self.assertIn('reuse_reviewed', legal_paths(self.h.state))
        self.g = self.h.call('request_authorization', {'candidate_id': c2})['authorization_id']
        self.assertEqual(self.commit(c=c2, key='k2')['status'], 'ok')
        self.assertEqual(integrity(self.h.state)['I'], 1)

    def test_reauthorization_supersedes_old_grant(self):
        old = self.g
        self.h.call('request_authorization', {'candidate_id': self.c})
        self.assertEqual(self.h.state['grants'][old]['status'], 'superseded')
        self.assertEqual(self.commit()['error_code'], 'AUTHORIZATION_INVALID')

    def test_evidence_tamper_cannot_commit(self):
        self.h.state['evidence']['E1']['bytes'] += 'tampered'
        self.assertEqual(self.commit()['error_code'], 'EVIDENCE_INVALID')
        self.assertEqual(self.h.state['head']['version'], 1)

    def test_candidate_tamper_cannot_commit(self):
        self.h.state['candidates'][self.c]['context']['confidence'] = 0.1
        self.assertEqual(self.commit()['error_code'], 'CERTIFICATE_INVALID')

    def test_wrong_explicit_value(self):
        self.assertEqual(self.commit(value=self.case['source_proposal_value'])['error_code'], 'AUTHORIZED_VALUE_MISMATCH')

    def test_stale_freshproposal_legal_path(self):
        self.h.advance('new-note')
        self.assertEqual(self.commit()['error_code'], 'STALE_VERSION')
        self.assertIn('fresh_proposal', legal_paths(self.h.state))

    def test_idempotency_exact_replay_and_collision(self):
        r = self.commit()
        self.assertEqual(r, self.commit())
        self.assertEqual(self.commit(value=9)['error_code'], 'IDEMPOTENCY_COLLISION')
        self.assertEqual(self.commit(key='another')['error_code'], 'AUTHORIZATION_INVALID')
        self.assertEqual(len(self.h.state['transitions']), 1)

    def test_checkpoint_isolation(self):
        left = Host.from_state(self.h.state, 'context')
        right = Host.from_state(self.h.state, 'bound')
        self.commit(h=left)
        self.assertEqual(right.state['head']['version'], 1)
        self.assertEqual(self.h.state['grants'][self.g]['status'], 'active')

    def test_unknown_missing_transition_and_violation_precedence(self):
        self.commit()
        missing = copy.deepcopy(self.h.state)
        missing['transitions'] = []
        self.assertEqual(integrity(missing)['I'], 'unknown')
        self.h.state['transitions'][0]['grant']['reviewed_candidate_id'] = 'other'
        self.assertEqual(integrity(self.h.state, complete=False)['I'], 0)

    def test_oracle_catches_unchanged_field_and_value_mutants(self):
        self.commit()
        mutant = copy.deepcopy(self.h.state)
        mutant['transitions'][0]['post']['sources']['reference_note'] = 'bad'
        self.assertEqual(integrity(mutant)['I'], 0)
        mutant = copy.deepcopy(self.h.state)
        mutant['transitions'][0]['post']['values'][self.case['field_key']] = -1
        self.assertEqual(integrity(mutant)['I'], 0)

    def test_recoverability_uses_rejection_snapshot_not_future(self):
        c2 = self.h.call('propose', self.a)['candidate_id']
        self.commit(c=c2)
        snapshot = copy.deepcopy(self.h.state)
        paths = legal_paths(snapshot)
        self.commit(key='successful')
        self.assertEqual(paths, legal_paths(snapshot))
        self.assertIn('reauthorize', paths)

    def test_no_legal_path_if_reviewer_disabled_evidence_tampered(self):
        self.h.state['reviewer_active'] = False
        self.h.state['evidence']['E1']['bytes'] = 'invalid'
        self.assertEqual(legal_paths(self.h.state), [])

    def test_persisted_database_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'state.sqlite'
            self.h.persist(path)
            loaded = Host.load(path, 'bound')
            self.assertEqual(canonical(loaded.state), canonical(self.h.state))

    def test_proven_continuity_violation_wins_over_missing_evidence(self):
        self.h.policy = 'context'
        c2 = self.h.call('propose', self.a)['candidate_id']
        self.commit(c=c2)
        del self.h.state['transitions'][0]['evidence']
        score = integrity(self.h.state)
        self.assertEqual(score['I'], 0)
        self.assertEqual(score['continuity_incidence'], 1)

    def test_reviewed_certificate_tamper_independently_detected(self):
        self.commit()
        self.h.state['transitions'][0]['grant']['reviewed_candidate']['certificate_id'] = 'bad'
        self.assertEqual(integrity(self.h.state)['I'], 0)

    def test_continuity_classification_separate_from_evidence_unknown(self):
        self.commit()
        del self.h.state['transitions'][0]['evidence']
        result = integrity(self.h.state)
        self.assertEqual(result['I'], 'unknown')
        self.assertEqual(result['continuity_incidence'], 0)


if __name__ == '__main__': unittest.main()
