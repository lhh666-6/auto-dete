"""Offline regression tests. Never decrypt credentials or contact an API."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('budget_run', ROOT / 'run.py')
run = None
if (ROOT / 'run.py').exists():
    run = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(run)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(run, 'Budget runner implementation is missing')

    def test_allocation_is_balanced_reproducible_and_matches_sampling_rule(self):
        tasks = run.read_json(run.SOURCE / 'frozen-formal/formal-task-manifest.json')['tasks']
        a = run.build_allocation(tasks)
        self.assertTrue(all(isinstance(k, str) for k in a['condition_map']), 'Persisted allocation keys must be strings')
        self.assertEqual(a, run.build_allocation(list(reversed(tasks))))
        self.assertEqual(len(a['tasks']), 24)
        self.assertEqual(len(a['cells']), 96)
        import random
        rng = random.Random(20261014)
        for scenario in 'EGLNRV':
            expected = rng.sample(sorted([t['task_instance_id'] for t in tasks if t['scenario'] == scenario]), 4)
            selected = [t for t in a['tasks'] if t['scenario'] == scenario]
            self.assertEqual({t['task_id'] for t in selected}, set(expected))
            self.assertEqual(sorted(t['sequence_index'] for t in selected), [0, 1, 2, 3])
        for task in a['tasks']:
            cells = [c for c in a['cells'] if c['task_id'] == task['task_id']]
            self.assertEqual([run.CONDITION_NAMES.index(c['condition']) for c in cells], run.WILLIAMS[task['sequence_index']])
            self.assertEqual({c['max_tokens'] for c in cells}, {4096, 393216})
            self.assertTrue(all(c['path'].endswith('/' + c['policy']) for c in cells))

    def test_request_body_budget_is_only_difference_and_contains_no_secret(self):
        configs = run.make_configs()
        low = run.request_body(configs['low'], [{'kind': 'test'}])
        high = run.request_body(configs['high'], [{'kind': 'test'}])
        self.assertEqual(low['max_tokens'], 4096)
        self.assertEqual(high.pop('max_tokens'), 393216)
        low.pop('max_tokens')
        self.assertEqual(low, high)
        self.assertNotIn('credential', run.canonical(low))
        self.assertEqual({c['id'] for c in configs.values()}, {'B'})
        self.assertEqual({c['request_timeout_seconds'] for c in configs.values()}, {1800})
        self.assertEqual({c['suffix_seconds'] for c in configs.values()}, {21600})
        for config in configs.values():
            self.assertNotIn('actual_returned_identifier', config)
            self.assertNotIn('availability_probe_start_utc', config)
            self.assertNotIn('availability_probe_end_utc', config)
            self.assertEqual(config['expected_returned_identifier'], 'deepseek-v4-flash')

    def test_vendor_semantics_and_scorer_unchanged(self):
        for name in ('kernel.py', 'oracle.py', 'trajectories.py', 'providers.py', '__init__.py'):
            self.assertEqual((run.SOURCE / 'src/phase2' / name).read_bytes(), (ROOT / 'vendor/src/phase2' / name).read_bytes())
        original = (run.SOURCE / 'src/phase2/runner.py').read_text(encoding='utf-8')
        copied = (ROOT / 'vendor/src/phase2/runner.py').read_text(encoding='utf-8')
        self.assertEqual(original[original.index('def validate_run('):], copied[copied.index('def validate_run('):])

    def test_initial_equivalence_check_covers_all_planned_cells(self):
        self.assertTrue(hasattr(run, 'check_initial_inputs'), 'Full 24-task equivalence preflight missing')
        report = run.check_initial_inputs(run.build_allocation(run.source_tasks()), run.make_configs())
        self.assertEqual(report['tasks_checked'], 24)
        self.assertEqual(len(report['cells']), 96)
        self.assertTrue(report['passed'])

    def test_initial_messages_identical_for_same_policy_and_scenarios_preserved(self):
        allocation = run.build_allocation(run.source_tasks())
        configs = run.make_configs()
        for scenario in 'EGLNRV':
            task = next(t for t in allocation['tasks'] if t['scenario'] == scenario)
            case = next(c for c in run.source_tasks() if c['task_instance_id'] == task['task_id'])
            for policy in ('context', 'bound'):
                visible = []
                with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
                    for budget in ('low', 'high'):
                        cell = next(c for c in allocation['cells'] if c['task_id'] == task['task_id'] and c['budget'] == budget and c['policy'] == policy)
                        run.copy_prefix(cell, Path(tmp))
                        branch, log, messages, pending = run.initialize_arm(cell, case, configs[budget], Path(tmp))
                        visible.append(run.canonical(messages))
                        self.assertTrue(branch.state['after_checkpoint'])
                        self.assertTrue(log.events[0]['run_id'].endswith('-B-' + policy))
                        self.assertNotEqual(log.events[0]['timestamp_utc'], run.logical_time(branch.state))
                        if scenario == 'N': self.assertEqual(messages[-1]['kind'], 'business_notice')
                        if scenario == 'G':
                            self.assertEqual(messages[-1]['kind'], 'external_executor_notice')
                            self.assertEqual(messages[-1]['result']['status'], 'ok' if policy == 'context' else 'rejected')
                            self.assertEqual(len(pending), int(policy == 'bound'))
                        if scenario == 'E': self.assertEqual(branch.state['current_evidence_ref'], 'E2')
                        if scenario == 'V': self.assertEqual(messages[-1]['kind'], 'external_state_advance')
                        if scenario == 'R':
                            grant = next(g for g in branch.state['grants'].values() if g['status'] == 'active')
                            result = branch.call('commit', {'candidate_id': grant['reviewed_candidate_id'], 'authorization_id': grant['authorization_id'], 'committed_value': grant['authorized_value'], 'idempotency_key': 'test'})
                            self.assertEqual(branch.call('get_receipt', {'commit_request_id': result['commit_request_id']})['error_code'], 'CAPABILITY_UNAVAILABLE')
                self.assertEqual(*visible)

    def test_provider_records_actual_wire_and_raw_without_headers(self):
        class Reply:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return b'{"id":"test","model":"deepseek-v4-flash","content":[{"type":"text","text":"invalid"}],"stop_reason":"max_tokens","usage":{"output_tokens":4096}}'
        for budget in ('low', 'high'):
            config = run.make_configs()[budget]
            with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp, patch.dict('os.environ', {'PHASE2_DSH_API_KEY': 'SENTINEL_SECRET'}), patch('urllib.request.urlopen', return_value=Reply()) as request:
                reply = run.RecordingProvider(config).decide([{'kind': 'test'}], Path(tmp), 1800)
                self.assertEqual(request.call_args.kwargs['timeout'], 1800)
                wire = request.call_args.args[0].data
                self.assertEqual(wire, (Path(tmp) / 'request-body.raw.json').read_bytes())
                self.assertEqual(json.loads(wire)['max_tokens'], run.BUDGETS[budget])
                self.assertEqual((Path(tmp) / 'response-body.bin').read_bytes(), (Path(tmp) / 'response.json').read_bytes())
                self.assertEqual(reply['stop_reason'], 'max_tokens')
                self.assertTrue(all(b'SENTINEL_SECRET' not in f.read_bytes() for f in Path(tmp).rglob('*') if f.is_file()))

    def test_global_stop_codes(self):
        for code in ('HTTP_400', 'HTTP_401', 'HTTP_402', 'HTTP_403', 'HTTP_404', 'DEPLOYMENT_CHANGED', 'AUDIT_FAILED'):
            self.assertTrue(run.global_stop(code))
        self.assertFalse(run.global_stop('invalid_output'))
        self.assertFalse(run.global_stop('budget'))

    def test_quota_429_stops_without_retrying_and_preserves_raw(self):
        import io
        import urllib.error
        config = run.make_configs()['low']
        error = urllib.error.HTTPError('https://fixture.invalid', 429, 'Too many requests', {},
                                      io.BytesIO(b'{"error":"insufficient balance"}'))
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp, patch.dict('os.environ', {'PHASE2_DSH_API_KEY': 'SENTINEL_SECRET'}), patch('urllib.request.urlopen', side_effect=error):
            with self.assertRaises(run.TransportError) as caught:
                run.RecordingProvider(config).decide([], Path(tmp))
            self.assertFalse(caught.exception.retryable)
            self.assertTrue(run.global_stop(caught.exception.code))
            self.assertEqual(run.read_json(Path(tmp) / 'failure.json')['upstream_code'], 'HTTP_429')
            self.assertEqual((Path(tmp) / 'http-error.txt').read_bytes(), b'{"error":"insufficient balance"}')

    def test_freeze_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            root = Path(tmp)
            (root / 'PROTOCOL.md').write_text('approved', encoding='utf-8')
            run.write_json(root / 'freeze.json', {'files': {'PROTOCOL.md': run.sha(root / 'PROTOCOL.md')}})
            (root / 'freeze.sha256').write_text(run.sha(root / 'freeze.json'), encoding='ascii')
            run.verify_freeze(root)
            (root / 'PROTOCOL.md').write_text('changed', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'FREEZE_HASH_MISMATCH'):
                run.verify_freeze(root)

    def test_os_lock_rejects_a_second_lane(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            with run.collection_lock(Path(tmp)):
                with self.assertRaises(OSError):
                    with run.collection_lock(Path(tmp)): pass

    def fixture(self, root, scenario='L', budget='low'):
        allocation = run.build_allocation(run.source_tasks())
        cell = next(c for c in allocation['cells'] if c['scenario'] == scenario and c['budget'] == budget and c['policy'] == 'bound')
        case = next(t for t in run.source_tasks() if t['task_instance_id'] == cell['task_id'])
        run.copy_prefix(cell, root)
        return cell, case, run.make_configs()[budget]

    def test_terminal_arm_is_audited_but_never_resampled(self):
        self.assertTrue(hasattr(run, 'execute_arm'), 'single-arm execution missing')
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            root = Path(tmp)
            cell, case, config = self.fixture(root)
            provider = FakeProvider(config)
            first = run.execute_arm(cell, case, provider, root)
            self.assertEqual(first['score']['terminal'], 'agent_final')
            self.assertEqual(first['score']['audit_errors'], [])
            n = provider.calls
            self.assertEqual(run.execute_arm(cell, case, provider, root), first)
            self.assertEqual(provider.calls, n)
            self.assertEqual(first['score']['I'], 1)
            self.assertFalse(first['score']['task_completion'])

    def test_inherited_repair_budget_is_not_reset(self):
        self.assertTrue(hasattr(run, 'execute_arm'), 'single-arm execution missing')
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            root = Path(tmp)
            cell, case, config = self.fixture(root)
            host, log, messages, pending = run.initialize_arm(cell, case, config, root)
            messages.append({'kind': 'format_error', 'instruction': 'INVALID_ACTION_FORMAT. Return the required JSON format.'})
            provider = FakeProvider(config, raw_action='bad')
            outcome = run.runner.loop(host, provider, messages, log)
            self.assertEqual(outcome['terminal'], 'invalid_output')
            self.assertEqual(provider.calls, 1)

    def test_initialization_interruption_is_retained_and_not_replayed(self):
        self.assertTrue(hasattr(run, 'execute_arm'), 'single-arm execution missing')
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            root = Path(tmp)
            cell, case, config = self.fixture(root, 'G')
            run.initialize_arm(cell, case, config, root)
            directory = root / cell['path']
            before = run.sha(directory / 'state.sqlite')
            provider = FakeProvider(config)
            result = run.execute_arm(cell, case, provider, root)
            self.assertTrue(result['global_stop'])
            self.assertEqual(result['error'], 'RESUME_BOUNDARY_MISSING')
            self.assertEqual(result['status'], 'preserved_incomplete')
            self.assertEqual(provider.calls, 0)
            self.assertEqual(before, run.sha(directory / 'state.sqlite'))

    def test_interruption_before_first_event_preserves_unknown(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            root = Path(tmp)
            cell, case, config = self.fixture(root)
            directory = root / cell['path']
            directory.mkdir(parents=True)
            import shutil
            shutil.copyfile(root / cell['prefix_path'] / 'state.sqlite', directory / 'state.sqlite')
            provider = FakeProvider(config)
            try:
                result = run.execute_arm(cell, case, provider, root)
            except Exception as exc:
                self.fail('An interrupted initialization must retain unknown rather than crash: ' + type(exc).__name__)
            self.assertEqual(result['status'], 'preserved_incomplete')
            self.assertEqual(result['score']['I'], 'unknown')
            self.assertIsNone(result['score']['task_completion'])
            self.assertEqual(provider.calls, 0)

    def test_raw_received_response_is_reused_after_pause(self):
        self.assertTrue(hasattr(run, 'execute_arm'), 'single-arm execution missing')
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            root = Path(tmp)
            cell, case, config = self.fixture(root)
            class PausingProvider(FakeProvider):
                def decide(self, *args, **kwargs):
                    super().decide(*args, **kwargs)
                    raise run.PauseRequested()
            paused = PausingProvider(config)
            with self.assertRaises(run.PauseRequested): run.execute_arm(cell, case, paused, root)
            resumed = FakeProvider(config)
            result = run.execute_arm(cell, case, resumed, root)
            self.assertEqual(result['score']['terminal'], 'agent_final')
            self.assertEqual(resumed.calls, 0)
            self.assertEqual(result['score']['audit_errors'], [])

    def test_interrupted_semantic_action_is_not_replayed(self):
        self.assertTrue(hasattr(run, 'execute_arm'), 'single-arm execution missing')
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            root = Path(tmp)
            cell, case, config = self.fixture(root)
            action = json.dumps({'kind': 'tool', 'tool': 'get_state', 'arguments_json': json.dumps({'record_id': case['record_id']}), 'report_json': '{}'})
            provider = FakeProvider(config, raw_action=action)
            real_record = run.runner.record_tool
            def interrupted(*args, **kwargs):
                real_record(*args, **kwargs)
                raise run.PauseRequested()
            with patch.object(run.runner, 'record_tool', interrupted):
                with self.assertRaises(run.PauseRequested): run.execute_arm(cell, case, provider, root)
            before = provider.calls
            result = run.execute_arm(cell, case, provider, root)
            self.assertTrue(result['global_stop'])
            self.assertEqual(result['error'], 'INTERRUPTED_SEMANTIC_STEP')
            self.assertEqual(provider.calls, before)

    def test_termination_event_without_score_is_rescored_without_model(self):
        self.assertTrue(hasattr(run, 'execute_arm'), 'single-arm execution missing')
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            root = Path(tmp)
            cell, case, config = self.fixture(root)
            host, log, messages, pending = run.initialize_arm(cell, case, config, root)
            provider = FakeProvider(config)
            outcome = run.runner.loop(host, provider, messages, log, pending=pending)
            run.runner.finish(log, host, outcome)
            (log.directory / 'score.json').unlink()
            before = provider.calls
            result = run.execute_arm(cell, case, provider, root)
            self.assertEqual(result['score']['audit_errors'], [])
            self.assertEqual(provider.calls, before)

    def test_collect_checks_initial_frozen_input_before_model_call(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            root = Path(tmp)
            cell, case, config = self.fixture(root)
            run.write_json(root / 'inputs/initial-input-equivalence.json', {'cells': {cell['path']: {'messages_sha256': '0' * 64}}})
            provider = FakeProvider(config)
            with self.assertRaisesRegex(ValueError, 'INITIAL_INPUT_FROZEN_MISMATCH'):
                run.execute_arm(cell, case, provider, root)
            self.assertEqual(provider.calls, 0)

    def test_twenty_responses_and_three_transport_attempts(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            root = Path(tmp)
            cell, case, config = self.fixture(root)
            action = json.dumps({'kind': 'tool', 'tool': 'get_state', 'arguments_json': json.dumps({'record_id': case['record_id']}), 'report_json': '{}'})
            provider = FakeProvider(config, raw_action=action)
            result = run.execute_arm(cell, case, provider, root)
            self.assertEqual(provider.calls, 20)
            self.assertEqual(result['score']['terminal'], 'budget')
            self.assertFalse(result['global_stop'])
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            root = Path(tmp)
            cell, case, config = self.fixture(root)
            class TransientProvider(FakeProvider):
                def decide(self, *args, **kwargs):
                    self.calls += 1
                    raise run.TransportError('HTTP_503', True)
            provider = TransientProvider(config)
            with patch.object(run.runner.time, 'sleep') as sleep:
                result = run.execute_arm(cell, case, provider, root)
            self.assertEqual(provider.calls, 3)
            self.assertEqual([c.args[0] for c in sleep.call_args_list], [2, 8])
            self.assertEqual(result['score']['terminal'], 'runtime_error')

    def test_collection_pause_resume_and_global_stop(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests-temp') as tmp:
            root = Path(tmp)
            cell, case, config = self.fixture(root)
            run.write_json(root / 'allocation.json', {'cells': [cell]})
            run.write_json(root / 'configs.json', run.make_configs())
            run.write_json(root / 'inputs/tasks.json', {'tasks': [case]})
            run.write_json(root / 'inputs/source-hashes.json', {'files': {}})
            run.write_json(root / 'freeze.json', {'files': {name: run.sha(root / name) for name in ('allocation.json', 'configs.json', 'inputs/tasks.json')}})
            (root / 'freeze.sha256').write_text(run.sha(root / 'freeze.json'), encoding='ascii')
            class PausingProvider(FakeProvider):
                def decide(self, *args, **kwargs):
                    super().decide(*args, **kwargs)
                    raise run.PauseRequested()
            result = run.collect(root, provider_factory=lambda cfg, study: PausingProvider(cfg))
            self.assertEqual(result['status'], 'paused')
            resumed = FakeProvider(config)
            result = run.collect(root, resume=True, provider_factory=lambda cfg, study: resumed)
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(resumed.calls, 0)
            progress = run.read_json(root / 'collection-status.json')
            progress['status'] = 'global_stop'
            run.write_json(root / 'collection-status.json', progress)
            with self.assertRaisesRegex(ValueError, 'GLOBAL_STOP_REQUIRES_INSPECTION'):
                run.collect(root, resume=True, provider_factory=lambda cfg, study: resumed)


class FakeProvider:
    def __init__(self, config, raw_action=None):
        self.config = config
        self.calls = 0
        self.raw_action = raw_action or json.dumps({'kind': 'final', 'tool': '', 'arguments_json': '{}', 'report_json': '{}'})

    def decide(self, messages, directory, timeout=1800):
        self.calls += 1
        directory.mkdir(parents=True, exist_ok=True)
        body = run.request_body(self.config, messages)
        (directory / 'prompt.txt').write_text(body['messages'][0]['content'], encoding='utf-8')
        run.write_json(directory / 'request-body.json', body)
        (directory / 'request-body.raw.json').write_bytes(json.dumps(body).encode())
        run.write_json(directory / 'response.json', {'id': 'fixture-' + str(self.calls), 'model': self.config['model'],
            'content': [{'type': 'text', 'text': self.raw_action}], 'stop_reason': 'end_turn',
            'usage': {'input_tokens': 1, 'output_tokens': 1}})
        return run.response_value(directory, self.config)


if __name__ == '__main__':
    (ROOT / 'tests-temp').mkdir(exist_ok=True)
    unittest.main(verbosity=2)
