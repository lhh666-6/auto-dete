"""Availability checks contain no recovery task; never select by pilot performance."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from phase2.providers import Provider, TransportError, parse_action

root = Path(__file__).resolve().parent
dest = root / 'preflight/availability'
dest.mkdir(parents=True, exist_ok=True)
if (dest / 'selected-configs.json').exists(): raise SystemExit('Already selected; no model reselection')
diagnostic = [{'kind': 'diagnostic', 'instruction': 'Return kind final, report_json {"availability":"ok"}; this tests JSON output only.'}]
configs, observations = [], []
for cid, provider, models in [('A', 'openai', ['gpt-5.6-terra', 'gpt-6.1-sol']),
                              ('B', 'deepseek', ['deepseek-v4-flash'])]:
    for model in models:
        c = {'id': cid, 'provider': provider, 'model': model, 'reasoning_effort': 'low' if cid == 'A' else None,
             'temperature': 0 if cid == 'B' else None, 'seed': None,
             'interface': 'shared-json-action-facade-v1', 'max_output_tokens': 4096 if cid == 'B' else None,
             'output_cap_limitation': 'CLI upstream output cap unavailable' if cid == 'A' else None,
             'snapshot_or_revision': None, 'sdk': 'codex-cli-0.160.0' if cid == 'A' else 'urllib/Python-3.11',
             'request_timeout_seconds': 90}
        try:
            reply = Provider(c).decide(diagnostic, dest / model)
            parse_action(reply['raw_action'])
            observations.append({'config': c, 'status': 'AVAILABLE', 'returned_model': reply['model'], 'usage': reply['usage']})
            configs.append(c)
            print(json.dumps({'id': cid, 'model': model, 'status': 'AVAILABLE'}), flush=True)
            break
        except (TransportError, ValueError) as exc:
            code = getattr(exc, 'code', str(exc))
            observations.append({'config': c, 'status': code})
            print(json.dumps({'id': cid, 'model': model, 'status': code}), flush=True)
            if code != 'MODEL_UNAVAILABLE': break
(dest / 'availability-results.json').write_text(json.dumps(observations, indent=2), encoding='utf-8')
if len(configs) != 2: raise SystemExit('Two real configurations unavailable; pilot not started')
(dest / 'selected-configs.json').write_text(json.dumps(configs, indent=2), encoding='utf-8')
