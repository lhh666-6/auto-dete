import copy, json, tempfile, unittest
from pathlib import Path
from phase2.kernel import Host, fixtures
from phase2.runner import execute_pair, validate_run, assignment, Log, record_tool
from phase2.providers import parse_action


class Scripted:
    """Deterministic engineering fixture only; never counted as online Agent data."""
    config = {'id': 'TEST', 'provider': 'deterministic_fixture', 'model': 'not-an-online-model'}
    def __init__(self): self.inputs = []
    def decide(self, messages, directory, timeout=90):
        self.inputs.append(copy.deepcopy(messages))
        task = messages[0]['task']
        results = [m for m in messages if m.get('kind') == 'tool_result']
        if not any(m['tool_name'] == 'propose' for m in results):
            return self.action('propose', record_id=task['record_id'], field_key=task['field_key'],
                proposal_value=task['source_proposal_value'], evidence_ref='E1', parent_certificate_id='root-v1')
        c = next(m['result']['candidate_id'] for m in results if m['tool_name'] == 'propose')
        if not any(m['tool_name'] == 'request_authorization' for m in results):
            return self.action('request_authorization', candidate_id=c)
        g = next(m['result'] for m in results if m['tool_name'] == 'request_authorization')
        if not any(m['tool_name'] == 'get_state' for m in results):
            notice = next((m for m in messages if m.get('kind') == 'external_executor_notice'), None)
            if not notice or notice['result']['status'] != 'ok':
                if not any(m['tool_name'] == 'commit' for m in results):
                    return self.action('commit', candidate_id=c, authorization_id=g['authorization_id'],
                        committed_value=g['authorized_value'], idempotency_key='fixture-reuse')
            return self.action('get_state', record_id=task['record_id'])
        h = next(m['result'] for m in reversed(results) if m['tool_name'] == 'get_state')
        return {'action': {'kind': 'final', 'report': {'record_id': task['record_id'], 'version': h['version'],
            'value': h['values'][task['field_key']]}}, 'usage': {}, 'model': 'deterministic', 'provider_request_id': 'fixture'}
    def action(self, tool, **args):
        return {'action': {'kind': 'tool', 'tool': tool, 'arguments': args}, 'usage': {},
            'model': 'deterministic', 'provider_request_id': 'fixture'}


