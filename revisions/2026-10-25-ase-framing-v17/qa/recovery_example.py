"""Verify and document the two archived examples in OR1 S12.6; no model calls."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath

BASE = Path(__file__).resolve().parent.parent

EXAMPLES = [
    {
        'id': 'FORMAL-G-002-B',
        'route': 'reuse-reviewed',
        'selection': 'Illustration of reuse followed by confirmation; not a representative latency estimate.',
        'calls': [('commit', ('candidate_id', 'authorization_id')),
                  ('get_receipt', ('commit_request_id',))],
        'expected_context_calls': 0,
    },
    {
        'id': 'FORMAL-G-006-A',
        'route': 'reauthorization',
        'selection': 'Illustration of fresh authorization for the submitted candidate; not a representative '
                     'latency estimate.',
        'calls': [('request_authorization', ('candidate_id',)),
                  ('commit', ('candidate_id', 'authorization_id')),
                  ('get_receipt', ('commit_request_id',)),
                  ('get_state', ())],
        'expected_context_calls': 2,
    },
]


def load_events(raw):
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def verify(data, repository_root, spec):
    pair = next(p for p in data['g_pairs'] if p['id'] == spec['id'])
    assert pair['recovery_path'] == spec['route'], (pair['id'], pair['recovery_path'])
    archive = repository_root / pair['source_archive']
    archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
    assert archive_hash == next(s['sha256'] for s in data['sources'] if s['path'] == pair['source_archive'])
    member = pair['archive_members']['bound']['events']
    parent = PurePosixPath(member).parent
    members, checks = [], {}

    with zipfile.ZipFile(archive) as z:
        def read(name):
            raw = z.read(name)
            members.append({'member': name, 'sha256': hashlib.sha256(raw).hexdigest()})
            return raw.decode('utf-8-sig')

        events = load_events(read(member))
        by_seq = {e['sequence']: e for e in events}

        # 1. the delivered rejection is an identity-only mismatch that writes nothing
        rejection = by_seq[6]['payload']
        assert rejection['reason_code'] == 'INSTANCE_MISMATCH'
        assert rejection['candidate_id'] == 'c2' and rejection['reviewed_candidate_id'] == 'c1'
        assert rejection['same_context'] and rejection['same_value'] and rejection['state_unchanged']
        assert rejection['transition_ref'] is None and rejection['decision'] == 'rejected'

        # 2. the saved input that starts the continuation already holds candidate, grant and value
        feedback = by_seq[10]['payload']
        assert feedback['delivered']
        input_ref = feedback['agent_input_message_ref']
        saved = json.loads(read(str(parent / input_ref['relative_path'])))
        propose = next(x['result'] for x in saved if x.get('tool_name') == 'propose')
        grant = next(x['result'] for x in saved if x.get('tool_name') == 'request_authorization')
        assert propose['candidate_id'] == 'c1'
        assert grant['authorization_id'] == 'a1' and grant['authorization_status'] == 'active'
        assert grant['reviewed_candidate']['candidate_id'] == 'c1'
        assert grant['authorized_value'] is not None
        assert grant['reviewed_candidate']['context']['proposal_value_payload'] == \
            propose['context']['proposal_value_payload']
        assert any(x.get('kind') == 'external_executor_notice' and x['candidate']['candidate_id'] == 'c2'
                   for x in saved)

        # 3. the saved rejection state still offers the reviewed candidate and an active grant
        state = json.loads(read(str(parent / feedback['rejection_state_ref']['relative_path'])))
        candidate = state['candidates']['c1']
        assert candidate['context_hash'] == propose['context_hash']
        active = state['grants']['a1']
        assert active['status'] == 'active' and active['reviewed_candidate']['candidate_id'] == 'c1'
        assert active['authorized_value'] == grant['authorized_value']
        assert state['head']['version'] == rejection['observed_head_version'] == 2
        assert state['reviewer_active'] is True and state['current_evidence_ref'] == 'E1'
        assert 'a2' not in state['grants']

        # 4. the continuation takes the documented route, in order, with no failed call in between
        calls = [e for e in events if e['event_type'] == 'tool_call' and e['origin'] == 'agent']
        assert len(calls) == len(spec['calls']), (pair['id'], [c['payload']['tool_name'] for c in calls])
        for call, (name, keys) in zip(calls, spec['calls']):
            payload = call['payload']
            assert payload['tool_name'] == name, (pair['id'], payload['tool_name'], name)
            for key in keys:
                assert payload['arguments'].get(key), (pair['id'], name, key)
        results = [e for e in events if e['event_type'] == 'tool_result' and e['origin'] == 'trusted_host'
                   and e['sequence'] > by_seq[10]['sequence']]
        assert all(r['payload']['error_code'] is None for r in results)

        # 5. the first accepted commit arrives through the documented route
        accepted = [e['payload'] for e in events
                    if e['event_type'] == 'admission_decision' and e['payload']['decision'] == 'accepted']
        assert len(accepted) == 1
        commit = accepted[0]
        commit_index = next(i for i, c in enumerate(calls) if c['payload']['tool_name'] == 'commit')
        commit_call = calls[commit_index]
        assert commit['candidate_id'] == commit_call['payload']['arguments']['candidate_id']
        assert commit['authorization_id'] == commit_call['payload']['arguments']['authorization_id']
        assert commit['committed_value_payload'] == str(commit_call['payload']['arguments']['committed_value'])
        assert commit['transition_ref'] is not None
        committed = [e for e in events if e['event_type'] == 'transition_persisted']
        assert len(committed) == 1

        if spec['route'] == 'reauthorization':
            issued = [e['payload'] for e in events if e['event_type'] == 'authorization_issued']
            assert len(issued) == 1 and issued[0]['authorization_id'] == 'a2'
            assert issued[0]['reviewed_candidate_id'] == 'c2'
            assert issued[0]['authorized_value_payload'] == str(active['authorized_value'])
            superseded = [e['payload'] for e in events if e['event_type'] == 'authorization_superseded']
            assert superseded == [{'authorization_ids': ['a1'], 'new_authorization_id': 'a2'}]
            checks.update({'reuse_route_available': True, 'fresh_grant_issued': 'a2',
                           'old_grant_superseded': True})
        else:
            assert commit['candidate_id'] == 'c1' and commit['authorization_id'] == 'a1'
            checks.update({'reuse_route_used': True})

        # 6. the paired context arm is the contrast for route cost
        context = load_events(read(pair['archive_members']['context']['events']))
        context_calls = [e for e in context if e['event_type'] == 'tool_call' and e['origin'] == 'agent']
        assert len(context_calls) == spec['expected_context_calls']

        checks.update({
            'saved_grant_available': True,
            'reviewed_candidate_unchanged': True,
            'candidate_grant_value_in_model_input': True,
            'rejection_writes_nothing': True,
            'persistent_recovery_commits': 1,
            'bound_recovery_calls': commit_index + 1,
            'confirmation_calls': len(calls) - (commit_index + 1),
            'context_agent_calls': len(context_calls),
        })

    return {
        'pair_id': pair['id'], 'cohort': pair['cohort'], 'route': pair['recovery_path'],
        'source_archive': pair['source_archive'], 'source_archive_sha256': archive_hash,
        'selection': spec['selection'], 'members': members, 'checks': checks,
        'events': [by_seq[n] for n in (4, 5, 6, 10, 11, 12, 13, 14, 17, 18, 19, 20, 23, 24, 27, 28)
                   if n in by_seq],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository-root', type=Path, default=BASE.parent.parent)
    parser.add_argument('--output', type=Path, default=BASE / 'tables')
    args = parser.parse_args()
    data = json.loads((BASE / 'scripts/figures/figure-data.json').read_text(encoding='utf-8-sig'))
    examples = [verify(data, args.repository_root, spec) for spec in EXAMPLES]
    output = {'schema': 2, 'examples': examples,
              'scope': 'Two archived G episodes: one reuse route and one fresh-authorization route. '
                       'Selected to show the mechanism, not typicality or latency.'}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'recovery-example-source.json').write_text(json.dumps(output, indent=2) + '\n',
                                                             encoding='utf-8')
    print(json.dumps([{'pair_id': e['pair_id'], 'route': e['route'], 'checks': e['checks']}
                      for e in examples], indent=1))


if __name__ == '__main__':
    main()
