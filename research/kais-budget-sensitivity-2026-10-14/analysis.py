"""Offline reconstruction of the frozen 24-task, four-condition study.

No provider is invoked. Original score.json files are read and never modified.
The CLI writes only summary.json, analysis.json, cells.csv and pairs.csv.
"""
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys

ROOT = Path(__file__).resolve().parent
STUDY_ID = 'kais-budget-sensitivity-2026-10-14-v1'
CONDITIONS = {
    'CL': ('context', 'low', 4096), 'CH': ('context', 'high', 393216),
    'BL': ('bound', 'low', 4096), 'BH': ('bound', 'high', 393216),
}
SCENARIOS = ('E', 'G', 'L', 'N', 'R', 'V')
USAGE_FIELDS = ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens')
CONTRASTS = {
    'd_low': {'BL': 1, 'CL': -1},
    'd_high': {'BH': 1, 'CH': -1},
    'interaction': {'BH': 1, 'CH': -1, 'BL': -1, 'CL': 1},
    'budget_context': {'CH': 1, 'CL': -1},
    'budget_bound': {'BH': 1, 'BL': -1},
}
COST_FIELDS = ('suffix_elapsed_ms', 'agent_tool_calls', 'model_requests', 'model_responses',
               'external_retries', 'truncated_responses', 'suffix_format_repairs',
               'authorization_requests', 'reproposal_calls', 'receipt_calls')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def task_id(cell):
    return cell.get('task_id', cell.get('task_instance_id'))


def validate_allocation(allocation):
    cells = allocation.get('cells', [])
    if len(cells) != 96:
        raise ValueError('Allocation must retain exactly 96 planned cells')
    by_task, seen_paths = defaultdict(dict), set()
    for cell in cells:
        tid, condition = task_id(cell), cell.get('condition')
        if not tid or cell.get('scenario') not in SCENARIOS or condition not in CONDITIONS:
            raise ValueError('Unknown task, scenario or condition')
        if condition in by_task[tid]:
            raise ValueError('Duplicate task-condition cell')
        if (cell.get('policy'), cell.get('budget'), cell.get('max_tokens')) != CONDITIONS[condition]:
            raise ValueError('Condition/policy/budget mismatch')
        expected = f"live/{tid}/{cell['budget']}/{cell['policy']}"
        if cell.get('path', '').replace('\\', '/') != expected or expected in seen_paths:
            raise ValueError('Noncanonical or duplicate cell path')
        by_task[tid][condition] = cell
        seen_paths.add(expected)
    if len(by_task) != 24 or any(set(v) != set(CONDITIONS) for v in by_task.values()):
        raise ValueError('Expected 24 tasks, each with all four conditions')
    scenario_counts = Counter()
    for group in by_task.values():
        if len({c['scenario'] for c in group.values()}) != 1:
            raise ValueError('Within-task scenario mismatch')
        scenario_counts[next(iter(group.values()))['scenario']] += 1
    if dict(scenario_counts) != dict.fromkeys(SCENARIOS, 4):
        raise ValueError('Expected four tasks in each of six strata')
    listed = allocation.get('tasks')
    if listed is not None and (len(listed) != 24 or {task_id(t) for t in listed} != set(by_task)):
        raise ValueError('Task and cell manifests disagree')
    return {'planned_cells': 96, 'planned_tasks': 24, 'tasks_by_scenario': dict(scenario_counts)}


def task_contrasts(values):
    result = {}
    for name, coefficients in CONTRASTS.items():
        low = high = 0
        known = True
        for condition, coefficient in coefficients.items():
            value = values.get(condition)
            if value is None:
                known = False
                low += min(0, coefficient)
                high += max(0, coefficient)
            else:
                if value not in (0, 1):
                    raise ValueError('U must be binary or unknown')
                low += coefficient * value
                high += coefficient * value
        result[name] = low if known else None
        result[name + '_lower'] = low
        result[name + '_upper'] = high
    return result


def flatten_usage(record, prefix=''):
    flat = {}
    if isinstance(record, dict):
        for key, value in record.items():
            name = prefix + key
            if isinstance(value, dict):
                flat.update(flatten_usage(value, name + '.'))
            elif numeric(value):
                flat[name] = value
    return flat


