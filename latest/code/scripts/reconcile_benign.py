"""Recompute missingness from immutable normalized Final rows; no hosted calls."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = json.loads(args.runs.read_text(encoding='utf-8'))
    benign = [r for r in rows if r['scenario_id'] in ('B1', 'B2', 'B3', 'B4')]
    missing = [r for r in benign if not r['agent_behavior_evaluable']]
    successes = sum(r['agent_task_completed'] is True for r in benign)
    summary = {
        'source_sha256': hashlib.sha256(args.runs.read_bytes()).hexdigest(),
        'planned_benign': len(benign),
        'evaluable': len(benign) - len(missing),
        'strict_success': successes,
        'unscored': len(missing),
        'unscored_rows': [
            {k: r[k] for k in ('run_id', 'model_config_id', 'terminal_class')}
            for r in missing
        ],
        'strict_unidentified_outcome_bounds': [
            successes / len(benign), (successes + len(missing)) / len(benign)
        ],
    }
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(summary, output, indent=2)
    print(f"{successes}/{len(benign)} demonstrated strict successes; {len(missing)} unscored")


if __name__ == '__main__':
    main()
