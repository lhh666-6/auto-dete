"""Offline sufficiency probe of the unchanged paper Host; no model/API calls."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import sys
import traceback
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
CASES = ('before_delivery', 'after_durable_commit', 'competing_key_same_value',
         'committed_then_reviewer_disabled', 'hidden_primary_commit', 'hidden_competing_commit')
HIDDEN = ('hidden_primary_commit', 'hidden_competing_commit')
TIMEOUT = {'status': 'unknown', 'error_code': 'TRANSPORT_TIMEOUT'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def local(path):
    resolved = (HERE / path).resolve()
    if not resolved.is_relative_to(HERE):
        raise ValueError('Path must stay within experiment directory')
    return resolved


def load_host():
    path = HERE / 'vendor/original-host/src/phase2/kernel.py'
    spec = importlib.util.spec_from_file_location('unchanged_uncertainty_host', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Host


def prepare(Host, relation, policy):
    case = {'task_instance_id': 'UNCERTAINTY-' + relation, 'scenario': 'L',
            'record_id': 'local-record', 'field_key': 'quantity', 'domain': 'purchase_quantity',
            'baseline_values': {'quantity': 7, 'reference_note': 'retain-original-note'},
            'source_proposal_value': 20, 'host_authorized_value': 20 if relation == 'Accept' else 21}
    host = Host(case, policy)
    prefix = []

    def call(tool, args):
        result = host.call(tool, args)
        prefix.append({'tool': tool, 'arguments': copy.deepcopy(args), 'result': copy.deepcopy(result)})
        if result['status'] != 'ok':
            raise RuntimeError(f'Preparation failed: {tool}: {result}')
        return result

    state = call('get_state', {'record_id': case['record_id']})
    candidate = call('propose', {'record_id': case['record_id'], 'field_key': 'quantity',
                               'proposal_value': 20, 'evidence_ref': state['evidence_ref'],
                               'parent_certificate_id': state['root_certificate_id']})
    grant = call('request_authorization', {'candidate_id': candidate['candidate_id']})
    journal = {'prefix': prefix, 'record_id': case['record_id'], 'field_key': 'quantity',
               'authorized_value': grant['authorized_value'],
               'request': {'candidate_id': candidate['candidate_id'],
                           'authorization_id': grant['authorization_id'],
                           'committed_value': grant['authorized_value'], 'idempotency_key': 'primary-request'}}
    return copy.deepcopy(host.state), journal


class Trace:
    def __init__(self, Host, state, policy, directory):
        self.Host, self.policy, self.directory = Host, policy, directory
        directory.mkdir(parents=True)
        self.host = Host.from_state(state, policy)
        self.snapshots, self.raw, self.public = [], [], []
        self.checkpoint('prepared')

    def checkpoint(self, label):
        number = len(self.snapshots)
        db = self.directory / 'states' / f'{number:03d}.sqlite'
        db.parent.mkdir(exist_ok=True)
        state = copy.deepcopy(self.host.state)
        self.host.persist(db)
        restored = self.Host.load(db, self.policy)
        if restored.state != state:
            raise RuntimeError('Persist/load changed Host state')
        self.host = restored
        json_path = db.with_suffix('.json')
        write(json_path, state)
        item = {'label': label, 'sqlite': db.relative_to(self.directory).as_posix(),
                'json': json_path.relative_to(self.directory).as_posix(),
                'sqlite_sha256': sha(db), 'json_sha256': sha(json_path)}
        self.snapshots.append(item)
        write(self.directory / 'snapshots.json', self.snapshots)
        return number

    def call(self, tool, args, label, *, delivered=True, hide=False, observe=False):
        before = self.checkpoint(label + '-before')
        actual = self.host.call(tool, copy.deepcopy(args)) if delivered else None
        after = self.checkpoint(label + '-after')
        visible = copy.deepcopy(TIMEOUT if hide or not delivered else actual)
        self.raw.append({'label': label, 'tool': tool, 'arguments': copy.deepcopy(args),
                         'delivered': delivered, 'response_hidden': hide,
                         'actual_result': copy.deepcopy(actual), 'visible_result': visible,
                         'before_snapshot': before, 'after_snapshot': after, 'client_observed': observe})
        write(self.directory / 'private-calls.json', self.raw)
        if observe:
            self.public.append({'tool': tool, 'arguments': copy.deepcopy(args), 'result': visible})
            write(self.directory / 'public-transcript.json', self.public)
        return visible

    def reviewer(self, active):
        before = self.checkpoint('reviewer-event-before')
        self.host.state['reviewer_active'] = active
        after = self.checkpoint('reviewer-event-after')
        self.raw.append({'trusted_environment_event': 'reviewer_active', 'value': active,
                         'before_snapshot': before, 'after_snapshot': after})
        write(self.directory / 'private-calls.json', self.raw)


def recover(journal, call):
    """Only caller evidence and public tools; no scenario or private Host access."""
    result = call('commit', copy.deepcopy(journal['request']))
    current = call('get_state', {'record_id': journal['record_id']})
    if result['status'] == 'ok':
        outcome = 'confirmed'
    elif result['status'] == 'rejected' and result.get('error_code') not in (
            'IDEMPOTENCY_COLLISION', 'INVALID_ARGUMENTS'):
        outcome = 'rejected'
    else:
        outcome = 'unknown'
    return {'request_outcome': outcome,
            'current_goal_present': current['values'][journal['field_key']] == journal['authorized_value']
                if current['status'] == 'ok' else None,
            'observed_current_version': current.get('version'),
            'confirmed_request_id': result.get('commit_request_id') if outcome == 'confirmed' else None,
            'confirmed_historical_version': result.get('version') if outcome == 'confirmed' else None,
            'claimed_original_delivery_timing': 'not_inferred',
            'claimed_competing_request_identity': 'not_inferred'}


def run_case(trace, journal, scenario):
    write(trace.directory / 'client-journal.json', journal)
    # Re-read the durable caller journal; a lost response never supplies a server request ID.
    caller = read(trace.directory / 'client-journal.json')
    own_delivered = scenario in ('after_durable_commit', 'committed_then_reviewer_disabled',
                                'hidden_primary_commit')
    trace.call('commit', caller['request'], 'initial-attempt', delivered=own_delivered, hide=True, observe=True)
    if scenario in ('competing_key_same_value', 'hidden_competing_commit'):
        other = dict(caller['request'], idempotency_key='competing-request')
        response = trace.call('commit', other, 'competing-request', observe=False)
        if response['status'] != 'ok':
            raise RuntimeError('Competing request setup failed')
    if scenario == 'committed_then_reviewer_disabled':
        trace.reviewer(False)
    before = copy.deepcopy(trace.host.state)

    def public_call(tool, args):
        return trace.call(tool, args, 'recovery-' + tool,
                          delivered=not (scenario in HIDDEN and tool == 'commit'), observe=True)

    report = recover(caller, public_call)
    after = trace.host.state
    primary = caller['request']['idempotency_key']
    own_before = sum(t['arguments']['idempotency_key'] == primary for t in before['transitions'])
    own_after = sum(t['arguments']['idempotency_key'] == primary for t in after['transitions'])
    added = len(after['transitions']) - len(before['transitions'])
    expected = 'unknown' if scenario in HIDDEN else 'rejected' if scenario == 'competing_key_same_value' else 'confirmed'
    checks = {'report_matches_available_evidence': report['request_outcome'] == expected,
              'goal_presence_reported_separately': report['current_goal_present'] is True,
              'one_total_transition': len(after['transitions']) == 1,
              'expected_new_transitions': added == (1 if scenario == 'before_delivery' else 0),
              'no_false_request_attribution': report['request_outcome'] != 'confirmed' or own_after == 1,
              'known_rejection_not_own_commit': report['request_outcome'] != 'rejected' or own_after == 0,
              'reference_value_preserved': after['head']['values']['reference_note'] == 'retain-original-note',
              'reference_source_preserved': after['head']['sources']['reference_note'] == before['baseline']['sources']['reference_note'],
              'original_request_retried_exactly': trace.public[1]['arguments'] == caller['request'],
              'no_extra_authorization': len(after['grants']) == len(before['grants']) == 1,
              'recovery_only_retry_and_state': [x['tool'] for x in trace.public[1:]] == ['commit', 'get_state']}
    truth = {'primary_committed_before_recovery': own_before == 1,
             'primary_committed_after_recovery': own_after == 1,
             'total_transitions_before': len(before['transitions']), 'total_transitions_after': len(after['transitions']),
             'recovery_new_transitions': added, 'reviewer_active_after': after['reviewer_active']}
    write(trace.directory / 'private-truth.json', truth)
    write(trace.directory / 'client-report.json', report)
    return {'scenario': scenario, 'status': 'pass' if all(checks.values()) else 'fail',
            'checks': checks, 'report': report, 'truth': truth,
            'public_response_codes': [x['result'].get('error_code', x['result']['status']) for x in trace.public],
            'public_tool_sequence': [x['tool'] for x in trace.public]}


def run_control(trace, journal, kind):
    write(trace.directory / 'client-journal.json', journal)
    request = journal['request']
    if kind == 'changed_payload_collision':
        first = trace.call('commit', request, 'first')
        changed = dict(request, committed_value=request['committed_value'] + 100)
        collision = trace.call('commit', changed, 'changed-payload')
        replay = trace.call('commit', request, 'original-replay')
        checks = {'initial_commit_ok': first['status'] == 'ok',
                  'collision_detected': collision.get('error_code') == 'IDEMPOTENCY_COLLISION',
                  'original_result_retained': replay == first,
                  'one_transition_only': len(trace.host.state['transitions']) == 1}
        responses = [first, collision, replay]
    else:
        trace.reviewer(False)
        first = trace.call('commit', request, 'initial-rejection')
        trace.reviewer(True)
        replay = trace.call('commit', request, 'historical-rejection-replay')
        transitions_before_fresh = len(trace.host.state['transitions'])
        fresh = trace.call('commit', dict(request, idempotency_key='fresh-after-change'), 'fresh-request')
        checks = {'initial_reviewer_rejection': first.get('error_code') == 'REVIEWER_INVALID',
                  'cached_rejection_unchanged': replay == first,
                  'rejected_requests_do_not_mutate': transitions_before_fresh == 0,
                  'fresh_legal_request_succeeds': fresh['status'] == 'ok',
                  'one_transition_only': len(trace.host.state['transitions']) == 1}
        responses = [first, replay, fresh]
    return {'control': kind, 'status': 'pass' if all(checks.values()) else 'fail', 'checks': checks,
            'response_codes': [r.get('error_code', r['status']) for r in responses],
            'total_transitions': len(trace.host.state['transitions'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--out-dir', required=True)
    parser.add_argument('--freeze', default='freeze.json')
    args = parser.parse_args()
    if not args.run:
        parser.error('Specify --run after locking the protocol')
    freeze = read(local(args.freeze))
    required = {'run_probe.py', 'PROTOCOL.md', 'inputs.json',
                'vendor/original-host/src/phase2/kernel.py',
                'vendor/original-host/frozen-design/protocol-manifest.json',
                'vendor/original-host/frozen-design/tool-definitions.json'}
    if not freeze.get('locked_at_utc') or not required.issubset({f['path'] for f in freeze['inputs']}):
        raise ValueError('Incomplete protocol lock')
    for item in freeze['inputs']:
        if sha(local(item['path'])) != item['sha256']:
            raise ValueError('Changed locked input: ' + item['path'])
    environment = read(HERE / 'inputs.json')
    if f'{sys.version_info.major}.{sys.version_info.minor}' != environment['python_version']:
        raise ValueError('Python major/minor differs from locked environment')
    if importlib.metadata.version('jsonschema') != environment['jsonschema']:
        raise ValueError('jsonschema version differs from locked environment')
    output = local(args.out_dir)
    if not output.is_relative_to(HERE / 'runs') or output == HERE / 'runs' or output.exists():
        raise ValueError('Use a new directory strictly under runs/')
    output.mkdir(parents=True)
    write(output / 'frozen-inputs.json', freeze)
    write(output / 'environment.json', {'started_at_utc': datetime.now(timezone.utc).isoformat(),
          'python': sys.version, 'jsonschema': importlib.metadata.version('jsonschema'),
          'model_calls': 0, 'unchanged_paper_host': True, 'agent_behavior_measured': False})
    Host = load_host()
    rows, controls, pair_checks = [], [], []
    for relation in ('Accept', 'Correction'):
        for policy in ('context', 'bound'):
            state, journal = prepare(Host, relation, policy)
            for group, kind in [('main', k) for k in CASES] + [('controls', k) for k in
                                ('changed_payload_collision', 'cached_rejection_after_change')]:
                identifier = f'{relation.lower()}--{policy}--{kind}'
                directory = output / group / identifier
                try:
                    trace = Trace(Host, state, policy, directory)
                    result = run_case(trace, journal, kind) if group == 'main' else run_control(trace, journal, kind)
                except Exception as exc:
                    directory.mkdir(parents=True, exist_ok=True)
                    (directory / 'error.txt').write_text(traceback.format_exc(), encoding='utf-8')
                    result = {'scenario' if group == 'main' else 'control': kind,
                              'status': 'error', 'checks': {}, 'exception': repr(exc)}
                result.update(relation=relation, policy=policy,
                              record_directory=directory.relative_to(output).as_posix())
                write(directory / 'result.json', result)
                (rows if group == 'main' else controls).append(result)
                write(output / 'results.json', {'main': rows, 'controls': controls})
                print(identifier + ': ' + result['status'], flush=True)
            paths = [output / 'main' / f'{relation.lower()}--{policy}--{k}' for k in HIDDEN]
            try:
                same_journal = read(paths[0] / 'client-journal.json') == read(paths[1] / 'client-journal.json')
                same_observation = read(paths[0] / 'public-transcript.json') == read(paths[1] / 'public-transcript.json')
                truths = [read(q / 'private-truth.json') for q in paths]
                different_ownership = truths[0]['primary_committed_after_recovery'] and not truths[1]['primary_committed_after_recovery']
                reports = [read(q / 'client-report.json') for q in paths]
                both_unknown = all(r['request_outcome'] == 'unknown' for r in reports)
                checks = {'same_complete_journal': same_journal, 'same_complete_public_transcript': same_observation,
                          'different_private_request_ownership': different_ownership, 'both_preserve_unknown': both_unknown}
                pair_checks.append({'relation': relation, 'policy': policy, 'checks': checks,
                                    'status': 'pass' if all(checks.values()) else 'fail'})
            except Exception as exc:
                pair_checks.append({'relation': relation, 'policy': policy, 'status': 'error', 'checks': {}, 'exception': repr(exc)})
    normalized = {'main': [{k: v for k, v in r.items() if k != 'record_directory'} for r in rows],
                  'controls': [{k: v for k, v in r.items() if k != 'record_directory'} for r in controls],
                  'observation_pairs': pair_checks}
    write(output / 'normalized_summary.json', normalized)
    all_records = rows + controls + pair_checks
    summary = {'completed_at_utc': datetime.now(timezone.utc).isoformat(), 'main_records': len(rows),
               'control_records': len(controls), 'indistinguishable_history_pairs': len(pair_checks),
               'statuses': {s: sum(r['status'] == s for r in all_records) for s in ('pass', 'fail', 'error')},
               'main_outcomes': {s: sum(r.get('report', {}).get('request_outcome') == s for r in rows)
                                 for s in ('confirmed', 'rejected', 'unknown')},
               'checks_evaluated': sum(len(r['checks']) for r in all_records),
               'checks_passed': sum(sum(r['checks'].values()) for r in all_records),
               'model_calls': 0, 'agent_behavior_measured': False}
    write(output / 'run_summary.json', summary)
    print(json.dumps(summary, indent=2))
    return 0 if not summary['statuses']['fail'] and not summary['statuses']['error'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