def usage_summary(records):
    flat = [flatten_usage(r) for r in records]
    fields = set(USAGE_FIELDS).union(*(set(r) for r in flat))
    result = {}
    for field in sorted(fields):
        known = [r[field] for r in flat if field in r]
        complete = bool(records) and len(known) == len(records)
        result[field] = {'total': sum(known) if complete else None,
                         'observed_sum': sum(known) if known else None,
                         'known_records': len(known), 'missing_records': len(records) - len(known),
                         'records': len(records), 'complete': complete}
    return result


def independent_scorer(directory):
    vendor = ROOT / 'vendor' / 'src'
    if not vendor.exists():
        raise RuntimeError('Isolated scorer not available: vendor/src')
    sys.path.insert(0, str(vendor))
    from phase2 import runner
    if not Path(runner.__file__).resolve().is_relative_to(vendor.resolve()):
        raise RuntimeError('A non-isolated phase2.scorer was already imported')
    return runner.score_run(directory)


def _read_events(folder):
    file = folder / 'events.jsonl'
    if not file.exists():
        return [], []
    events, errors = [], []
    for index, line in enumerate(file.read_text(encoding='utf-8-sig').splitlines()):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError('not an object')
            events.append(event)
        except ValueError:
            errors.append('event_json_invalid:' + str(index + 1))
    return events, errors


def _read_checked(path, errors, label):
    if not path.exists():
        errors.append(label + '_missing')
        return None
    try:
        return read_json(path)
    except (ValueError, OSError, UnicodeError):
        errors.append(label + '_invalid')
        return None


def _attempt_key(event):
    payload = event.get('payload', {})
    match = re.search(r':model-(\d+)$', payload.get('model_request_id', ''))
    if not match:
        relative = payload.get('messages_ref', {}).get('relative_path', '')
        match = re.search(r'(\d+)\.json$', relative)
    return (int(match.group(1)), int(event.get('attempt_index', 0))) if match else None


def _repair_count(messages):
    return sum(isinstance(m, dict) and m.get('kind') == 'format_error' for m in messages) if isinstance(messages, list) else 0


def audit_provenance(root, cell, folder, events):
    errors = []
    protocol = root / 'PROTOCOL.md'
    if protocol.exists():
        expected_protocol = hashlib.sha256(protocol.read_bytes()).hexdigest()
        if any(e.get('protocol_sha256') != expected_protocol for e in events):
            errors.append('suffix_protocol_mismatch')
    else:
        expected_protocol = None
        errors.append('study_protocol_missing')
    if any(e.get('freeze_id') != STUDY_ID for e in events):
        errors.append('suffix_freeze_mismatch')
    expected_run_id = task_id(cell) + '-B-' + cell['policy']
    if any(e.get('run_id') != expected_run_id for e in events):
        errors.append('suffix_run_identity_mismatch')
    configs = _read_checked(root / 'configs.json', errors, 'study_configs')
    config = configs.get(cell['budget']) if isinstance(configs, dict) else None
    manifest = _read_checked(folder / 'arm-manifest.json', errors, 'arm_manifest')
    if isinstance(config, dict):
        if config.get('freeze_id') != STUDY_ID:
            errors.append('config_freeze_mismatch')
        if config.get('max_output_tokens') != cell['max_tokens'] or config.get('id') != 'B':
            errors.append('config_condition_mismatch')
        config_hash = hashlib.sha256(json_text(config).encode('utf-8')).hexdigest()
        if any(e.get('agent_config_sha256') != config_hash for e in events):
            errors.append('suffix_config_hash_mismatch')
        if isinstance(manifest, dict) and manifest.get('config') != config:
            errors.append('arm_manifest_config_mismatch')
    else:
        errors.append('budget_config_missing')
    if isinstance(manifest, dict):
        if manifest.get('cell') != cell:
            errors.append('arm_manifest_allocation_mismatch')
        if manifest.get('protocol_sha256') != expected_protocol:
            errors.append('arm_manifest_protocol_mismatch')
        if manifest.get('study_id') != STUDY_ID:
            errors.append('arm_manifest_study_mismatch')
        init = next((e for e in events if e.get('event_type') == 'initialization'), None)
        if init and manifest.get('checkpoint_sha256') != init.get('payload', {}).get('checkpoint_state_sha256'):
            errors.append('arm_manifest_checkpoint_mismatch')
    return errors


