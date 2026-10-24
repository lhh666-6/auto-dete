"""Verify and document the archived example in OR1 S12.6; no model calls."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath

BASE = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository-root', type=Path, default=BASE.parent.parent)
    parser.add_argument('--output', type=Path, default=BASE / 'tables')
    args = parser.parse_args()
    data = json.loads((BASE / 'scripts/figures/figure-data.json').read_text(encoding='utf-8-sig'))
    pair = next(p for p in data['g_pairs'] if p['id'] == 'FORMAL-G-002-B')
    archive = args.repository_root / pair['source_archive']
    archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
    assert archive_hash == next(s['sha256'] for s in data['sources'] if s['path'] == pair['source_archive'])
    member = pair['archive_members']['bound']['events']
    parent = PurePosixPath(member).parent
    checks, members = {}, []
    with zipfile.ZipFile(archive) as z:
        def read(name, expected=None):
            raw = z.read(name)
            digest = hashlib.sha256(raw).hexdigest()
            if expected:
                assert digest == expected, name
            members.append({'member': name, 'sha256': digest})
            return raw.decode('utf-8-sig')

        events = [json.loads(line) for line in read(member).splitlines() if line.strip()]
        by_seq = {e['sequence']: e for e in events}
        rejection = by_seq[6]['payload']
        assert rejection['reason_code'] == 'INSTANCE_MISMATCH'
        assert rejection['candidate_id'] == 'c2' and rejection['reviewed_candidate_id'] == 'c1'
        assert rejection['same_context'] and rejection['same_value'] and rejection['state_unchanged']
        feedback = by_seq[10]['payload']
        input_ref = feedback['agent_input_message_ref']
        saved_input = json.loads(read(str(parent / input_ref['relative_path']), input_ref['sha256']))
        assert feedback['delivered']
        grant = next(x['result'] for x in saved_input if x.get('tool_name') == 'request_authorization')
        assert grant['authorization_id'] == 'a1' and grant['reviewed_candidate_id'] == 'c1'
        assert grant['authorized_value'] == 3412
        assert grant['reviewed_candidate']['context']['proposal_value_payload'] == '3405'
        call = by_seq[11]['payload']
        assert call['tool_name'] == 'commit'
        assert {k: call['arguments'][k] for k in ('candidate_id', 'authorization_id', 'committed_value')} == {
            'candidate_id': 'c1', 'authorization_id': 'a1', 'committed_value': 3412}
        result = by_seq[12]['payload']
        states = [json.loads(read(str(parent / result[k]['relative_path']), result[k]['sha256']))
                  for k in ('state_before_ref', 'state_after_ref')]
        assert len(states[1]['transitions']) - len(states[0]['transitions']) == 1
        assert result['result']['transition_id'] == 'transition-1' and result['result']['version'] == 3
        receipt = by_seq[18]['payload']
        assert by_seq[17]['payload']['tool_name'] == 'get_receipt'
        assert by_seq[17]['payload']['arguments']['commit_request_id'] == 'request-2'
        for key in ('state_before_ref', 'state_after_ref'):
            read(str(parent / receipt[key]['relative_path']), receipt[key]['sha256'])
        assert receipt['state_before_ref']['sha256'] == receipt['state_after_ref']['sha256']
        assert receipt['result']['transition_id'] == 'transition-1'
        bound_calls = [e for e in events if e['event_type'] == 'tool_call' and e['origin'] == 'agent']
        assert len(bound_calls) == 2
        context = [json.loads(line) for line in read(pair['archive_members']['context']['events']).splitlines() if line.strip()]
        assert not [e for e in context if e['event_type'] == 'tool_call' and e['origin'] == 'agent']
        checks = {'saved_grant_available': True, 'identity_only_rejection': True,
                  'durable_recovery_transitions_added': 1, 'recovery_calls': 1,
                  'confirmation_calls': 1, 'context_agent_calls': 0,
                  'receipt_does_not_mutate_state': True}
    output = {'pair_id': pair['id'], 'cohort': pair['cohort'], 'source_archive': pair['source_archive'],
              'source_archive_sha256': archive_hash, 'members': members, 'checks': checks,
              'selection': 'Illustration of reuse followed by confirmation; not a representative latency estimate.',
              'events': [by_seq[n] for n in (4, 5, 6, 10, 11, 12, 17, 18)]}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'recovery-example-source.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'pair_id': pair['id'], 'checks': checks}))


if __name__ == '__main__':
    main()
