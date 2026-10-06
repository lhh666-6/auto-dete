import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from phase2.providers import Provider, TransportError, parse_action
root = Path(__file__).resolve().parent
dest = root / 'preflight/availability-openai-system-proxy'
dest.mkdir(exist_ok=False)
observations = []
for model in ['gpt-5.6-terra', 'gpt-6.1-sol']:
    config = {'id': 'A', 'provider': 'openai', 'model': model, 'reasoning_effort': 'low',
        'proxy_url': 'http://127.0.0.1:7897', 'proxy_source': 'Existing enabled Windows user system proxy',
        'temperature': None, 'seed': None, 'max_output_tokens': None,
        'snapshot_or_revision': None, 'sdk': 'codex-cli-0.160.0', 'request_timeout_seconds': 90,
        'output_cap_limitation': 'CLI upstream output cap unavailable; request/response/time caps enforced',
        'interface': 'shared-json-action-facade-v1'}
    try:
        reply = Provider(config).decide([{'kind': 'diagnostic', 'instruction': 'Return kind final with report_json {"availability":"ok"}; no recovery task.'}], dest / model)
        parse_action(reply['raw_action'])
        item = {'status': 'AVAILABLE', 'config': config, 'usage': reply['usage']}
        observations.append(item)
        (dest / 'selected-config-A.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
        print(json.dumps({'model': model, 'status': 'AVAILABLE'}), flush=True)
        break
    except (TransportError, ValueError) as exc:
        code = getattr(exc, 'code', str(exc))
        observations.append({'status': code, 'config': config})
        print(json.dumps({'model': model, 'status': code}), flush=True)
        if code != 'MODEL_UNAVAILABLE': break
(dest / 'results.json').write_text(json.dumps(observations, indent=2), encoding='utf-8')