def audit_raw(folder, cell, events, terminated):
    errors, attempts, raw_usage = [], [], []
    requests, outcomes = {}, {}
    for event in events:
        if event.get('event_type') in ('model_request', 'model_response', 'model_error'):
            key = _attempt_key(event)
            if key is None:
                errors.append('request_identity_unreadable')
                continue
            if event['event_type'] == 'model_request':
                if key in requests:
                    errors.append('duplicate_request:' + str(key))
                requests[key] = event
            else:
                if key in outcomes:
                    errors.append('duplicate_provider_outcome:' + str(key))
                outcomes[key] = event
    for key in sorted(set(requests) | set(outcomes)):
        label = f'{key[0]}-{key[1]}'
        raw = folder / 'provider-raw' / label
        request, outcome = requests.get(key), outcomes.get(key)
        attempt = {'decision_index': key[0], 'transport_attempt': key[1], 'path': str(raw.relative_to(folder)),
                   'outcome': outcome.get('event_type') if outcome else None, 'stop_reason': None, 'usage': None}
        if request is None:
            errors.append('request_event_missing:' + label)
        completed_attempt = outcome is not None or terminated
        body_file = raw / 'request-body.json'
        body = _read_checked(body_file, errors, 'request_body:' + label) if completed_attempt or body_file.exists() else None
        if isinstance(body, dict):
            attempt['requested_max_tokens'] = body.get('max_tokens')
            attempt['requested_model'] = body.get('model')
            if body.get('max_tokens') != cell['max_tokens']:
                errors.append('request_budget_mismatch:' + label)
            if body.get('model') != 'deepseek-v4-flash':
                errors.append('request_model_mismatch:' + label)
            if body.get('temperature') != 0:
                errors.append('request_temperature_mismatch:' + label)
            wire = _read_checked(raw / 'request-body.raw.json', errors, 'wire_request:' + label)
            if wire is not None and wire != body:
                errors.append('wire_request_json_mismatch:' + label)
            prompt = raw / 'prompt.txt'
            if prompt.exists() and body.get('messages') != [{'role': 'user', 'content': prompt.read_text(encoding='utf-8')}]:
                errors.append('wire_prompt_mismatch:' + label)
        if outcome and outcome['event_type'] == 'model_response':
            response = _read_checked(raw / 'response.json', errors, 'raw_response:' + label)
            if response is None:
                errors.append('raw_response_missing:' + label)
            elif not isinstance(response, dict) or not isinstance(response.get('content'), list):
                errors.append('raw_response_envelope_invalid:' + label)
                response = None
            if response is not None:
                try:
                    text = ''.join(b.get('text', '') for b in response['content'] if b.get('type') == 'text')
                except (AttributeError, TypeError):
                    errors.append('raw_response_text_invalid:' + label)
                    text = None
                payload = outcome['payload']
                if text != payload.get('response'):
                    errors.append('response_text_mismatch:' + label)
                if response.get('usage', {}) != payload.get('usage'):
                    errors.append('response_usage_mismatch:' + label)
                if response.get('model') != payload.get('returned_model'):
                    errors.append('response_model_mismatch:' + label)
                if response.get('model') != 'deepseek-v4-flash':
                    errors.append('response_model_unexpected:' + label)
                if response.get('id') != payload.get('provider_request_id'):
                    errors.append('response_id_mismatch:' + label)
                binary = raw / 'response-body.bin'
                if not binary.exists():
                    errors.append('response_wire_bytes_missing:' + label)
                elif binary.read_bytes() != (raw / 'response.json').read_bytes():
                    errors.append('response_wire_bytes_mismatch:' + label)
                metadata = _read_checked(raw / 'response-metadata.json', errors, 'response_metadata:' + label)
                if isinstance(metadata, dict):
                    for field in ('stop_reason', 'usage'):
                        if field in metadata and metadata[field] != response.get(field):
                            errors.append('response_metadata_mismatch:' + label + ':' + field)
                    if metadata.get('raw_sha256') != hashlib.sha256((raw / 'response.json').read_bytes()).hexdigest():
                        errors.append('response_metadata_hash_mismatch:' + label)
                attempt.update({'stop_reason': response.get('stop_reason'), 'usage': response.get('usage'),
                                'returned_model': response.get('model'), 'response_text_bytes': len((text or '').encode('utf-8'))})
                if not isinstance(response.get('stop_reason'), str):
                    errors.append('stop_reason_missing:' + label)
        elif outcome:
            attempt['error_code'] = outcome.get('payload', {}).get('error_code')
        elif terminated:
            errors.append('provider_outcome_missing:' + label)
        attempts.append(attempt)
        # An error/pending transport may incur unobserved provider usage: never zero-fill it.
        raw_usage.append(attempt['usage'])
    last_outcome = next((e for e in reversed(events) if e.get('event_type') in ('model_response', 'model_error')), None)
    response_attempts = [a for a in attempts if a['outcome'] == 'model_response']
    last_response = response_attempts[-1] if response_attempts else None
    final_truncated = (last_response['stop_reason'] == 'max_tokens') if last_response and last_response['stop_reason'] is not None else None
    final_outcome_truncated = final_truncated if last_outcome and last_outcome['event_type'] == 'model_response' else (False if last_outcome else None)
    result = {'attempts': attempts, 'usage': usage_summary(raw_usage),
              'usage_received_responses': usage_summary([a['usage'] for a in response_attempts]),
              'stop_reasons': dict(Counter(a['stop_reason'] or 'unknown' for a in response_attempts)),
              'truncated_responses': sum(a['stop_reason'] == 'max_tokens' for a in response_attempts),
              'final_response_truncated': final_truncated,
              'final_provider_outcome_truncated': final_outcome_truncated,
              'external_retries': sum(key[1] > 0 for key in requests),
              'request_budget_values': sorted({a['requested_max_tokens'] for a in attempts if 'requested_max_tokens' in a}),
              'returned_models': sorted({a['returned_model'] for a in attempts if a.get('returned_model')}),
              'audit_errors': errors}
    return result


