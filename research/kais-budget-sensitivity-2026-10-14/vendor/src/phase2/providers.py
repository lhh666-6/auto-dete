"""Real model transports. Credentials are read only at request time, never logged."""
import json, os, shutil, subprocess, urllib.request, urllib.error, http.client
from pathlib import Path

ACTION_SCHEMA = {'type': 'object', 'properties': {
    'kind': {'type': 'string', 'enum': ['tool', 'final']}, 'tool': {'type': 'string'},
    'arguments_json': {'type': 'string'}, 'report_json': {'type': 'string'}},
    'required': ['kind', 'tool', 'arguments_json', 'report_json'], 'additionalProperties': False}
OUTPUT_RULE = ('Return exactly one JSON object with keys kind, tool, arguments_json, report_json. '
    'kind is tool or final. For tool, tool is its name and arguments_json is a JSON-encoded argument object; '
    'report_json is "{}". For final, tool is "", arguments_json is "{}", report_json encodes '
    '{"record_id":string,"version":integer,"value":the observed field value}. '
    'Choose exactly one next action from the visible conversation. Do not execute outside tools. '
    'Tool names and parameters are in the first message. Tools actually execute after your response. '
    'No prose, code fences, or invented tool results.')


class TransportError(Exception):
    def __init__(self, code, retryable=False, retry_after=0):
        super().__init__(code)
        self.code, self.retryable, self.retry_after = code, retryable, retry_after


def parse_action(text):
    try:
        obj = json.loads(text)
        if not isinstance(obj, dict) or obj.get('kind') not in ('tool', 'final'): raise ValueError()
        if 'arguments_json' in obj:
            obj['arguments'] = json.loads(obj.pop('arguments_json'))
            obj['report'] = json.loads(obj.pop('report_json'))
        if obj['kind'] == 'tool' and (not isinstance(obj.get('tool'), str) or not isinstance(obj.get('arguments'), dict)): raise ValueError()
        if obj['kind'] == 'final' and not isinstance(obj.get('report'), dict): raise ValueError()
        return obj
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ValueError('INVALID_ACTION_FORMAT') from exc


