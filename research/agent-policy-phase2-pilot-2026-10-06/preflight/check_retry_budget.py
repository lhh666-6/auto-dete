"""Additional deterministic transport-failure check, excluded from online data."""
import json, sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from phase2.kernel import ROOT, Host, fixtures, canonical
from phase2.providers import TransportError
from phase2.runner import Log, loop, initial_messages, finish, validate_run
from phase2.oracle import integrity

class Unavailable:
    config = {'id': 'FAULT-CHECK', 'provider': 'deterministic_fixture', 'model': 'no-real-model'}
    def __init__(self): self.attempts = 0
    def decide(self, *args):
        self.attempts += 1
        raise TransportError('SIMULATED_429', True, 3)

directory = ROOT / 'preflight/deterministic-transport-failure'
case = fixtures()[0]
h, p = Host(case), Unavailable()
log = Log(directory, case, p.config, 'pre_policy')
ref = log.snapshot(h, 'initial')
log.event('initialization', {'state_ref': ref}, origin='harness', artifacts=[ref])
with patch('phase2.runner.time.sleep') as delay:
    out = loop(h, p, initial_messages(case), log, prefix=True)
    waits = [call.args[0] for call in delay.call_args_list]
finish(log, h, out)
assert p.attempts == 3 and waits == [3, 8]
assert out['terminal'] == 'runtime_error' and out['tools'] == 0
assert integrity(h.state)['I'] == 1 and h.state['head']['version'] == 1
assert validate_run(directory)['errors'] == []
result = {'status': 'PASS', 'engineering_only': True, 'online_model_calls': 0,
    'attempts': p.attempts, 'max_retries': 2, 'retry_after_respected': True,
    'wait_seconds_without_actual_sleep': waits, 'semantic_tool_events': 0,
    'final_I': 1, 'head_version': 1}
(directory / 'verification.json').write_text(canonical(result), encoding='utf-8')
print(json.dumps(result))