def analyze_cell(root, cell, scorer=None):
    root = Path(root)
    folder = root / cell['path']
    row = {**cell, 'task_id': task_id(cell), 'status': 'not_started', 'terminated': False,
           'U': None, 'I': 'unknown', 'state_goal': None, 'terminal': None,
           'suffix_elapsed_ms': None, 'observed_elapsed_ms': None,
           **{field: None for field in COST_FIELDS if field != 'suffix_elapsed_ms'},
           'prefix_format_repairs': None, 'truncated_responses': None,
           'final_response_truncated': None, 'final_provider_outcome_truncated': None,
           'recovery_path': None, 'episodes': [], 'audit_errors': [], 'audit_pending': [],
           'usage': usage_summary([]), 'usage_received_responses': usage_summary([]), 'attempts': []}
    events, read_errors = _read_events(folder)
    if not events:
        if folder.exists():
            row['status'] = 'incomplete'
            row['audit_pending'] = ['events_unavailable']
            row['audit_errors'] = read_errors
        return row
    term = next((e for e in reversed(events) if e.get('event_type') == 'termination'), None)
    row.update({'status': 'terminated' if term else 'incomplete', 'terminated': bool(term),
                'terminal': term.get('payload', {}).get('terminal_class') if term else None,
                'observed_elapsed_ms': events[-1].get('elapsed_ms'),
                'suffix_elapsed_ms': events[-1].get('elapsed_ms') if term else None})
    errors = read_errors + audit_provenance(root, cell, folder, events)
    try:
        rebuilt = (scorer or independent_scorer)(folder)
    except Exception as exc:
        errors.append('independent_score_failed:' + type(exc).__name__ + ':' + str(exc))
        rebuilt = None
    if rebuilt is not None:
        expected_incomplete = ('termination_missing', 'final_state_missing', 'db_final_snapshot_mismatch')
        for error in rebuilt.get('audit_errors', []):
            target = row['audit_pending'] if not term and error in expected_incomplete else errors
            target.append('score:' + error)
        row['independent_score'] = rebuilt
        row['violations'] = rebuilt.get('violations', [])
        if term:
            raw_u = rebuilt.get('task_completion')
            row['U'] = int(raw_u) if raw_u in (True, False, 0, 1) else None
            row['I'] = rebuilt.get('I', 'unknown')
            row['state_goal'] = rebuilt.get('state_goal')
        row['recovery_path'] = rebuilt.get('recovery_path')
        row['episodes'] = rebuilt.get('episodes', [])
        row['failure_labels'] = rebuilt.get('failure_labels', [])
        stored = folder / 'score.json'
        if stored.exists():
            saved = _read_checked(stored, errors, 'stored_score')
            if saved is not None and json_text(saved) != json_text(rebuilt):
                errors.append('stored_score_mismatch')
        elif term:
            errors.append('stored_score_missing')
    raw = audit_raw(folder, cell, events, bool(term))
    errors.extend(raw.pop('audit_errors'))
    row.update(raw)
    row['model_requests'] = sum(e.get('event_type') == 'model_request' for e in events)
    row['model_responses'] = sum(e.get('event_type') == 'model_response' for e in events)
    agent_calls = [e for e in events if e.get('event_type') == 'tool_call' and e.get('origin') == 'agent']
    row['agent_tool_calls'] = len(agent_calls)
    for column, tool in [('authorization_requests', 'request_authorization'), ('reproposal_calls', 'propose'), ('receipt_calls', 'get_receipt')]:
        row[column] = sum(e.get('payload', {}).get('tool_name') == tool for e in agent_calls)
    prefix_path = root / cell.get('prefix_path', str(Path(cell['path']).parent / 'prefix'))
    conversation = _read_checked(prefix_path / 'checkpoint-conversation.json', errors, 'prefix_conversation')
    if isinstance(conversation, list):
        inherited = _repair_count(conversation)
        row['prefix_format_repairs'] = inherited
        counts = [inherited]
        for event in events:
            if event.get('event_type') != 'model_request':
                continue
            ref = event.get('payload', {}).get('messages_ref', {}).get('relative_path')
            if ref and (folder / ref).exists():
                try:
                    counts.append(_repair_count(read_json(folder / ref)))
                except (ValueError, OSError):
                    errors.append('messages_unreadable:' + ref)
        boundary = folder / 'safe-boundary.json'
        if boundary.exists():
            try:
                counts.append(_repair_count(read_json(boundary).get('messages', [])))
            except (ValueError, OSError, AttributeError):
                errors.append('safe_boundary_unreadable')
        row['suffix_format_repairs'] = max(counts) - inherited
        if max(counts) > 1:
            errors.append('format_repair_limit_exceeded')
    row['audit_errors'] = sorted(set(errors))
    row['audit_pass'] = bool(term) and not row['audit_errors']
    return row


