"""Offline tests only. All fixture writes are isolated in TemporaryDirectory."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('budget_analysis', HERE / 'analysis.py')
if (HERE / 'analysis.py').exists():
    analysis = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(analysis)
else:
    analysis = None


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')


def plan():
    cells, tasks = [], []
    for scenario in 'EGLNRV':
        for number in range(4):
            tid = f'FORMAL-{scenario}-{number + 1:03}'
            tasks.append({'task_id': tid, 'scenario': scenario})
            for condition, policy, budget, cap in (
                    ('CL', 'context', 'low', 4096), ('CH', 'context', 'high', 393216),
                    ('BL', 'bound', 'low', 4096), ('BH', 'bound', 'high', 393216)):
                cells.append({'task_id': tid, 'scenario': scenario, 'condition': condition,
                              'policy': policy, 'budget': budget, 'max_tokens': cap,
                              'path': f'live/{tid}/{budget}/{policy}',
                              'prefix_path': f'live/{tid}/{budget}/prefix'})
    return {'seed': 20261014, 'tasks': tasks, 'cells': cells}


def fixture(root, cell=None, terminal='agent_final', complete=True, elapsed=2300.0):
    cell = copy.deepcopy(cell or plan()['cells'][0])
    folder = root / cell['path']
    folder.mkdir(parents=True)
    prefix = root / cell['prefix_path']
    write_json(prefix / 'checkpoint-conversation.json', [{'kind': 'initial'}])
    messages = [{'kind': 'initial'}]
    write_json(folder / 'model-inputs' / '0.json', messages)
    text = json.dumps({'kind': 'final', 'report': {'record_id': 'fixture'}})
    body = {'model': 'deepseek-v4-flash', 'max_tokens': cell['max_tokens'],
            'temperature': 0, 'messages': [{'role': 'user', 'content': 'fixture prompt'}]}
    raw = folder / 'provider-raw' / '0-0'
    write_json(raw / 'request-body.json', body)
    write_json(raw / 'request-body.raw.json', body)
    (raw / 'prompt.txt').write_text('fixture prompt', encoding='utf-8')
    usage = {'input_tokens': 10, 'output_tokens': 20, 'cache_read_input_tokens': 0,
             'cache_creation_input_tokens': 0}
    response = {'id': 'response-1', 'model': 'deepseek-v4-flash', 'stop_reason': 'end_turn',
                'content': [{'type': 'text', 'text': text}], 'usage': usage}
    write_json(raw / 'response.json', response)
    (raw / 'response-body.bin').write_bytes((raw / 'response.json').read_bytes())
    write_json(raw / 'response-metadata.json', {'stop_reason': 'end_turn', 'usage': usage})
    req = {'event_type': 'model_request', 'sequence': 1, 'elapsed_ms': 10,
           'attempt_index': 0, 'payload': {'model_request_id': 'fixture:model-0',
               'requested_model': 'deepseek-v4-flash',
               'messages_ref': {'relative_path': 'model-inputs/0.json'}}}
    res = {'event_type': 'model_response', 'sequence': 2, 'elapsed_ms': 2000,
           'attempt_index': 0, 'payload': {'model_request_id': 'fixture:model-0',
               'provider_request_id': 'response-1', 'returned_model': 'deepseek-v4-flash',
               'response': text, 'usage': usage}}
    events = [req, res]
    if complete:
        events.append({'event_type': 'termination', 'sequence': 3, 'elapsed_ms': elapsed,
                       'payload': {'terminal_class': terminal}})
    (folder / 'events.jsonl').write_text('\n'.join(json.dumps(e) for e in events) + '\n', encoding='utf-8')
    score = {'task_completion': terminal == 'agent_final', 'I': 1, 'state_goal': True,
             'terminal': terminal, 'audit_errors': [], 'violations': [], 'elapsed_ms': elapsed,
             'recovery_path': None, 'episodes': []}
    if complete:
        write_json(folder / 'score.json', score)
    return cell, folder, score, events


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(analysis, 'The independently auditable analysis layer has not been implemented')

    def test_interaction_sign(self):
        row = analysis.task_contrasts({'CL': 1, 'CH': 0, 'BL': 0, 'BH': 1})
        self.assertEqual(row['d_low'], -1)
        self.assertEqual(row['d_high'], 1)
        self.assertEqual(row['interaction'], 2)
        self.assertEqual(row['budget_context'], -1)
        self.assertEqual(row['budget_bound'], 1)

    def test_missing_cell_has_identification_bounds(self):
        row = analysis.task_contrasts({'CL': 1, 'CH': None, 'BL': 0, 'BH': 1})
        self.assertIsNone(row['interaction'])
        self.assertEqual(row['interaction_lower'], 1)
        self.assertEqual(row['interaction_upper'], 2)

    def test_all_missing_not_failure(self):
        row = analysis.task_contrasts({})
        self.assertIsNone(row['d_low'])
        self.assertEqual((row['interaction_lower'], row['interaction_upper']), (-2, 2))

    def test_plan_validates_96_and_stratum_units(self):
        checked = analysis.validate_allocation(plan())
        self.assertEqual(checked['planned_cells'], 96)
        self.assertEqual(checked['planned_tasks'], 24)
        self.assertEqual(checked['tasks_by_scenario'], dict.fromkeys('EGLNRV', 4))

    def test_plan_rejects_duplicate_cell(self):
        allocation = plan()
        allocation['cells'][-1] = copy.deepcopy(allocation['cells'][0])
        with self.assertRaises(ValueError):
            analysis.validate_allocation(allocation)

    def test_plan_rejects_wrong_budget(self):
        allocation = plan()
        allocation['cells'][0]['max_tokens'] = 393216
        with self.assertRaises(ValueError):
            analysis.validate_allocation(allocation)

    def test_missing_usage_is_not_zero(self):
        result = analysis.usage_summary([{'input_tokens': 10, 'output_tokens': 3}, {'input_tokens': 12}])
        self.assertEqual(result['input_tokens']['total'], 22)
        self.assertIsNone(result['output_tokens']['total'])
        self.assertEqual(result['output_tokens']['observed_sum'], 3)
        self.assertEqual(result['output_tokens']['missing_records'], 1)
        self.assertIsNone(result['cache_read_input_tokens']['total'])

    def test_explicit_zero_usage_is_known(self):
        result = analysis.usage_summary([{'output_tokens': 0}])
        self.assertEqual(result['output_tokens']['total'], 0)
        self.assertTrue(result['output_tokens']['complete'])

    def test_no_response_usage_remains_unknown(self):
        self.assertIsNone(analysis.usage_summary([])['input_tokens']['total'])

    def test_nonstarted_cell_is_null(self):
        with tempfile.TemporaryDirectory() as d:
            row = analysis.analyze_cell(Path(d), plan()['cells'][0], scorer=lambda p: self.fail('scorer called'))
        self.assertEqual(row['status'], 'not_started')
        self.assertIsNone(row['U'])
        self.assertEqual(row['I'], 'unknown')
        self.assertIsNone(row['suffix_elapsed_ms'])

    def test_partial_cell_is_not_scored_failure(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, _ = fixture(Path(d), complete=False)
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertEqual(row['status'], 'incomplete')
        self.assertIsNone(row['U'])
        self.assertIsNone(row['suffix_elapsed_ms'])
        self.assertEqual(row['observed_elapsed_ms'], 2000)

    def test_failure_elapsed_retained_without_720_cap(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, _ = fixture(Path(d), terminal='invalid_output', elapsed=801000)
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertEqual(row['U'], 0)
        self.assertEqual(row['suffix_elapsed_ms'], 801000)

    def test_score_tamper_detected_without_rewriting(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, _ = fixture(Path(d))
            write_json(folder / 'score.json', {**score, 'task_completion': False})
            before = (folder / 'score.json').read_bytes()
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
            self.assertEqual(before, (folder / 'score.json').read_bytes())
        self.assertIn('stored_score_mismatch', row['audit_errors'])
        self.assertEqual(row['U'], 1)

    def test_independent_scorer_audit_errors_propagate(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, _ = fixture(Path(d))
            score['audit_errors'] = ['artifact:provider-raw/0-0/response.json']
            write_json(folder / 'score.json', score)
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertIn('score:artifact:provider-raw/0-0/response.json', row['audit_errors'])

    def test_missing_raw_response_detected(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, _ = fixture(Path(d))
            (folder / 'provider-raw/0-0/response.json').unlink()
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertTrue(any('raw_response_missing' in err for err in row['audit_errors']))
        self.assertIsNone(row['usage']['output_tokens']['total'])

    def test_wire_budget_mismatch_detected(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, _ = fixture(Path(d))
            file = folder / 'provider-raw/0-0/request-body.json'
            body = json.loads(file.read_text(encoding='utf-8'))
            body['max_tokens'] = 123
            write_json(file, body)
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertTrue(any('request_budget_mismatch' in err for err in row['audit_errors']))

    def test_raw_response_text_and_usage_mismatch_detected(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, events = fixture(Path(d))
            events[1]['payload']['response'] = 'altered'
            events[1]['payload']['usage']['output_tokens'] = 999
            (folder / 'events.jsonl').write_text('\n'.join(json.dumps(e) for e in events), encoding='utf-8')
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertTrue(any('response_text_mismatch' in err for err in row['audit_errors']))
        self.assertTrue(any('response_usage_mismatch' in err for err in row['audit_errors']))

    def test_final_truncation_and_format_repair_counted(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, _ = fixture(Path(d), terminal='invalid_output')
            file = folder / 'provider-raw/0-0/response.json'
            response = json.loads(file.read_text(encoding='utf-8'))
            response['stop_reason'] = 'max_tokens'
            write_json(file, response)
            (folder / 'provider-raw/0-0/response-body.bin').write_bytes(file.read_bytes())
            write_json(folder / 'safe-boundary.json', {'messages': [{'kind': 'initial'}, {'kind': 'format_error'}]})
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertEqual(row['truncated_responses'], 1)
        self.assertTrue(row['final_response_truncated'])
        self.assertEqual(row['suffix_format_repairs'], 1)

    def test_unknown_integrity_not_cast_to_bool(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, _ = fixture(Path(d))
            score['I'] = 'unknown'
            write_json(folder / 'score.json', score)
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertEqual(row['I'], 'unknown')

    def test_cost_deltas_include_negative_and_missing(self):
        cells = [dict(c, U=1, suffix_elapsed_ms=t, status='terminated', audit_errors=[], I=1,
                      state_goal=True, terminal='agent_final', usage={})
                 for c, t in zip(plan()['cells'][:4], [100, None, 40, 60])]
        row = analysis.build_pairs(cells)[0]
        self.assertEqual(row['delta_low_suffix_elapsed_ms'], -60)
        self.assertIsNone(row['delta_high_suffix_elapsed_ms'])

    def test_partial_arm_tool_counts_do_not_become_cost_deltas(self):
        cells = [dict(c, U=1, status='terminated', agent_tool_calls=3, usage={})
                 for c in plan()['cells'][:4]]
        cells[2].update(U=None, status='incomplete', agent_tool_calls=1)
        row = analysis.build_pairs(cells)[0]
        self.assertIsNone(row['delta_low_agent_tool_calls'])

    def test_wrong_protocol_and_old_freeze_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cell, folder, score, events = fixture(root)
            (root / 'PROTOCOL.md').write_text('new protocol', encoding='utf-8')
            config = {'id': 'B', 'freeze_id': 'kais-budget-sensitivity-2026-10-14-v1',
                      'max_output_tokens': 4096, 'model': 'deepseek-v4-flash', 'temperature': 0}
            write_json(root / 'configs.json', {'low': config})
            write_json(folder / 'arm-manifest.json', {'config': config, 'cell': cell})
            for event in events:
                event['protocol_sha256'] = 'old-protocol-hash'
                event['freeze_id'] = 'phase2-formal-v1.0'
            (folder / 'events.jsonl').write_text('\n'.join(json.dumps(e) for e in events), encoding='utf-8')
            row = analysis.analyze_cell(root, cell, scorer=lambda p: score)
        self.assertIn('suffix_protocol_mismatch', row['audit_errors'])
        self.assertIn('suffix_freeze_mismatch', row['audit_errors'])

    def test_checkpoint_mismatch_across_budgets_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for c in plan()['cells'][:2]:
                fixture(root, c)
                write_json(root / c['prefix_path'] / 'state/checkpoint.json', {'case': 'same'})
            write_json(root / plan()['cells'][1]['prefix_path'] / 'state/checkpoint.json', {'case': 'changed'})
            errors = analysis.audit_budget_pair_inputs(root, plan()['cells'][:2])
        self.assertTrue(any('checkpoint_state_mismatch' in err for err in errors))

    def test_suffix_failure_does_not_count_as_transport_retry(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, _ = fixture(Path(d), terminal='invalid_output')
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertEqual(row['external_retries'], 0)

    def test_missing_raw_keeps_truncation_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, _ = fixture(Path(d))
            (folder / 'provider-raw/0-0/response.json').unlink()
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertIsNone(row['final_response_truncated'])
        self.assertIsNone(row['final_provider_outcome_truncated'])

    def test_metadata_checksum_mismatch_detected(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, _ = fixture(Path(d))
            file = folder / 'provider-raw/0-0/response-metadata.json'
            meta = json.loads(file.read_text(encoding='utf-8'))
            meta['raw_sha256'] = 'incorrect'
            write_json(file, meta)
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertTrue(any('response_metadata_hash_mismatch' in err for err in row['audit_errors']))

    def test_transport_error_usage_is_unknown_not_free(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, events = fixture(Path(d), terminal='runtime_error')
            events[1] = {**events[1], 'event_type': 'model_error',
                         'payload': {'model_request_id': 'fixture:model-0', 'error_code': 'HTTP_500'}}
            (folder / 'events.jsonl').write_text('\n'.join(json.dumps(e) for e in events), encoding='utf-8')
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertIsNone(row['usage']['input_tokens']['total'])
        self.assertEqual(row['usage']['input_tokens']['missing_records'], 1)

    def test_prefix_format_repair_is_inherited(self):
        with tempfile.TemporaryDirectory() as d:
            cell, folder, score, _ = fixture(Path(d))
            messages = [{'kind': 'initial'}, {'kind': 'format_error'}]
            write_json(Path(d) / cell['prefix_path'] / 'checkpoint-conversation.json', messages)
            write_json(folder / 'model-inputs/0.json', messages)
            row = analysis.analyze_cell(Path(d), cell, scorer=lambda p: score)
        self.assertEqual(row['prefix_format_repairs'], 1)
        self.assertEqual(row['suffix_format_repairs'], 0)

    def test_full_plan_aggregate_interaction_is_task_weighted(self):
        cells = [dict(c, U={'CL': 1, 'CH': 0, 'BL': 0, 'BH': 1}[c['condition']],
                      status='terminated', audit_errors=[], I=1, usage={}) for c in plan()['cells']]
        result = analysis.summarize(cells, analysis.build_pairs(cells))
        self.assertEqual(result['overall']['interaction']['mean'], 2)
        self.assertEqual(result['overall']['interaction']['known_tasks'], 24)
        self.assertEqual(result['conditions']['CL']['known_U'], 24)

    def test_original_scorer_and_runner_offline_integration(self):
        # The response provider is a deterministic file-writing fixture; no credential/API path is called.
        import test_run
        run = test_run.run
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'PROTOCOL.md').write_bytes((HERE / 'PROTOCOL.md').read_bytes())
            allocation = run.build_allocation(run.source_tasks())
            cell = next(c for c in allocation['cells'] if c['scenario'] == 'G' and c['condition'] == 'BL')
            case = next(c for c in run.source_tasks() if c['task_instance_id'] == cell['task_id'])
            configs = run.make_configs()
            write_json(root / 'configs.json', configs)
            run.copy_prefix(cell, root)
            run.execute_arm(cell, case, test_run.FakeProvider(configs['low']), root)
            row = analysis.analyze_cell(root, cell)
        self.assertEqual(row['status'], 'terminated')
        self.assertEqual(row['U'], 0)
        self.assertEqual(row['I'], 1)
        self.assertEqual(row['audit_errors'], [])
        self.assertEqual(row['model_requests'], 1)
        self.assertEqual(row['usage']['output_tokens']['total'], 1)

    def test_aggregation_retains_missing_tasks_and_equal_strata(self):
        cells = [dict(c, U=None, suffix_elapsed_ms=None, status='not_started', audit_errors=[],
                      I='unknown', state_goal=None, terminal=None, usage={}) for c in plan()['cells']]
        cells[0]['U'] = 1
        rows = analysis.build_pairs(cells)
        result = analysis.summarize(cells, rows)
        self.assertEqual(result['planned_cells'], 96)
        self.assertEqual(result['planned_tasks'], 24)
        self.assertEqual(result['overall']['interaction']['planned_tasks'], 24)
        self.assertIsNone(result['overall']['interaction']['mean'])
        self.assertEqual(result['scenarios']['E']['planned_tasks'], 4)

    def test_first_wire_bodies_must_match_except_budget(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for c in plan()['cells'][:2]:
                fixture(root, c)
            errors = analysis.audit_budget_pair_inputs(root, plan()['cells'][:2])
            self.assertEqual(errors, [])
            file = root / plan()['cells'][1]['path'] / 'provider-raw/0-0/request-body.json'
            body = json.loads(file.read_text(encoding='utf-8'))
            body['messages'][0]['content'] = 'different history'
            write_json(file, body)
            errors = analysis.audit_budget_pair_inputs(root, plan()['cells'][:2])
        self.assertTrue(any('first_wire_body_mismatch' in err for err in errors))

    def test_analyze_empty_plan_exports_all_96_without_api(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_json(root / 'allocation.json', plan())
            result = analysis.analyze(root, scorer=lambda p: self.fail('scorer called'))
            self.assertEqual(result['planned_cells'], 96)
            self.assertTrue((root / 'cells.csv').exists())
            self.assertTrue((root / 'pairs.csv').exists())
            self.assertTrue((root / 'analysis.json').exists())
            self.assertEqual(json.loads((root / 'summary.json').read_text(encoding='utf-8'))['not_started_cells'], 96)


if __name__ == '__main__':
    unittest.main()
