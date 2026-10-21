"""Post-submission diagnostic. Standard library only; never calls a provider.

Run with python -B analysis.py. All writes are restricted to this script's directory.
The only evaluated frozen source is the isolated parse_action AST, with json only.
"""
import ast
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
FORMAL = ROOT / 'research/agent-policy-phase2-formal-2026-10-07'
RAW = FORMAL / 'formal-results'
SNAPSHOT = ROOT / 'research/phase2-results-snapshots/2026-10-07T021002Z/original-formal-analysis'
PARSER_SOURCE = FORMAL / 'src/phase2/providers.py'

def load_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def frozen_parser():
    tree = ast.parse(PARSER_SOURCE.read_text(encoding='utf-8-sig'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'parse_action')
    namespace = {'json': json}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(PARSER_SOURCE), 'exec'), namespace)
    return namespace['parse_action']

PARSE = frozen_parser()

def classify_response(obj):
    result = {'stop_reason': obj.get('stop_reason') if isinstance(obj, dict) else None,
              'truncated': False, 'text_chars': None, 'parseable': False,
              'action_kind': None, 'response_class': 'malformed_envelope', 'output_tokens': None}
    if not isinstance(obj, dict) or not isinstance(obj.get('content'), list):
        return result
    try:
        text = ''.join(b.get('text', '') for b in obj['content'] if b.get('type') == 'text')
    except (AttributeError, TypeError):
        return result
    result.update(text_chars=len(text), truncated=obj.get('stop_reason') == 'max_tokens',
                  output_tokens=obj.get('usage', {}).get('output_tokens'))
    try:
        action = PARSE(text)
        result.update(parseable=True, action_kind=action['kind'])
    except ValueError:
        pass
    subtype = 'parseable' if result['parseable'] else ('empty' if not text.strip() else 'nonparseable_text')
    if result['truncated']:
        result['response_class'] = 'max_tokens_' + subtype
    elif result['stop_reason'] == 'end_turn':
        result['response_class'] = 'natural_stop_' + ('nonparseable' if subtype == 'nonparseable_text' else subtype)
    else:
        result['response_class'] = 'other_stop_' + subtype
    return result

def terminal_diagnostic(terminal, attempts):
    if terminal != 'invalid_output':
        return terminal
    if not attempts:
        return 'invalid_output_unresolved'
    last = attempts[-1]
    if last.get('outcome_event_type') != 'model_response' or last.get('parseable'):
        return 'invalid_output_unresolved'
    if not last.get('truncated'):
        return 'invalid_output_other_last_response'
    prior_bad = any(a.get('outcome_event_type') == 'model_response' and not a.get('parseable') for a in attempts[:-1])
    suffix = '_after_format_repair' if prior_bad and last.get('format_repair_visible') else ''
    return 'invalid_output_after_output_truncation' + suffix

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rel(path):
    return path.relative_to(ROOT).as_posix()

def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))

def write_csv(name, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()})

def input_inventory():
    files = set()
    for directory in RAW.glob('*-B'):
        files.update(p for p in directory.rglob('*') if p.is_file())
    files.update(p for p in SNAPSHOT.iterdir() if p.suffix in ('.csv', '.json'))
    files.update(FORMAL / p for p in ('src/phase2/providers.py', 'src/phase2/runner.py',
        'frozen-formal/agent-config-manifest.json', 'frozen-formal/formal-task-manifest.json',
        'frozen-formal/source-version-hashes.json', 'frozen-formal/failure-handling.md'))
    return {rel(p): digest(p) for p in sorted(files)}

