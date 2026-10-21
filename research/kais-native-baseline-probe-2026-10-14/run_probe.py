"""Offline descriptive probe. Executes unchanged CK and Host; never calls a model."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
import runpy
import sys
import traceback
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CK_SOURCE = ROOT / 'reviews/kais-execution-plan-2026-10-14/baseline-audit/sources/ck-bounded-model.txt'
HOST_SOURCE = ROOT / 'research/agent-policy-phase2-formal-2026-10-07/src/phase2/kernel.py'
MODES = ('Accept', 'Correction')
CONDITIONS = ('normal', 'new_instance', 'evidence_changed', 'predecessor_changed')


def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(mode, condition):
    return {
        'task_instance_id': f'PROBE-{mode}-{condition}', 'scenario': 'E',
        'record_id': 'OFFLINE-CONSTRUCTED-1', 'field_key': 'quantity',
        'domain': 'purchase_quantity',
        'baseline_values': {'quantity': 7, 'reference_note': 'constructed note',
                            'business_context': 'constructed procurement'},
        'baseline_sources': {'quantity': 'fixture:quantity', 'reference_note': 'fixture:note',
                             'business_context': 'fixture:context'},
        'source_proposal_value': 20, 'host_authorized_value': 20 if mode == 'Accept' else 21,
        'evidence_snapshots': {
            'E1': {'bytes': 'Constructed source: quantity 20; revision 1.', 'locator': 'row/quantity/revision-1'},
            'E2': {'bytes': 'Constructed source: quantity 20; revision 2.', 'locator': 'row/quantity/revision-2'},
        },
    }


def host_run(Host, mode, condition, policy, *, reauthorize_instance=False, wrong_value=False, capture=None):
    host = Host(fixture(mode, condition), policy)
    trace = []
    if capture is not None:
        capture['trace'] = trace
        capture['final_state'] = host.state  # Retain partial state if a later call raises.

    def call(tool, args):
        result = host.call(tool, args)
        trace.append({'tool': tool, 'args': copy.deepcopy(args), 'result': copy.deepcopy(result)})
        return result

    def prepare():
        state = call('get_state', {'record_id': host.case['record_id']})
        candidate = call('propose', {
            'record_id': host.case['record_id'], 'field_key': 'quantity', 'proposal_value': 20,
            'evidence_ref': state['evidence_ref'], 'parent_certificate_id': state['root_certificate_id'],
        })
        return candidate

    def commit_args(candidate, grant, key):
        return {'candidate_id': candidate['candidate_id'], 'authorization_id': grant['authorization_id'],
                'committed_value': grant['authorized_value'], 'idempotency_key': key}

    def attempt(args):
        before = copy.deepcopy(host.state['head'])
        count_before = len(host.state['transitions'])
        c = host.state['candidates'][args['candidate_id']]
        g = host.state['grants'][args['authorization_id']]
        facts = {
            'original_proposal_value': host.case['source_proposal_value'],
            'authorized_value': g['authorized_value'], 'attempted_value': args['committed_value'],
            'reviewed_candidate_id': g['reviewed_candidate_id'], 'attempted_candidate_id': c['candidate_id'],
            'same_reviewed_instance': g['reviewed_candidate_id'] == c['candidate_id'],
            'same_context': c['context'] == g['context'],
            'evidence_current': c['context']['evidence_file_id'] == host.state['current_evidence_ref'],
            'predecessor_current': c['context']['expected_fact_version'] == before['version'],
        }
        result = call('commit', args)
        after = copy.deepcopy(host.state['head'])
        facts.update({
            'new_transition_count': len(host.state['transitions']) - count_before,
            'state_changed': before != after,
            'final_value': after['values']['quantity'],
            'final_matches_authorized': after['values']['quantity'] == g['authorized_value'],
            'unchanged_values_preserved': all(after['values'][k] == v for k, v in before['values'].items() if k != 'quantity'),
            'unchanged_sources_preserved': all(after['sources'][k] == v for k, v in before['sources'].items() if k != 'quantity'),
            'head_before': before['version'], 'head_after': after['version'],
        })
        return {'response': result.get('error_code', result['status']),
                'accepted_response': result['status'] == 'ok', 'facts': facts}

    c1 = prepare()
    grant = call('request_authorization', {'candidate_id': c1['candidate_id']})
    candidate = c1
    if condition == 'new_instance':
        candidate = prepare()
    elif condition == 'evidence_changed':
        host.publish_evidence()
        trace.append({'trusted_environment_event': 'publish_E2', 'evidence': copy.deepcopy(host.state['evidence'])})
    elif condition == 'predecessor_changed':
        host.advance('constructed note; independent head advance')
        trace.append({'trusted_environment_event': 'advance', 'head': copy.deepcopy(host.state['head'])})

    args = commit_args(candidate, grant, 'initial')
    if wrong_value:
        args['committed_value'] = host.case['source_proposal_value']
    initial = attempt(args)
    replay = attempt(args)
    recovery = None
    if not initial['accepted_response'] and not wrong_value:
        if condition == 'new_instance' and not reauthorize_instance:
            candidate = c1
        else:
            if condition != 'new_instance':
                candidate = prepare()
            grant = call('request_authorization', {'candidate_id': candidate['candidate_id']})
        recovery = attempt(commit_args(candidate, grant, 'recovery'))
    return {'initial': initial, 'replay': replay, 'recovery': recovery,
            'trace': trace, 'final_state': copy.deepcopy(host.state)}


def ck_projection(state):
    return {k: getattr(state, k) for k in (
        'head', 'state_root', 'authority_version', 'effects', 'quarantine', 'branch_exists',
        'epoch', 'dir_seq', 'writer', 'lifecycle', 'restorable_root', 'protected_root')}


def ck_prepare(ck, state, mode, evidence='E1', pid=0, eid=0, ops=None):
    # Opaque digest records adapter context; CK does not interpret correction values.
    operation = ops if ops is not None else (1 if mode == 'Accept' else 2)
    description = {'pid': pid, 'head': state.head, 'evidence': evidence, 'mode': mode,
                   'proposal_value': 20, 'authorized_value': 20 if mode == 'Accept' else 21,
                   'ops_token': operation, 'eid': eid}
    core = int(hashlib.sha256(canonical(description).encode()).hexdigest(), 16)
    request = ck['Request'](pid, core, core + 1, state.head, state.epoch, state.writer,
        ops_token=operation, candidate_root=ck['transition_root'](state.state_root, operation),
        manifest_eids=(eid,), operation_eids=(eid,))
    return request


def ck_attempt(ck, state, request):
    before = ck_projection(state)
    result = ck['submit'](state, request)
    after = ck_projection(result.state)
    outcome = ck['outcome_for'](result.state, request.pid)
    metrics = {'response': result.response, 'accepted_response': result.response == 'Commit',
        'facts': {'state_changed': before != after, 'head_before': state.head, 'head_after': result.state.head,
                  'new_effect_count': len(result.state.effects) - len(state.effects),
                  'predecessor_current': request.expected_head == state.head,
                  'supplied_initial_freshness': request.commit_bound_valid,
                  'supplied_final_freshness': request.final_bound_valid,
                  'native_stage': outcome.act_check if outcome else None,
                  'same_reviewed_instance': None, 'original_proposal_value': None,
                  'authorized_value': None, 'final_value': None,
                  'unchanged_values_preserved': None, 'unchanged_sources_preserved': None}}
    trace = {'request': request._asdict(), 'state_before': asdict(state),
             'response': result.response, 'state_after': asdict(result.state)}
    return result.state, metrics, trace


def ck_run(ck, mode, condition, capture=None):
    state = ck['State']()
    prepared = ck_prepare(ck, state, mode)
    trace = [{'adapter_preparation': prepared._asdict(), 'bound_evidence': 'E1'}]
    if capture is not None:
        capture.update(trace=trace, final_state=asdict(state))
    current_evidence = 'E1'
    if condition == 'predecessor_changed':
        external = ck_prepare(ck, state, 'Accept', pid=2, eid=1, ops=1)
        state, metric, event = ck_attempt(ck, state, external)
        if capture is not None:
            capture['final_state'] = asdict(state)
        if not metric['accepted_response']:
            raise RuntimeError('Independent CK head advance was not accepted')
        trace.append({'trusted_environment_event': 'independent_commit', **event})
    elif condition == 'evidence_changed':
        current_evidence = 'E2'
    validity = current_evidence == 'E1'
    # Environmental revalidation of an unchanged prepared package, not a new attempt.
    request = prepared._replace(commit_bound_valid=validity, final_bound_valid=validity)
    trace.append({'adapter_revalidation': {'bound_evidence': 'E1', 'current_evidence': current_evidence,
                                          'predicate': validity}})
    state, initial, event = ck_attempt(ck, state, request)
    trace.append(event)
    if capture is not None:
        capture.update(initial=initial, final_state=asdict(state))
    state, replay, event = ck_attempt(ck, state, request)
    trace.append(event)
    if capture is not None:
        capture.update(replay=replay, final_state=asdict(state))
    recovery = None
    if not initial['accepted_response']:
        # New pid, new digest, current predecessor/evidence, original unconsumed effect.
        fresh = ck_prepare(ck, state, mode, evidence=current_evidence, pid=1, eid=0)
        state, recovery, event = ck_attempt(ck, state, fresh)
        trace.append(event)
        if capture is not None:
            capture.update(recovery=recovery, final_state=asdict(state))
    return {'initial': initial, 'replay': replay, 'recovery': recovery,
            'trace': trace, 'final_state': asdict(state)}


def native_controls(ck, records):
    base = ck['State']()
    request = ck_prepare(ck, base, 'Correction')
    definitions = [
        ('candidate_root_mismatch', base, request._replace(candidate_root=(request.candidate_root + 1) % 29), 'RejectCandidateBinding'),
        ('final_freshness', base, request._replace(final_bound_valid=False), 'RejectExpiredAtActivation'),
        ('invalid_successor', base, request._replace(successor_well_formed=False), 'RejectInvalidSuccessor'),
        ('self_authorization', base, request._replace(authority_required=1, authority_effect=1), 'RejectUnauthorized'),
    ]
    accepted = ck['submit'](base, request)
    if accepted.response != 'Commit':
        raise RuntimeError('Native control setup commit failed')
    current = accepted.state
    definitions.extend([
        ('reused_pid_core', current, request._replace(core_digest=request.core_digest + 1), 'IdReuseConflict'),
        ('reused_pid_attempt', current, request._replace(attempt_digest=request.attempt_digest + 1), 'AttemptVariantConflict'),
        ('duplicate_effect', current, ck_prepare(ck, current, 'Correction', pid=1, eid=0), 'RejectDuplicateEffect'),
    ])
    for label, state, query, expected in definitions:
        record = {'control': label, 'method': 'CK_native_model', 'expected_response': expected,
                  'trace': {'request': query._asdict(), 'state_before': asdict(state)}}
        records.append(record)
        _, metrics, trace = ck_attempt(ck, state, query)
        record.update(observed=metrics, trace=trace)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=HERE / 'results.json')
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit('Output already exists; choose a new --out path to preserve it.')
    if not __debug__:
        raise SystemExit('Do not use python -O: native assertions must remain enabled.')
    freeze = json.loads((HERE / 'freeze.json').read_text(encoding='utf-8'))
    for item in freeze['inputs']:
        if sha(ROOT / item['path']) != item['sha256']:
            raise SystemExit(f'Frozen input changed: {item["path"]}')
    spec = importlib.util.spec_from_file_location('original_probe_host', HOST_SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    ck = runpy.run_path(str(CK_SOURCE), run_name='ck_probe_original')
    rows, controls, errors, checks = [], [], [], []

    def check(label, value):
        checks.append({'check': label, 'pass': bool(value)})

    for mode in MODES:
        for condition in CONDITIONS:
            for method in ('context', 'bound', 'CK_native_model'):
                row = {'mode': mode, 'condition': condition, 'method': method}
                try:
                    if method == 'CK_native_model' and condition == 'new_instance':
                        row.update(status='not_representable', reason='No distinct reviewed/executed candidate identity in native abstraction')
                    else:
                        data = ck_run(ck, mode, condition, capture=row) if method == 'CK_native_model' else host_run(module.Host, mode, condition, method, capture=row)
                        row.update(status='executed', **data)
                        first, replay, recovery = (row[k] for k in ('initial', 'replay', 'recovery'))
                        prefix = f'{mode}/{condition}/{method}'
                        expected = condition == 'normal' or (condition == 'new_instance' and method == 'context')
                        check(prefix + ':admission', first['accepted_response'] == expected)
                        reasons = ({'normal': 'Commit', 'evidence_changed': 'RejectExpiredAtActivation',
                                    'predecessor_changed': 'RejectStaleHead'} if method == 'CK_native_model' else
                                   {'normal': 'ok', 'new_instance': 'ok' if method == 'context' else 'INSTANCE_MISMATCH',
                                    'evidence_changed': 'EVIDENCE_SUPERSEDED', 'predecessor_changed': 'STALE_VERSION'})
                        check(prefix + ':intended_single_fault', first['response'] == reasons[condition])
                        check(prefix + ':replay', first['response'] == replay['response'] and not replay['facts']['state_changed'])
                        if not first['accepted_response']:
                            check(prefix + ':rejection_preserves_authoritative_state', not first['facts']['state_changed'])
                            check(prefix + ':legal_recovery', recovery is not None and recovery['accepted_response'])
                        if method != 'CK_native_model':
                            accepted = first if first['accepted_response'] else recovery
                            facts = accepted['facts']
                            check(prefix + ':committed_value_and_preservation', facts['final_matches_authorized'] and facts['unchanged_values_preserved'] and facts['unchanged_sources_preserved'])
                            check(prefix + ':single_successor', facts['new_transition_count'] == 1 and facts['head_after'] == facts['head_before'] + 1)
                except Exception:
                    row.update(status='error', error=traceback.format_exc())
                    errors.append(row['error'])
                rows.append(row)
    try:
        native_controls(ck, controls)
        for mode in MODES:
            control = {'control': f'new_instance_fresh_authorization_{mode}', 'method': 'bound', 'expected_response': 'ok'}
            controls.append(control)
            result = host_run(module.Host, mode, 'new_instance', 'bound', reauthorize_instance=True, capture=control)
            control.update(observed=result['recovery'])
        for policy in ('context', 'bound'):
            control = {'control': 'correction_original_value', 'method': policy, 'expected_response': 'AUTHORIZED_VALUE_MISMATCH'}
            controls.append(control)
            result = host_run(module.Host, 'Correction', 'normal', policy, wrong_value=True, capture=control)
            control.update(observed=result['initial'])
        for control in controls:
            check(control['method'] + ':' + control['control'], control['observed']['response'] == control['expected_response'])
            if control['expected_response'] != 'ok':
                check(control['method'] + ':' + control['control'] + ':unchanged', not control['observed']['facts']['state_changed'])
    except Exception:
        errors.append(traceback.format_exc())
    check('planned_24_records', len(rows) == 24)
    check('executed_22_records', sum(r['status'] == 'executed' for r in rows) == 22)
    check('two_not_representable', sum(r['status'] == 'not_representable' for r in rows) == 2)
    check('all_11_controls_present', len(controls) == 11)
    semantic = {
        'rows': [{k: v for k, v in r.items() if k not in ('trace', 'final_state')} for r in rows],
        'controls': [{k: v for k, v in c.items() if k not in ('trace', 'final_state')} for c in controls],
        'checks': checks, 'errors': errors,
    }
    output = {'run_utc': datetime.now(timezone.utc).isoformat(),
              'python': platform.python_version(), 'platform': platform.platform(),
              'jsonschema': importlib.metadata.version('jsonschema'), 'freeze_sha256': sha(HERE / 'freeze.json'),
              'scope': 'exploratory_coarse_admission_probe', 'model_calls': 0,
              'full_ck_exploration': False, 'external_runtime_benchmark': False,
              'rows': rows, 'controls': controls, 'checks': checks, 'errors': errors,
              'semantic_sha256': hashlib.sha256(canonical(semantic).encode()).hexdigest(),
              'all_checks_pass': not errors and all(c['pass'] for c in checks)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(args.out), 'rows': len(rows), 'checks': len(checks),
                      'all_checks_pass': output['all_checks_pass'], 'errors': errors}, ensure_ascii=False))
    return 0 if output['all_checks_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