class RunnerTests(unittest.TestCase):
    def test_invalid_commit_arguments_logged_without_crash(self):
        with tempfile.TemporaryDirectory() as d:
            h = Host(fixtures()[0])
            log = Log(Path(d) / 'run', fixtures()[0], Scripted.config, 'pre_policy')
            result, _, _ = record_tool(log, h, 'commit', {}, 'req')
            self.assertEqual(result['error_code'], 'INVALID_ARGUMENTS')
            self.assertEqual(h.state['head']['version'], 1)

    def test_host_exception_after_mutation_preserves_authoritative_state(self):
        with tempfile.TemporaryDirectory() as d:
            h = Host(fixtures()[0])
            case = fixtures()[0]
            c = h.call('propose', {'record_id': case['record_id'], 'field_key': case['field_key'],
                'proposal_value': case['source_proposal_value'], 'evidence_ref': 'E1', 'parent_certificate_id': 'root-v1'})['candidate_id']
            g = h.call('request_authorization', {'candidate_id': c})['authorization_id']
            original = h.call
            def uncertain(tool, args):
                original(tool, args)
                raise RuntimeError('simulated post-commit connection loss')
            h.call = uncertain
            log = Log(Path(d) / 'run', case, Scripted.config, 'pre_policy')
            result, _, _ = record_tool(log, h, 'commit', {'candidate_id': c, 'authorization_id': g,
                'committed_value': case['host_authorized_value'], 'idempotency_key': 'uncertain'}, 'req')
            self.assertEqual(result['status'], 'unknown')
            self.assertEqual(Host.load(log.directory / 'state.sqlite', 'bound').state['head']['version'], 2)

    def test_final_without_completed_report_does_not_count_recovery(self):
        class MissingReport(Scripted):
            def decide(self, messages, directory, timeout=90):
                out = super().decide(messages, directory, timeout)
                if out['action']['kind'] == 'final': out['action']['report'] = {}
                return out
        with tempfile.TemporaryDirectory() as d:
            result = execute_pair(fixtures()[3], MissingReport(), Path(d), ['bound', 'context'])
            self.assertFalse(result['bound']['recovered'])
            self.assertTrue(result['bound']['post_feedback_commit'])

    def test_feedback_in_next_real_decision_input_and_schema_hashes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Scripted()
            result = execute_pair(fixtures()[3], p, Path(d), ['bound', 'context'])
            self.assertEqual(result['bound']['I'], 1)
            self.assertEqual(result['context']['I'], 0)
            self.assertEqual(result['bound']['task_completion'], True)
            self.assertEqual(result['bound']['delivered_recoverable'], 1)
            self.assertEqual(result['bound']['recovered'], True)
            self.assertTrue(any(any(m.get('kind') == 'external_executor_notice' and
                m['result']['error_code'] == 'INSTANCE_MISMATCH' for m in ms) for ms in p.inputs))
            audit = validate_run(Path(d) / 'bound')
            self.assertEqual(audit['errors'], [])
            self.assertEqual(result['checkpoint_hashes']['bound'], result['checkpoint_hashes']['context'])

    def test_n_ignoring_required_preview_fails_task_even_when_state_goal(self):
        with tempfile.TemporaryDirectory() as d:
            result = execute_pair(fixtures()[1], Scripted(), Path(d), ['context', 'bound'])
            self.assertTrue(result['bound']['state_goal'])
            self.assertFalse(result['bound']['task_completion'])

    def test_planned_16_assignments_balanced(self):
        pairs = assignment()
        self.assertEqual(len(pairs), 8)
        self.assertEqual(sum(len(p['order']) for p in pairs), 16)
        self.assertEqual(sum(p['order'][0] == 'bound' for p in pairs), 4)

    def test_invalid_action_not_silently_repaired(self):
        with self.assertRaises(ValueError): parse_action('nonsense')
        self.assertEqual(parse_action('{"kind":"tool","tool":"get_state","arguments":{"record_id":"R"}}')['tool'], 'get_state')

    def test_removed_event_detected(self):
        with tempfile.TemporaryDirectory() as d:
            execute_pair(fixtures()[0], Scripted(), Path(d), ['context', 'bound'])
            file = Path(d) / 'bound/events.jsonl'
            lines = file.read_text(encoding='utf-8').splitlines()
            file.write_text('\n'.join(lines[:2] + lines[3:]) + '\n', encoding='utf-8')
            self.assertTrue(validate_run(Path(d) / 'bound')['errors'])

    def test_rejected_mutation_then_restore_cannot_hide_in_final_journal(self):
        from unittest.mock import patch
        original = Host.call
        def transient(h, tool, args):
            if tool == 'commit' and args.get('idempotency_key') == 'fixture-reuse':
                h.state['head']['values']['reference_note'] = h.case['baseline_values']['reference_note']
            result = original(h, tool, args)
            if tool == 'commit' and result.get('error_code') == 'INSTANCE_MISMATCH':
                h.state['head']['values']['reference_note'] = 'unauthorized-transient'
            return result
        with tempfile.TemporaryDirectory() as d, patch.object(Host, 'call', transient):
            result = execute_pair(fixtures()[3], Scripted(), Path(d), ['bound', 'context'])
            self.assertEqual(result['bound']['I'], 0)
            self.assertTrue(any('rejected_mutation' in s for s in result['bound']['violations']))

    def test_failed_authorization_attempt_not_labeled_reauthorization(self):
        class FailedReview(Scripted):
            def decide(self, messages, directory, timeout=90):
                noticed = any(m.get('kind') == 'external_executor_notice' for m in messages)
                failed = any(m.get('tool_name') == 'request_authorization' and m.get('result', {}).get('error_code') for m in messages)
                if noticed and not failed and any(m.get('kind') == 'tool_result' and m['tool_name'] == 'request_authorization' for m in messages):
                    return self.action('request_authorization', candidate_id='missing')
                return super().decide(messages, directory, timeout)
        with tempfile.TemporaryDirectory() as d:
            result = execute_pair(fixtures()[3], FailedReview(), Path(d), ['bound', 'context'])
            self.assertEqual(result['bound']['recovery_path'], 'reuse_reviewed')

    def test_shared_prefix_corruption_detected(self):
        from phase2.runner import score_run
        with tempfile.TemporaryDirectory() as d:
            execute_pair(fixtures()[0], Scripted(), Path(d), ['bound', 'context'])
            checkpoint = Path(d) / 'prefix/state/checkpoint.json'
            checkpoint.write_text('{}', encoding='utf-8')
            self.assertEqual(score_run(Path(d) / 'bound')['I'], 'unknown')

    def test_missing_feedback_input_preserves_unknown_and_excludes_denominator(self):
        from phase2.runner import score_run
        with tempfile.TemporaryDirectory() as d:
            execute_pair(fixtures()[3], Scripted(), Path(d), ['bound', 'context'])
            (Path(d) / 'bound/model-inputs/0.json').unlink()
            score = score_run(Path(d) / 'bound')
            self.assertEqual(score['I'], 'unknown')
            self.assertEqual(score['delivered_recoverable'], 0)

    def test_missing_final_snapshot_does_not_crash_scoring(self):
        from phase2.runner import score_run
        with tempfile.TemporaryDirectory() as d:
            execute_pair(fixtures()[0], Scripted(), Path(d), ['bound', 'context'])
            (Path(d) / 'bound/state/final.json').unlink()
            self.assertEqual(score_run(Path(d) / 'bound')['I'], 'unknown')


if __name__ == '__main__': unittest.main()
