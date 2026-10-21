"""Post-run raw-artifact verification; does not execute Host or call models."""
import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_run(name):
    run = HERE / 'runs' / name
    counts = dict(records=0, sqlite_snapshots=0, tool_calls=0, withheld_requests=0,
                  hidden_responses=0, public_observations=0, environment_events=0,
                  cached_results_replayed=0, new_commits=0, hidden_history_pairs=0)
    for group in ('main', 'controls'):
        for directory in sorted((run / group).iterdir()):
            if not directory.is_dir():
                continue
            counts['records'] += 1
            states = []
            for snapshot in read(directory / 'snapshots.json'):
                db_path, json_path = (directory / snapshot[k] for k in ('sqlite', 'json'))
                assert sha(db_path) == snapshot['sqlite_sha256'], db_path
                assert sha(json_path) == snapshot['json_sha256'], json_path
                with closing(sqlite3.connect(db_path.as_uri() + '?mode=ro', uri=True)) as db:
                    payloads = db.execute('SELECT payload FROM state').fetchall()
                assert len(payloads) == 1, db_path
                state = json.loads(payloads[0][0])
                assert state == read(json_path), db_path
                states.append(state)
                counts['sqlite_snapshots'] += 1
            public = []
            for call in read(directory / 'private-calls.json'):
                before, after = (states[call[k]] for k in ('before_snapshot', 'after_snapshot'))
                if 'trusted_environment_event' in call:
                    assert call['trusted_environment_event'] == 'reviewer_active'
                    assert after == dict(before, reviewer_active=call['value'])
                    counts['environment_events'] += 1
                    continue
                counts['tool_calls'] += 1
                actual = call['actual_result']
                if not call['delivered']:
                    assert actual is None and after == before
                    counts['withheld_requests'] += 1
                elif call['tool'] == 'commit':
                    args = call['arguments']
                    cached = before['idempotency'].get(args['idempotency_key'])
                    if cached and cached['arguments'] == args:
                        assert actual == cached['result'] and after == before
                        counts['cached_results_replayed'] += 1
                    elif actual['status'] == 'ok':
                        assert len(after['transitions']) == len(before['transitions']) + 1
                        transition = after['transitions'][-1]
                        assert transition['arguments'] == args
                        assert transition['pre'] == before['head'] and transition['post'] == after['head']
                        assert after['receipts'][actual['commit_request_id']] == actual
                        assert after['idempotency'][args['idempotency_key']]['result'] == actual
                        counts['new_commits'] += 1
                    else:
                        assert actual['status'] == 'rejected'
                        assert after['head'] == before['head'] and after['transitions'] == before['transitions']
                elif call['tool'] == 'get_state':
                    assert after == before
                    assert all(actual[k] == after['head'][k] for k in ('version', 'values', 'sources'))
                else:
                    raise AssertionError('Unexpected post-preparation tool: ' + call['tool'])
                if call['response_hidden']:
                    counts['hidden_responses'] += 1
                expected = {'status': 'unknown', 'error_code': 'TRANSPORT_TIMEOUT'} if (
                    call['response_hidden'] or not call['delivered']) else actual
                assert call['visible_result'] == expected
                if call['client_observed']:
                    public.append({'tool': call['tool'], 'arguments': call['arguments'], 'result': expected})
            if group == 'main':
                assert public == read(directory / 'public-transcript.json')
                counts['public_observations'] += len(public)
                report = read(directory / 'client-report.json')
                own = [t for t in states[-1]['transitions'] if t['arguments']['idempotency_key'] == 'primary-request']
                if report['request_outcome'] == 'confirmed':
                    assert len(own) == 1 and own[0]['commit_request_id'] == report['confirmed_request_id']
                if report['request_outcome'] == 'rejected':
                    assert not own
            assert read(directory / 'result.json')['status'] == 'pass'
    for relation in ('accept', 'correction'):
        for policy in ('context', 'bound'):
            a, b = (run / 'main' / f'{relation}--{policy}--hidden_{kind}_commit' for kind in ('primary', 'competing'))
            assert read(a / 'client-journal.json') == read(b / 'client-journal.json')
            assert read(a / 'public-transcript.json') == read(b / 'public-transcript.json')
            finals = [read(p / read(p / 'snapshots.json')[-1]['json']) for p in (a, b)]
            assert finals[0]['head'] == finals[1]['head']
            assert finals[0]['transitions'][0]['arguments']['idempotency_key'] == 'primary-request'
            assert finals[1]['transitions'][0]['arguments']['idempotency_key'] == 'competing-request'
            counts['hidden_history_pairs'] += 1
    assert counts['records'] == 32
    return counts


if __name__ == '__main__':
    frozen = read(HERE / 'freeze.json')
    for item in frozen['inputs']:
        assert sha(HERE / item['path']) == item['sha256'], item['path']
    inputs = read(HERE / 'inputs.json')
    for item in inputs['files']:
        assert sha(REPO / item['original']) == sha(HERE / item['copy']) == item['sha256']
    for item in inputs['protected_prior_inputs']:
        assert sha(REPO / item['path']) == item['sha256'], item['path']
    runs = {name: audit_run(name) for name in ('initial', 'rebuild')}
    paths = [HERE / 'runs' / name / 'normalized_summary.json' for name in runs]
    assert read(paths[0]) == read(paths[1])
    result = {'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'result': 'PASS',
              'verifier_sha256': sha(Path(__file__)), 'frozen_inputs_unchanged': len(frozen['inputs']),
              'vendor_files_match_originals': len(inputs['files']),
              'protected_prior_inputs_unchanged': len(inputs['protected_prior_inputs']),
              'normalized_summaries_equal': True, 'normalized_summary_sha256': sha(paths[0]),
              'raw_audit': runs, 'scope': 'Same machine, separate output directories; post-run verifier; no API or Host calls.'}
    output = HERE / 'verification.json'
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))
