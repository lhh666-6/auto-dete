"""Audit frozen input/prompt consistency; does not assign semantic labels."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--final-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = json.loads((args.final_root/'normalized/runs.json').read_text(encoding='utf-8'))
    audit = []
    for row in rows:
        folder = args.final_root/'runs'/row['run_id']
        raw = (folder/'prepared.json').read_bytes()
        prepared = json.loads(raw)
        prompt = (folder/'prompt.txt').read_text(encoding='utf-8')
        embedded, _ = json.JSONDecoder().raw_decode(prompt.split('Context: ', 1)[1])
        assert embedded == prepared, row['run_id']
        keys = [field['field_key'] for field in prepared['fields']]
        assert len(keys) == len(set(keys))
        assert set(prepared.get('declared_values_by_field', {})) <= set(keys)
        audit.append({'run_id': row['run_id'], 'scenario_id': row['scenario_id'],
                      'prepared_sha256': hashlib.sha256(raw).hexdigest(),
                      'prompt_context_equal': True, 'field_keys': keys,
                      'input_keys': sorted(prepared),
                      'has_explicit_target_key': any('target' in k or 'intended' in k for k in prepared)})
    result = {'scope': 'prepared/prompt consistency and declared-field checks; semantic interpretation is separate', 'rows': audit}
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2)
    print(dict(Counter(row['scenario_id'] for row in audit)))


if __name__ == '__main__':
    main()