def scan_phase(pair_id, phase, cap, issues):
    directory = RAW / pair_id / phase
    event_path = directory / 'events.jsonl'
    events = [json.loads(line) for line in event_path.read_text(encoding='utf-8-sig').splitlines() if line] if event_path.exists() else []
    requests, outcomes = {}, {}
    for event in events:
        if event['event_type'] not in ('model_request', 'model_response', 'model_error'):
            continue
        step = int(event['payload']['model_request_id'].rsplit(':model-', 1)[1])
        key = (step, event['attempt_index'])
        target = requests if event['event_type'] == 'model_request' else outcomes
        if key in target:
            issues.append({'kind': 'duplicate_event_key', 'pair_id': pair_id, 'phase': phase, 'key': key})
        target[key] = event
    raw_dirs = {tuple(map(int, p.name.split('-'))): p for p in (directory / 'provider-raw').glob('*') if p.is_dir()}
    rows = []
    for step, attempt_index in sorted(requests.keys() | outcomes.keys() | raw_dirs.keys()):
        key = (step, attempt_index)
        request, outcome = requests.get(key), outcomes.get(key)
        raw_dir = raw_dirs.get(key, directory / 'provider-raw' / f'{step}-{attempt_index}')
        response_path = raw_dir / 'response.json'
        classification = {'response_class': 'no_complete_response', 'stop_reason': None, 'truncated': False,
                          'text_chars': None, 'parseable': None, 'action_kind': None, 'output_tokens': None}
        response_obj = None
        if response_path.exists():
            try:
                response_obj = load_json(response_path)
                classification = classify_response(response_obj)
            except (ValueError, UnicodeDecodeError):
                classification['response_class'] = 'invalid_json_envelope'
        message_path = directory / 'model-inputs' / f'{step}.json'
        messages = load_json(message_path) if message_path.exists() else []
        format_repair = any(m.get('kind') == 'format_error' for m in messages)
        error_path = raw_dir / 'transport-error.json'
        error_detail = load_json(error_path) if error_path.exists() else {}
        recorded_text_match = None
        if response_obj is not None and outcome and outcome['event_type'] == 'model_response':
            text = ''.join(b.get('text', '') for b in response_obj.get('content', []) if b.get('type') == 'text')
            recorded_text_match = text == outcome['payload']['response']
            if not recorded_text_match:
                issues.append({'kind': 'response_text_mismatch', 'path': rel(response_path)})
        for event in (request, outcome):
            if not event:
                continue
            for artifact in event.get('artifacts', []):
                path = (directory / artifact['relative_path']).resolve()
                if not path.is_file() or digest(path) != artifact['sha256']:
                    issues.append({'kind': 'event_artifact_mismatch', 'path': rel(path), 'event_id': event['event_id']})
        rows.append({'pair_id': pair_id, 'task_instance_id': pair_id[:-2], 'scenario': pair_id.split('-')[1],
            'phase': phase, 'policy': phase if phase != 'prefix' else 'shared_once',
            'decision_index': step, 'transport_attempt': attempt_index,
            'request_event_id': request['event_id'] if request else None,
            'request_sequence': request['sequence'] if request else None,
            'outcome_event_type': outcome['event_type'] if outcome else 'missing_outcome',
            'response_event_id': outcome['event_id'] if outcome and outcome['event_type'] == 'model_response' else None,
            'outcome_event_id': outcome['event_id'] if outcome else None,
            'request_timestamp_utc': request['timestamp_utc'] if request else None,
            'request_elapsed_ms': request['elapsed_ms'] if request else None,
            'outcome_elapsed_ms': outcome['elapsed_ms'] if outcome else None,
            'request_to_outcome_ms': outcome['elapsed_ms'] - request['elapsed_ms'] if request and outcome else None,
            'format_repair_visible': format_repair, 'request_output_cap': cap,
            'cap_evidence': 'frozen_config_and_provider_source_not_wire_capture',
            'request_input_path': rel(message_path) if message_path.exists() else None,
            'prompt_path': rel(raw_dir / 'prompt.txt') if (raw_dir / 'prompt.txt').exists() else None,
            'response_path': rel(response_path) if response_path.exists() else None,
            'raw_directory': rel(raw_dir), 'response_text_matches_event': recorded_text_match,
            'runtime_error_code': outcome['payload'].get('error_code') if outcome else None,
            'transport_error_detail': error_detail,
            'http_error_file': rel(raw_dir / 'http-error.txt') if (raw_dir / 'http-error.txt').exists() else None,
            'partial_response_bytes': (raw_dir / 'partial-response.bin').stat().st_size if (raw_dir / 'partial-response.bin').exists() else 0,
            **classification})
    received = [r for r in rows if r['outcome_event_type'] == 'model_response']
    for row in rows:
        row['is_last_request_in_phase'] = row is rows[-1]
        row['is_last_received_response_in_phase'] = bool(received) and row is received[-1]
    return rows, events

