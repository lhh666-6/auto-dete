"""Independent post-run action/source audit, not imported by the runner/gate."""
import json, sys, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / 'pilot-results'
if not (RESULTS / 'RUN-COMPLETE.json').exists(): raise SystemExit('Online pilot unfinished')

def encoded(obj): return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
errors, responses, tool_calls, feedback = [], 0, 0, 0
for file in RESULTS.glob('*/*/events.jsonl'):
    directory = file.parent
    events = [json.loads(line) for line in file.read_text(encoding='utf-8').splitlines()]
    by_request = {}
    for e in events:
        if e['event_type'] == 'model_response':
            p = e['payload']
            by_request[p['model_request_id']] = e
            responses += 1
            raw = p['response']
            refs = e['artifacts']
            config = e['agent_config_id']
            if config == 'A':
                ref = next((r for r in refs if r['relative_path'].endswith('/last-message.txt')), None)
                actual = (directory / ref['relative_path']).read_text(encoding='utf-8') if ref else None
            else:
                ref = next((r for r in refs if r['relative_path'].endswith('/response.json')), None)
                obj = json.loads((directory / ref['relative_path']).read_text(encoding='utf-8')) if ref else {}
                actual = ''.join(b['text'] for b in obj.get('content', []) if b.get('type') == 'text')
                if obj.get('id') != p['provider_request_id']: errors.append(str(file) + ':provider_response_id')
            if actual != raw: errors.append(str(file) + ':provider_raw_response_mismatch')
        if e['event_type'] == 'tool_call':
            p = e['payload']
            response = by_request.get(p['model_request_id'])
            if not response:
                errors.append(str(file) + ':agent_call_without_online_response'); continue
            try:
                action = json.loads(response['payload']['response'])
                args = json.loads(action['arguments_json'])
                if action['kind'] != 'tool' or action['tool'] != p['tool_name'] or encoded(args) != encoded(p['arguments']):
                    errors.append(str(file) + ':agent_action_mismatch')
                tool_calls += 1
            except (ValueError, KeyError, TypeError): errors.append(str(file) + ':unparseable_agent_action')
        if e['event_type'] == 'feedback_delivered':
            response = by_request.get(e['payload']['next_model_request_id'])
            if not response: errors.append(str(file) + ':feedback_no_actual_provider_response')
            else: feedback += 1
result = {'status': 'PASS' if not errors else 'FAIL', 'engineering_only': True,
    'actual_model_responses_verified': responses, 'agent_tool_calls_grounded_in_raw_outputs': tool_calls,
    'delivered_feedback_with_provider_response': feedback, 'errors': errors,
    'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(RESULTS / 'online-provenance-verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
if errors: raise SystemExit(1)