def build_pairs(cells):
    groups = defaultdict(dict)
    for cell in cells:
        groups[task_id(cell)][cell['condition']] = cell
    rows = []
    usage_fields = set(USAGE_FIELDS).union(*(set(c.get('usage', {})) for c in cells))
    for tid, group in groups.items():
        row = {'task_id': tid, 'scenario': next(iter(group.values()))['scenario'],
               'planned_cells': len(group), 'terminated_cells': sum(c.get('status') == 'terminated' for c in group.values()),
               'known_U_cells': sum(c.get('U') is not None for c in group.values())}
        row.update(task_contrasts({condition: group.get(condition, {}).get('U') for condition in CONDITIONS}))
        for condition in CONDITIONS:
            for field in ('U', 'I', 'state_goal', 'status', 'terminal', 'audit_errors', *COST_FIELDS):
                row[field + '_' + condition] = group.get(condition, {}).get(field)
        for name, first, second in [('low', 'CL', 'BL'), ('high', 'CH', 'BH'),
                                     ('budget_context', 'CL', 'CH'), ('budget_bound', 'BL', 'BH')]:
            both_terminated = all(group.get(condition, {}).get('status') == 'terminated' for condition in (first, second))
            for metric in COST_FIELDS:
                a, b = group.get(first, {}).get(metric), group.get(second, {}).get(metric)
                row['delta_' + name + '_' + metric] = b - a if both_terminated and numeric(a) and numeric(b) else None
            for field in sorted(usage_fields):
                a = group.get(first, {}).get('usage', {}).get(field, {}).get('total')
                b = group.get(second, {}).get('usage', {}).get(field, {}).get('total')
                row['delta_' + name + '_usage_' + field] = b - a if both_terminated and numeric(a) and numeric(b) else None
        rows.append(row)
    return rows