class Provider:
    def __init__(self, config): self.config = config

    def decide(self, messages, directory, timeout=90):
        directory.mkdir(parents=True, exist_ok=True)
        prompt = OUTPUT_RULE + '\nVISIBLE CONVERSATION:\n' + json.dumps(messages,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
        (directory/'prompt.txt').write_text(prompt,encoding='utf-8')
        if self.config['provider'] == 'openai': return self.codex(prompt, directory, timeout)
        return self.deepseek(prompt, directory, timeout)

    def codex(self, prompt, directory, timeout):
        binary = shutil.which('codex')
        if not binary: raise TransportError('CODEX_NOT_FOUND')
        schema = directory / 'action-schema.json'
        schema.write_text(json.dumps(ACTION_SCHEMA), encoding='utf-8')
        output = directory / 'last-message.txt'
        work = directory / 'empty-workspace'
        work.mkdir()
        # Explicit local file rules avoid inherited project instructions.
        (work / 'AGENTS.md').write_text('Only return the requested JSON decision. Use no native tools.\n', encoding='utf-8')
        cmd = [binary, '-a', 'never']
        for feature in ['shell_tool', 'view_image', 'browser_use', 'in_app_browser', 'computer_use',
                        'image_generation', 'apps', 'skill_search', 'tool_suggest', 'multi_agent']:
            cmd += ['--disable', feature]
        cmd += ['exec', '--ephemeral', '--json', '--ignore-user-config', '--ignore-rules', '--skip-git-repo-check',
            '-m', self.config['model'], '-c', 'model_reasoning_effort="low"', '-s', 'read-only',
            '-C', str(work.resolve()), '--output-schema', str(schema.resolve()), '-o', str(output.resolve()), '-']
        env = os.environ.copy()
        for key in ['CODEX_THREAD_ID', 'CODEX_SESSION_ID', 'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_BASE_URL', 'OPENAI_API_KEY', 'DEEPSEEK_API_KEY', 'PHASE2_DSH_API_KEY']:
            env.pop(key, None)
        if self.config.get('proxy_url'):
            env['HTTPS_PROXY'] = self.config['proxy_url']
            env['HTTP_PROXY'] = self.config['proxy_url']
        try:
            p = subprocess.run(cmd, input=prompt, text=True, encoding='utf-8', errors='replace',
                capture_output=True, env=env, timeout=timeout, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        except subprocess.TimeoutExpired as exc:
            raw = exc.stdout or b''
            (directory / 'stdout.jsonl').write_bytes(raw if isinstance(raw, bytes) else raw.encode())
            raise TransportError('CODEX_TIMEOUT', True) from exc
        (directory / 'stdout.jsonl').write_text(p.stdout, encoding='utf-8')
        (directory / 'stderr.txt').write_text(p.stderr, encoding='utf-8')
        events = []
        for line in p.stdout.splitlines():
            try: events.append(json.loads(line))
            except json.JSONDecodeError: pass
        if p.returncode != 0:
            msg = ' '.join(str(e.get('message', '')) for e in events if e.get('type') == 'error')
            unavailable = any(w in msg.lower() for w in ['not supported', 'not available', 'does not exist', 'unsupported', 'not found'])
            raise TransportError('MODEL_UNAVAILABLE' if unavailable else 'CODEX_EXIT_' + str(p.returncode), not unavailable)
        # Unexpected native actions are protocol violations, not allowed tool calls.
        native = [e for e in events if e.get('type') == 'item.completed' and
                  e.get('item', {}).get('type') not in ('agent_message', 'reasoning')]
        if native: raise TransportError('UNEXPECTED_NATIVE_TOOL')
        usage = next((e.get('usage', {}) for e in reversed(events) if e.get('type') == 'turn.completed'), {})
        raw = output.read_text(encoding='utf-8') if output.exists() else ''
        return {'raw_action': raw, 'usage': usage, 'model': None,
            'provider_request_id': next((e.get('thread_id') for e in events if e.get('type') == 'thread.started'), None),
            'returned_revision': None}

    def deepseek(self, prompt, directory, timeout):
        token, base = os.environ.get('ANTHROPIC_AUTH_TOKEN'), self.config.get('base_url') or os.environ.get('ANTHROPIC_BASE_URL')
        if os.environ.get('PHASE2_DSH_API_KEY'):
            token=os.environ['PHASE2_DSH_API_KEY']
        elif self.config.get('credential_file'):
            path = self.config['credential_file'].replace("'", "''")
            script = "$s=(Get-Content -LiteralPath '" + path + "' -Raw).Trim() | ConvertTo-SecureString; $p=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($s); try {[Runtime.InteropServices.Marshal]::PtrToStringBSTR($p)} finally {[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($p)}"
            credential_env = os.environ.copy()
            credential_env.pop('PSModulePath', None)
            p = subprocess.run([shutil.which('pwsh') or 'powershell', '-NoProfile', '-NonInteractive', '-Command', script],
                capture_output=True, text=True, env=credential_env, timeout=10, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            if p.returncode: raise TransportError('LOCAL_CREDENTIAL_DECRYPT_FAILED')
            token = p.stdout.strip()
        if not token or not base: raise TransportError('DEEPSEEK_CREDENTIAL_UNAVAILABLE')
        body = {'model': self.config['model'], 'max_tokens': self.config.get('max_output_tokens',4096), 'temperature': self.config.get('temperature',0),
                'messages': [{'role': 'user', 'content': prompt}]}
        req = urllib.request.Request(base.rstrip('/') + '/v1/messages', data=json.dumps(body).encode(),
            headers={'x-api-key': token, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            # Body is diagnostic only; do not print tokens or headers.
            (directory / 'http-error.txt').write_bytes(exc.read())
            delay = exc.headers.get('Retry-After', '0')
            try: delay = float(delay)
            except ValueError: delay = 0
            raise TransportError('HTTP_' + str(exc.code), exc.code == 429 or exc.code >= 500, delay) from exc
        except (TimeoutError, urllib.error.URLError, ConnectionResetError, ConnectionAbortedError, http.client.IncompleteRead, http.client.RemoteDisconnected) as exc:
            partial=getattr(exc,'partial',b'')
            if isinstance(partial,bytes): (directory/'partial-response.bin').write_bytes(partial)
            (directory/'transport-error.json').write_text(json.dumps({'exception_type':type(exc).__name__}),encoding='utf-8')
            raise TransportError('DEEPSEEK_TRANSPORT', True) from exc
        (directory / 'response.json').write_bytes(raw)
        try:
            obj = json.loads(raw)
            if not isinstance(obj, dict) or not isinstance(obj.get('content'), list): raise ValueError()
            answer = ''.join(b.get('text', '') for b in obj['content'] if b.get('type') == 'text')
        except (ValueError, TypeError, AttributeError) as exc:
            raise TransportError('PROVIDER_MALFORMED_ENVELOPE') from exc
        return {'raw_action': answer, 'usage': obj.get('usage', {}), 'model': obj.get('model'),
                'provider_request_id': obj.get('id'), 'returned_revision': None}
