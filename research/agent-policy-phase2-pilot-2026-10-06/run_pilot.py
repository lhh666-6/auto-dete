"""Freeze the verified execution package, then run exactly the 16 approved arms."""
import hashlib, json, sys, platform
from importlib.metadata import version
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from phase2.kernel import ROOT, MANIFEST, canonical, fixtures, utc
from phase2.runner import assignment, execute_pair, initial_messages
from phase2.providers import Provider, ACTION_SCHEMA, OUTPUT_RULE

def hashfile(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def prepare():
    configs = [json.loads((ROOT / 'preflight/availability-openai-system-proxy/selected-config-A.json').read_text(encoding='utf-8'))]
    b = json.loads((ROOT / 'preflight/availability-dsh-user-key-retry2/result.json').read_text(encoding='utf-8'))
    if b['status'] != 'AVAILABLE': raise RuntimeError('DSH provider not available')
    configs.append(b['config'])
    review = ROOT / 'reviews/independent-review.md'
    if 'FINAL RETEST' not in review.read_text(encoding='utf-8'): raise RuntimeError('Independent final review missing')
    dest = ROOT / 'frozen-execution'
    dest.mkdir(exist_ok=False)
    for name, obj in [('configs.json', configs), ('fixtures.json', fixtures()), ('assignments.json', assignment()),
                      ('action-schema.json', ACTION_SCHEMA), ('initial-prompts.json', [initial_messages(c) for c in fixtures()])]:
        (dest / name).write_text(canonical(obj), encoding='utf-8')
    (dest / 'output-rule.txt').write_text(OUTPUT_RULE, encoding='utf-8')
    (dest / 'environment.json').write_text(canonical({'python': platform.python_version(),
        'platform': platform.platform(), 'jsonschema': version('jsonschema'), 'pyyaml': version('PyYAML')}), encoding='utf-8')
    files = list((ROOT / 'src').rglob('*.py')) + list((ROOT / 'tests').rglob('*.py'))
    files += list((ROOT / 'frozen-design').glob('*')) + list(dest.iterdir()) + [Path(__file__), review]
    freeze = {'timestamp_utc': utc(), 'status': 'PILOT_EXECUTION_FROZEN_FORMAL_COLLECTION_NOT_FROZEN',
        'online_arms': 16, 'pairs': 8, 'task_instances': 4, 'repetition': 1,
        'selection': 'Availability/interface only; user explicitly replaced B credential with DSH API; no recovery-performance selection',
        'registration': 'Local hash/timestamp, not public preregistration or immutable remote registration',
        'limitations': ['OpenAI CLI upstream max_output_tokens is unavailable; 4096 upstream output cap applies to DeepSeek only. Enforce request, response, tool and elapsed caps for both.',
            'Monetary price/cap unavailable for account-backed CLI; usage retained without inventing currency cost.',
            'Shared action facade, not provider-native tool calling; full visible messages replayed each decision; hidden sessions not cloned.',
            'Local SQLite trusted-host harness implements the frozen semantic interface; not a claim of production-stack integration.',
            'Requested aliases frozen, immutable provider snapshots unavailable; returned identity retained where exposed.'],
        'sha256': {p.relative_to(ROOT).as_posix(): hashfile(p) for p in files}}
    (dest / 'execution-freeze.json').write_text(json.dumps(freeze, indent=2), encoding='utf-8')
    return configs

def run():
    configs = prepare()
    resultdir = ROOT / 'pilot-results'
    resultdir.mkdir(exist_ok=False)
    results = []
    for p in assignment():
        case = next(c for c in fixtures() if c['task_instance_id'] == p['case_id'])
        config = next(c for c in configs if c['id'] == p['config_id'])
        results.append({'assignment': p, 'result': execute_pair(case, Provider(config), resultdir / p['pair_id'], p['order'])})
        (resultdir / 'completed-pairs.json').write_text(canonical(results), encoding='utf-8')
    (resultdir / 'RUN-COMPLETE.json').write_text(canonical({'timestamp_utc': utc(), 'pairs': len(results), 'arms': len(results) * 2,
        'engineering_only': True, 'formal_arms': 0}), encoding='utf-8')
    print('PILOT_COMPLETE_16_ARMS_FORMAL_0', flush=True)

if __name__ == '__main__': run()