def main():
    before = input_inventory()
    baseline = OUT / 'inputs-sha256-before.json'
    if baseline.exists() and load_json(baseline) != before:
        raise RuntimeError('Input inventory differs from first audit; retain baseline and investigate.')
    if not baseline.exists():
        write_json(baseline.name, before)
    protocol_hash = digest(OUT / 'PROTOCOL.md')
    config = next(c for c in load_json(FORMAL / 'frozen-formal/agent-config-manifest.json')['configs'] if c['id'] == 'B')
    original = [r for r in read_csv(SNAPSHOT / 'table4-utility-friction.csv') if r['config_id'] == 'B']
    failures = {(r['pair_id'], r['policy']): r for r in read_csv(SNAPSHOT / 'failure-archaeology-all-arms.csv') if r['config_id'] == 'B'}
    assert len(original) == 256 and len({r['pair_id'] for r in original}) == 128
    assert len({(r['pair_id'], r['policy']) for r in original}) == 256
    issues, attempts, phase_rows, phase_events = [], [], {}, {}
    for pair_id in sorted({r['pair_id'] for r in original}):
        for phase in ('prefix', 'context', 'bound'):
            rows, events = scan_phase(pair_id, phase, config['max_output_tokens'], issues)
            attempts.extend(rows)
            phase_rows[pair_id, phase] = rows
            phase_events[pair_id, phase] = events
    arms = []
    for source in sorted(original, key=lambda r: (r['pair_id'], r['policy'])):
        pair_id, policy = source['pair_id'], source['policy']
        rows, events = phase_rows[pair_id, policy], phase_events[pair_id, policy]
        prefix = phase_rows[pair_id, 'prefix']
        score_path = RAW / pair_id / policy / 'score.json'
        score = load_json(score_path) if score_path.exists() else {}
        failure = failures.get((pair_id, policy), {})
        terminal = source['terminal']
        if score and (score['terminal'] != terminal or score['task_completion'] != (source['task_completion'] == 'True')):
            issues.append({'kind': 'original_score_table_mismatch', 'pair_id': pair_id, 'policy': policy})
        termination = [e for e in events if e['event_type'] == 'termination']
        if termination and termination[-1]['payload']['terminal_class'] != terminal:
            issues.append({'kind': 'termination_table_mismatch', 'pair_id': pair_id, 'policy': policy})
        last = rows[-1] if rows else {}
        bad = [r for r in rows if r['outcome_event_type'] == 'model_response' and not r['parseable']]
        last_received = next((r for r in reversed(rows) if r['outcome_event_type'] == 'model_response'), {})
        arms.append({**source, 'U': source['task_completion'] == 'True',
            'I': score.get('I', failure.get('I')), 'state_goal': score.get('state_goal'),
            'diagnostic_terminal': terminal_diagnostic(terminal, rows), 'termination_event_present': bool(termination),
            'suffix_provider_attempts': len(rows), 'suffix_received_responses': sum(r['outcome_event_type'] == 'model_response' for r in rows),
            'suffix_truncated_responses': sum(r['truncated'] for r in rows),
            'suffix_transport_retries': sum(r['transport_attempt'] > 0 for r in rows),
            'suffix_model_error_events': sum(r['outcome_event_type'] == 'model_error' for r in rows),
            'suffix_missing_outcome_requests': sum(r['outcome_event_type'] == 'missing_outcome' for r in rows),
            'prefix_truncated_responses_shared': sum(r['truncated'] for r in prefix),
            'last_request_decision': last.get('decision_index'), 'last_request_outcome': last.get('outcome_event_type'),
            'last_response_class': last_received.get('response_class'), 'last_response_event_id': last_received.get('response_event_id'),
            'last_response_path': last_received.get('response_path'), 'last_response_format_repair_visible': last_received.get('format_repair_visible'),
            'nonparseable_response_events': [r['response_event_id'] for r in bad],
            'nonparseable_response_classes': [r['response_class'] for r in bad],
            'parseable_responses_between_bad': sum(r['parseable'] is True and bad and bad[0]['decision_index'] < r['decision_index'] < bad[-1]['decision_index'] for r in rows) if bad else 0,
            'runtime_error_codes': [r['runtime_error_code'] for r in rows if r['runtime_error_code']],
            'events_path': rel(RAW / pair_id / policy / 'events.jsonl'),
            'score_path': rel(score_path) if score_path.exists() else None})
    by_pair = {pid: {a['policy']: a for a in arms if a['pair_id'] == pid} for pid in sorted({a['pair_id'] for a in arms})}
    pairs = []
    for pid, group in by_pair.items():
        c, b = group['context'], group['bound']
        c_hit, b_hit = c['suffix_truncated_responses'] > 0, b['suffix_truncated_responses'] > 0
        position = 'both' if c_hit and b_hit else ('context_only' if c_hit else ('bound_only' if b_hit else 'neither'))
        c_failure = c['diagnostic_terminal'].startswith('invalid_output_after_output_truncation')
        b_failure = b['diagnostic_terminal'].startswith('invalid_output_after_output_truncation')
        failure_position = 'both' if c_failure and b_failure else ('context_only' if c_failure else ('bound_only' if b_failure else 'neither'))
        row = {'pair_id': pid, 'scenario': c['scenario'], 'truncation_position': position,
               'terminal_truncation_position': failure_position, 'U_delta_bound_minus_context': int(b['U']) - int(c['U'])}
        for arm in (c, b):
            for key in ('U', 'I', 'terminal', 'diagnostic_terminal', 'suffix_truncated_responses', 'suffix_agent_tool_calls', 'suffix_model_turns', 'suffix_elapsed_ms'):
                row[arm['policy'] + '_' + key] = arm[key]
        for key in ('suffix_agent_tool_calls', 'suffix_model_turns', 'suffix_elapsed_ms'):
            row[key + '_delta_bound_minus_context'] = float(b[key]) - float(c[key]) if b[key] != '' and c[key] != '' else None
        pairs.append(row)
    write_csv('attempts.csv', attempts)
    write_csv('arms.csv', arms)
    write_csv('pairs.csv', pairs)
    write_csv('invalid-output-arms.csv', [a for a in arms if a['terminal'] == 'invalid_output'])
    summary = {'status': 'post_submission_offline_diagnostic', 'protocol_sha256': protocol_hash,
        'planned_arms_original_all_configurations': 512, 'B_planned_arms': 256, 'B_pairs': 128, 'shared_prefixes_counted_once': 128,
        'provider_attempts': len(attempts), 'provider_requests_recorded': sum(bool(r['request_event_id']) for r in attempts),
        'attempts_by_phase': dict(Counter(r['phase'] for r in attempts)),
        'raw_responses': sum(bool(r['response_path']) for r in attempts),
        'response_classes': dict(Counter(r['response_class'] for r in attempts)),
        'outcome_event_types': dict(Counter(r['outcome_event_type'] for r in attempts)),
        'runtime_error_codes': dict(Counter(r['runtime_error_code'] for r in attempts if r['runtime_error_code'])),
        'transport_retries': sum(r['transport_attempt'] > 0 for r in attempts),
        'prefix_truncations': sum(r['truncated'] for r in attempts if r['phase'] == 'prefix'),
        'suffix_truncations': sum(r['truncated'] for r in attempts if r['phase'] != 'prefix'),
        'suffix_truncations_with_parseable_actions': sum(r['truncated'] and r['parseable'] for r in attempts if r['phase'] != 'prefix'),
        'arm_terminals': dict(Counter(a['terminal'] for a in arms)),
        'arm_diagnostic_terminals': dict(Counter(a['diagnostic_terminal'] for a in arms)),
        'policy': {}, 'paired_decomposition': {}, 'terminal_paired_decomposition': {}, 'audit_issues': issues,
        'truncated_arms_by_terminal': dict(Counter(a['terminal'] for a in arms if a['suffix_truncated_responses'])),
        'invalid_output_last_response_classes': dict(Counter(a['last_response_class'] for a in arms if a['terminal'] == 'invalid_output')),
        'invalid_output_parseable_responses_between_bad': dict(Counter(a['parseable_responses_between_bad'] for a in arms if a['terminal'] == 'invalid_output')),
        'wire_request_body_available': False, 'output_cap_source': 'frozen configuration and adapter source',
        'limits': ['No exclusion/re-scoring/re-running', 'No counterfactual unbounded U', 'Post-treatment strata are descriptive only', 'Tool counts may be curtailed by incomplete reasoning output; failed arms remain included']}
    for policy in ('context', 'bound'):
        group = [a for a in arms if a['policy'] == policy]
        summary['policy'][policy] = {'arms': len(group), 'U': sum(a['U'] for a in group),
            'invalid_output': sum(a['terminal'] == 'invalid_output' for a in group),
            'arms_with_suffix_truncation': sum(a['suffix_truncated_responses'] > 0 for a in group),
            'suffix_truncated_responses': sum(a['suffix_truncated_responses'] for a in group)}
    for position in ('neither', 'context_only', 'bound_only', 'both'):
        group = [p for p in pairs if p['truncation_position'] == position]
        summary['paired_decomposition'][position] = {'pairs': len(group), 'U_delta_sum_bound_minus_context': sum(p['U_delta_bound_minus_context'] for p in group), 'pair_ids': [p['pair_id'] for p in group]}
        terminal_group = [p for p in pairs if p['terminal_truncation_position'] == position]
        summary['terminal_paired_decomposition'][position] = {'pairs': len(terminal_group),
            'U_delta_sum_bound_minus_context': sum(p['U_delta_bound_minus_context'] for p in terminal_group),
            'pair_ids': [p['pair_id'] for p in terminal_group]}
    after = input_inventory()
    write_json('inputs-sha256-after.json', after)
    changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
    summary['input_files_hashed'] = len(before)
    summary['input_files_changed'] = changed
    write_json('integrity.json', {'before_after_match': not changed, 'files': len(before), 'changed': changed,
        'response_and_event_audit_issues': issues, 'script_sha256': digest(OUT / 'analysis.py'),
        'tests_sha256': digest(OUT / 'test_analysis.py'), 'protocol_sha256': protocol_hash})
    write_json('summary.json', summary)
    if changed or issues:
        raise RuntimeError(f'Audit integrity exceptions: {len(changed)} changed inputs; {len(issues)} evidence issues')
    print(json.dumps({k: summary[k] for k in ('B_planned_arms', 'provider_attempts', 'raw_responses', 'response_classes', 'arm_diagnostic_terminals', 'policy', 'input_files_hashed', 'input_files_changed')}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
