import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from phase2.providers import Provider, TransportError, parse_action
root = Path(__file__).resolve().parent
dest = root / ('preflight/availability-dsh-user-key' + (sys.argv[1] if len(sys.argv) > 1 else ''))
dest.mkdir(exist_ok=False)
config = {'id': 'B', 'provider': 'deepseek', 'model': 'deepseek-v4-flash',
    'base_url': 'https://api.deepseek.com/anthropic',
    'credential_file': str(Path.home() / '.codex/local-secrets/phase2-dsh-api.dpapi'),
    'credential_source': 'User-authorized DSH API credential, Windows user encrypted outside repository',
    'temperature': 0, 'seed': None, 'reasoning_effort': None, 'max_output_tokens': 4096,
    'snapshot_or_revision': None, 'sdk': 'urllib/Python-3.11', 'request_timeout_seconds': 90,
    'interface': 'shared-json-action-facade-v1'}
try:
    response = Provider(config).decide([{'kind': 'diagnostic', 'instruction': 'Return kind final, report_json {"availability":"ok"}; no task or recovery experiment.'}], dest / 'request')
    parse_action(response['raw_action'])
    result = {'status': 'AVAILABLE', 'config': config, 'usage': response['usage'], 'returned_model': response['model']}
except (TransportError, ValueError) as exc:
    result = {'status': getattr(exc, 'code', str(exc)), 'config': config}
(dest / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({'id': 'B', 'model': config['model'], 'status': result['status']}))
