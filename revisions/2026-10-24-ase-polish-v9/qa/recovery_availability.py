"""Read-only reconstruction of reuse availability in all 32 archived G pairs.

No model calls and no imports from the admission implementation. Checks the
saved state and visible input, not the logged legal_paths_at_rejection label.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

BASE = Path(__file__).resolve().parent.parent


def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository-root', type=Path, default=BASE.parent.parent)
    p.add_argument('--output', type=Path, default=BASE / 'tables' / 'availability')
    args = p.parse_args()
    data = json.loads((BASE / 'scripts/figures/figure-data.json').read_text(encoding='utf-8-sig'))
    rows, sources, members = [], [], []
    for archive in sorted({p['source_archive'] for p in data['g_pairs']}):
        path = args.repository_root / archive
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        assert sha == next(s['sha256'] for s in data['sources'] if s['path'] == archive)
        sources.append({'path': archive, 'sha256': sha})
        with zipfile.ZipFile(path) as z:
            for pair in [p for p in data['g_pairs'] if p['source_archive'] == archive]:
                member = pair['archive_members']['bound']['events']
                parent = PurePosixPath(member).parent

                def read(name, expected=None):
                    raw = z.read(name)
                    sha = hashlib.sha256(raw).hexdigest()
                    if expected:
                        assert sha == expected, name
                    members.append({'archive': archive, 'member': name, 'sha256': sha})
                    return json.loads(raw.decode('utf-8-sig'))

                raw = z.read(member)
                members.append({'archive': archive, 'member': member, 'sha256': hashlib.sha256(raw).hexdigest()})
                events = [json.loads(x) for x in raw.decode('utf-8-sig').splitlines() if x.strip()]
                f = next(e for e in events if e['event_id'] == pair['bound_episode']['feedback_event_id'])
                assert f['payload']['delivered']
                def ref(key):
                    r = f['payload'][key]
                    return read(str(parent / r['relative_path']), r['sha256'])
                state, visible = ref('rejection_state_ref'), ref('agent_input_message_ref')
                grants = [x['result'] for x in visible if x.get('tool_name') == 'request_authorization' and x.get('result', {}).get('status') == 'ok']
                g_visible = grants[-1]
                g = state['grants'][g_visible['authorization_id']]
                c = state['candidates'][g['reviewed_candidate_id']]
                k, case = c['context'], state['case']
                evidence = state['evidence'][k['evidence_file_id']]
                checks = {
                    'active_unconsumed_grant': g['status'] == 'active',
                    'reviewer_active': state['reviewer_active'],
                    'candidate_digest': c['certificate_id'] == digest({a: b for a, b in c.items() if a != 'certificate_id'}),
                    'context_digest': c['context_hash'] == digest(k),
                    'reviewed_candidate_preserved': c == g['reviewed_candidate'],
                    'fresh_predecessor': k['expected_fact_version'] == state['head']['version'],
                    'evidence_bytes': hashlib.sha256(evidence['bytes'].encode()).hexdigest() == k['evidence_hash'],
                    'evidence_locator': evidence['locator'] == k['evidence_locator'],
                    'source_supported': k['proposal_value_payload'] == canonical(case['source_proposal_value']),
                    'retained_metadata': all(k.get(a) == b for a, b in case['retained_metadata'].items()),
                    'target_matches': k['target_record_id'] == g['record_id'] == case['record_id'] and k['field_key'] == g['field_key'] == case['field_key'],
                    'review_context_matches': k == g['context'],
                    'visible_grant_and_candidate': g_visible['reviewed_candidate'] == c and g_visible['authorized_value'] == g['authorized_value'],
                }
                assert all(checks.values()), (pair['id'], checks)
                rejection = next(e for e in events if e['event_id'] == f['payload']['decision_event_id'])
                assert rejection['payload']['reason_code'] == 'INSTANCE_MISMATCH'
                before_ref = rejection['payload']['pre_state_ref']
                before = read(str(parent / before_ref['relative_path']), before_ref['sha256'])
                assert before['head'] == state['head'] and before['transitions'] == state['transitions']
                calls = [e for e in events if e['event_type'] == 'tool_call' and e['origin'] == 'agent' and e['sequence'] > f['sequence']]
                results = {e['payload']['tool_call_id']: e for e in events if e['event_type'] == 'tool_result'}
                first = calls[0]['payload']
                route = 'reuse-reviewed' if first['tool_name'] == 'commit' else 'reauthorization'
                assert route == pair['recovery_path']
                recovery = calls[:1 if route == 'reuse-reviewed' else 2]
                assert [e['payload']['tool_name'] for e in recovery] == (['commit'] if route == 'reuse-reviewed' else ['request_authorization', 'commit'])
                last = recovery[-1]['payload']
                result = results[last['tool_call_id']]['payload']
                assert result['result']['status'] == 'ok'
                snapshots = []
                for key in ('state_before_ref', 'state_after_ref'):
                    r = result[key]
                    snapshots.append(read(str(parent / r['relative_path']), r['sha256']))
                assert len(snapshots[1]['transitions']) == len(snapshots[0]['transitions']) + 1
                if route == 'reuse-reviewed':
                    assert last['arguments']['candidate_id'] == c['candidate_id']
                    assert last['arguments']['authorization_id'] == g['authorization_id']
                rows.append({'id': pair['id'], 'case_id': pair['case_id'], 'cohort': pair['cohort'],
                    'route': route, 'reuse_available_and_visible': True, 'availability_checks': len(checks),
                    'new_authorization_requests': int(route == 'reauthorization'),
                    'calls_to_first_durable_commit': len(recovery), 'feedback_event': f['event_id']})
    assert len(rows) == 32 and len({r['case_id'] for r in rows}) == 16
    matches = []
    for task in sorted({r['case_id'] for r in rows}):
        a = next(r for r in rows if r['case_id'] == task and r['cohort'] != 'original_B')
        b = next(r for r in rows if r['case_id'] == task and r['cohort'] == 'original_B')
        matches.append({'case_id': task, 'A_cohort': a['cohort'], 'A_route': a['route'], 'B_route': b['route']})
    args.output.mkdir(parents=True, exist_ok=True)
    for name, records in [('episodes.csv', rows), ('matched-tasks.csv', matches)]:
        with (args.output / name).open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0]))
            writer.writeheader(); writer.writerows(records)
    summary = {'scope': 'Post-hoc archival reconstruction, no new trajectories or counterfactual executions.',
        'episodes': len(rows), 'all_reuse_available_and_visible': all(r['reuse_available_and_visible'] for r in rows),
        'cohorts': {c: dict(Counter(r['route'] for r in rows if r['cohort'] == c)) for c in sorted({r['cohort'] for r in rows})},
        'matched_tasks': matches, 'sources': sources, 'members': members,
        'limits': 'Availability is established at saved rejection time under the reduced host assumptions; it does not assert optimality, human cost, or unchanged state during a production delay.'}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('sources','members','matched_tasks')}))


if __name__ == '__main__':
    main()