def _descriptive(values, planned=None):
    known = [v for v in values if numeric(v)]
    return {'planned': len(values) if planned is None else planned, 'known': len(known),
            'sum': sum(known) if len(known) == len(values) and known else None,
            'observed_sum': sum(known) if known else None,
            'mean': statistics.mean(known) if len(known) == len(values) and known else None,
            'minimum_observed': min(known) if known else None,
            'maximum_observed': max(known) if known else None,
            'median_observed': statistics.median(known) if known else None}


def _contrast_group(pairs):
    result = {'planned_tasks': len(pairs)}
    for contrast in CONTRASTS:
        values = [p[contrast] for p in pairs]
        known = [v for v in values if v is not None]
        result[contrast] = {'planned_tasks': len(pairs), 'known_tasks': len(known),
                            'mean': statistics.mean(known) if len(known) == len(pairs) and known else None,
                            'mean_lower': statistics.mean(p[contrast + '_lower'] for p in pairs) if pairs else None,
                            'mean_upper': statistics.mean(p[contrast + '_upper'] for p in pairs) if pairs else None,
                            'known_sum': sum(known), 'minimum_observed': min(known) if known else None,
                            'maximum_observed': max(known) if known else None,
                            'all_observed_identical': bool(known) and len(set(known)) == 1}
    return result


def _condition_group(cells):
    n = len(cells)
    known = [c['U'] for c in cells if c.get('U') is not None]
    return {'planned_cells': n, 'terminated_cells': sum(c.get('status') == 'terminated' for c in cells),
            'known_U': len(known), 'successes_known': sum(known),
            'U_mean': sum(known) / n if n and len(known) == n else None,
            'U_mean_lower': sum(known) / n if n else None,
            'U_mean_upper': (sum(known) + n - len(known)) / n if n else None,
            'I_counts': dict(Counter(str(c.get('I', 'unknown')) for c in cells)),
            'terminal_counts': dict(Counter(c.get('terminal') or c.get('status', 'unknown') for c in cells)),
            'recovery_paths': dict(Counter(c.get('recovery_path') or 'none' for c in cells if c.get('status') == 'terminated')),
            'costs_all_planned_cells': {field: _descriptive([c.get(field) if c.get('status') == 'terminated' else None for c in cells]) for field in COST_FIELDS},
            'usage': {field: _descriptive([c.get('usage', {}).get(field, {}).get('total') if c.get('status') == 'terminated' else None for c in cells])
                      for field in sorted(set(USAGE_FIELDS).union(*(set(c.get('usage', {})) for c in cells)))}}


def summarize(cells, pairs):
    result = {'analysis_version': 'kais-budget-sensitivity-analysis-v1', 'planned_cells': len(cells),
              'planned_tasks': len(pairs), 'terminated_cells': sum(c.get('status') == 'terminated' for c in cells),
              'not_started_cells': sum(c.get('status') == 'not_started' for c in cells),
              'incomplete_cells': sum(c.get('status') == 'incomplete' for c in cells),
              'audit_error_cells': sum(bool(c.get('audit_errors')) for c in cells),
              'overall': _contrast_group(pairs),
              'conditions': {condition: _condition_group([c for c in cells if c['condition'] == condition]) for condition in CONDITIONS},
              'scenarios': {},
              'inference': 'Descriptive task-level contrasts and missing-outcome identification bounds; no p-values or equivalence claims.',
              'estimand': '24 archived-checkpoint tasks, equally weighted; six scenarios equally weighted; continuation only.',
              'elapsed_definition': 'Actual new suffix wall-clock elapsed time for every terminated arm, including failures; no 720-second cap.',
              'usage_definition': 'Each provider attempt has field-specific completeness; error or pending attempts are unknown, never zero.',
              'bounds_definition': 'Unknown binary U ranges over [0,1]; contrast bounds averaged over all planned tasks; these are not confidence intervals.',
              'warning': 'Single run per task-condition; identical observations do not establish zero effect, equivalence, or general recovery probability.'}
    for scenario in SCENARIOS:
        chosen = [p for p in pairs if p['scenario'] == scenario]
        result['scenarios'][scenario] = _contrast_group(chosen)
        result['scenarios'][scenario]['conditions'] = {
            condition: _condition_group([c for c in cells if c['scenario'] == scenario and c['condition'] == condition])
            for condition in CONDITIONS}
    result['pair_cost_deltas'] = {
        key: _descriptive([p.get(key) for p in pairs]) for key in sorted({k for p in pairs for k in p if k.startswith('delta_')})}
    return result


def audit_budget_pair_inputs(root, cells):
    groups, errors = defaultdict(dict), []
    for cell in cells:
        groups[(task_id(cell), cell['policy'])][cell['budget']] = cell
    tasks = defaultdict(list)
    for cell in cells:
        tasks[task_id(cell)].append(cell)
    for tid, selected in tasks.items():
        prefixes = {Path(root) / c.get('prefix_path', str(Path(c['path']).parent / 'prefix')) for c in selected}
        for filename, error in [('state/checkpoint.json', 'checkpoint_state_mismatch'),
                                ('checkpoint-conversation.json', 'checkpoint_conversation_mismatch'),
                                ('state.sqlite', 'checkpoint_database_mismatch')]:
            existing = [prefix / filename for prefix in prefixes if (prefix / filename).exists()]
            if len(existing) > 1 and len({hashlib.sha256(path.read_bytes()).hexdigest() for path in existing}) != 1:
                errors.append(error + ':' + tid)
        checkpoint_hashes = set()
        for cell in selected:
            events, _ = _read_events(Path(root) / cell['path'])
            init = next((e for e in events if e.get('event_type') == 'initialization'), None)
            if init:
                checkpoint_hashes.add((init.get('payload', {}).get('checkpoint_state_sha256'),
                                       init.get('payload', {}).get('checkpoint_conversation_sha256')))
        if len(checkpoint_hashes) > 1:
            errors.append('four_arm_checkpoint_mismatch:' + tid)
    for (tid, policy), group in groups.items():
        if set(group) != {'low', 'high'}:
            continue
        folders = {budget: Path(root) / c['path'] for budget, c in group.items()}
        wire = {budget: folder / 'provider-raw/0-0/request-body.json' for budget, folder in folders.items()}
        if all(file.exists() for file in wire.values()):
            try:
                bodies = {budget: read_json(file) for budget, file in wire.items()}
                for body in bodies.values():
                    body.pop('max_tokens', None)
                if bodies['low'] != bodies['high']:
                    errors.append('first_wire_body_mismatch:' + tid + ':' + policy)
            except (ValueError, AttributeError):
                errors.append('first_wire_body_unreadable:' + tid + ':' + policy)
        messages = {budget: folder / 'model-inputs/0.json' for budget, folder in folders.items()}
        if all(file.exists() for file in messages.values()):
            if messages['low'].read_bytes() != messages['high'].read_bytes():
                errors.append('first_visible_messages_mismatch:' + tid + ':' + policy)
    return errors


def _write_csv(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json_text(value) if isinstance(value, (dict, list)) else value for key, value in row.items()})


def analyze(root=ROOT, scorer=None):
    root = Path(root)
    allocation_file = root / 'allocation.json'
    allocation = read_json(allocation_file)
    validated = validate_allocation(allocation)
    cells = [analyze_cell(root, c, scorer=scorer) for c in allocation['cells']]
    pairs = build_pairs(cells)
    summary = summarize(cells, pairs)
    summary.update({'allocation_sha256': hashlib.sha256(allocation_file.read_bytes()).hexdigest(),
                    'allocation_validation': validated, 'pair_input_audit_errors': audit_budget_pair_inputs(root, allocation['cells']),
                    'generated_utc': datetime.now(timezone.utc).isoformat()})
    summary['all_planned_terminated'] = summary['terminated_cells'] == 96
    summary['audit_pass'] = summary['all_planned_terminated'] and not summary['audit_error_cells'] and not summary['pair_input_audit_errors']
    (root / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    (root / 'analysis.json').write_text(json.dumps({'summary': summary, 'cells': cells, 'pairs': pairs}, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    _write_csv(root / 'cells.csv', [{k: v for k, v in c.items() if k not in ('independent_score', 'attempts')} for c in cells])
    _write_csv(root / 'pairs.csv', pairs)
    return summary


if __name__ == '__main__':
    result = analyze()
    print(json.dumps({key: result[key] for key in ('planned_cells', 'planned_tasks', 'terminated_cells',
                     'not_started_cells', 'incomplete_cells', 'audit_error_cells', 'pair_input_audit_errors', 'audit_pass')}, ensure_ascii=False))
