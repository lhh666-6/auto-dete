"""Deterministic trusted host. No model actions or recovery decisions here."""
import copy, hashlib, json, math, sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = json.loads((ROOT / 'frozen-design/protocol-manifest.json').read_text(encoding='utf-8'))
TOOLS = {t['function']['name']: t['function']['parameters'] for t in
         json.loads((ROOT / 'frozen-design/tool-definitions.json').read_text(encoding='utf-8-sig'))['tools']}
KEYS = MANIFEST['context_field_whitelist']


def canonical(value):
    # JSON retains integer vs float spelling; disallow Python-only/ambiguous keys.
    def check(x):
        if isinstance(x, float) and not math.isfinite(x): raise ValueError('nonfinite')
        if isinstance(x, dict):
            if any(not isinstance(k, str) for k in x): raise ValueError('non-string key')
            for v in x.values(): check(v)
        elif isinstance(x, list):
            for v in x: check(v)
        elif x is not None and type(x) not in (str, int, float, bool): raise ValueError('not JSON')
    check(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(value): return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()
def utc(): return datetime.now(timezone.utc).isoformat()


def fixtures():
    cases = []
    for i, pid in enumerate(MANIFEST['pilot']['case_ids']):
        scenario = pid.split('-')[1]
        cents = pid == 'PILOT-N-02'
        field = 'net_amount_cents' if cents else 'quantity'
        value = 20017 if cents else 211 + i * 7
        cases.append({'task_instance_id': pid, 'scenario': scenario,
            'record_id': 'P2-' + pid, 'field_key': field,
            'domain': 'invoice_net_amount_cents' if cents else 'purchase_quantity',
            'baseline_values': {field: 700 if cents else 7, 'reference_note': 'pilot-review-reference'},
            'source_proposal_value': value, 'host_authorized_value': value + (25 if cents else 1)})
    return cases


class Host:
    def __init__(self, case, policy='bound'):
        self.policy = policy
        self.case = copy.deepcopy(case)
        evidence = MANIFEST['source_evidence_template'].format(**case)
        head = {'version': 1, 'values': copy.deepcopy(case['baseline_values']),
                'sources': {k: case.get('baseline_sources', {}).get(k, 'baseline:' + k) for k in case['baseline_values']}}
        self.state = {'case': self.case, 'baseline': copy.deepcopy(head), 'head': head,
            'versions': [copy.deepcopy(head)], 'transitions': [], 'external_advances': [],
            'candidates': {}, 'grants': {}, 'idempotency': {}, 'receipts': {},
            'evidence': {'E1': {'bytes': evidence, 'sha256': hashlib.sha256(evidence.encode()).hexdigest(),
                              'locator': 'source-supported-value'}},
            'candidate_counter': 0, 'grant_counter': 0, 'request_counter': 0,
            'reviewer_active': True, 'preview_ids': [], 'after_checkpoint': False,
            'current_evidence_ref': 'E1', 'receipt_outage_used': False}
        if case.get('evidence_snapshots'):
            self.state['evidence'] = {key: {**copy.deepcopy(value),
                'sha256': hashlib.sha256(value['bytes'].encode()).hexdigest()}
                for key, value in case['evidence_snapshots'].items() if key == 'E1'}
        for _ in range(1, case.get('baseline_version', 1)):
            self.advance(case['baseline_values']['reference_note'])

    @classmethod
    def from_state(cls, state, policy):
        obj = cls.__new__(cls)
        obj.policy, obj.state = policy, copy.deepcopy(state)
        obj.case = obj.state['case']
        return obj

    def persist(self, path):
        with closing(sqlite3.connect(path)) as db, db:
            db.execute('CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)')
            db.execute('INSERT OR REPLACE INTO state VALUES (1, ?)', (canonical(self.state),))

    @classmethod
    def load(cls, path, policy):
        with closing(sqlite3.connect(path)) as db: state = json.loads(db.execute('SELECT payload FROM state WHERE id=1').fetchone()[0])
        return cls.from_state(state, policy)

    def error(self, code, **data): return {'status': 'rejected', 'error_code': code, **data}

    def valid(self, candidate):
        if candidate is None: return 'CANDIDATE_UNKNOWN'
        cert_body = {k: v for k, v in candidate.items() if k != 'certificate_id'}
        if candidate['certificate_id'] != digest(cert_body) or candidate['context_hash'] != digest(candidate['context']): return 'CERTIFICATE_INVALID'
        k = candidate['context']
        e = self.state['evidence'].get(k['evidence_file_id'])
        if not e or hashlib.sha256(e['bytes'].encode()).hexdigest() != k['evidence_hash'] or e['locator'] != k['evidence_locator']: return 'EVIDENCE_INVALID'
        if self.case['scenario']=='E' and k['evidence_file_id']!=self.state['current_evidence_ref']: return 'EVIDENCE_SUPERSEDED'
        if k['expected_fact_version'] != self.state['head']['version']: return 'STALE_VERSION'
        if canonical(k['proposal_value_payload']) != canonical(canonical(self.case['source_proposal_value'])): return 'SOURCE_UNSUPPORTED'
        if any(k.get(key)!=value for key,value in self.case.get('retained_metadata',{}).items()): return 'SOURCE_INVALID'
        if k['target_record_id'] != self.case['record_id'] or k['field_key'] != self.case['field_key']: return 'TARGET_INVALID'
        return None

    def call(self, tool, args):
        import jsonschema
        if tool not in TOOLS: return self.error('UNKNOWN_TOOL')
        try: jsonschema.validate(args, TOOLS[tool]); canonical(args)
        except (jsonschema.ValidationError, ValueError): return self.error('INVALID_ARGUMENTS')
        s = self.state
        if tool == 'get_state':
            if args['record_id'] != self.case['record_id']: return self.error('TARGET_INVALID')
            return {'status': 'ok', **copy.deepcopy(s['head']), 'record_id': self.case['record_id'],
                    'root_certificate_id': 'root-v' + str(s['head']['version']), 'evidence_ref': s['current_evidence_ref'],
                    'capabilities': list(TOOLS), 'field_order':self.case.get('field_order',list(s['head']['values']))}
        if tool == 'inspect_evidence':
            e = s['evidence'].get(args['evidence_ref'])
            return {'status': 'ok', **copy.deepcopy(e)} if e else self.error('EVIDENCE_UNKNOWN')
        if tool == 'propose':
            if args['record_id'] != self.case['record_id'] or args['field_key'] != self.case['field_key']: return self.error('TARGET_INVALID')
            if args['parent_certificate_id'] != 'root-v' + str(s['head']['version']): return self.error('PARENT_INVALID')
            e = s['evidence'].get(args['evidence_ref'])
            if not e or hashlib.sha256(e['bytes'].encode()).hexdigest() != e['sha256']: return self.error('EVIDENCE_INVALID')
            if canonical(args['proposal_value']) != canonical(self.case['source_proposal_value']): return self.error('SOURCE_UNSUPPORTED')
            s['candidate_counter'] += 1
            cid = 'c' + str(s['candidate_counter'])
            context = dict(zip(KEYS, [self.case['record_id'], self.case['field_key'], canonical(args['proposal_value']),
                s['head']['version'], self.case['domain'], '1', '1', args['evidence_ref'], e['sha256'],
                e['locator'], 'AI_SUGGESTION', 'pilot-source-adapter', '1', 'selection:' + self.case['task_instance_id'],
                'SELECTED', 1.0, [args['parent_certificate_id']]]))
            for key, value in self.case.get('retained_metadata', {}).items():
                if key in KEYS: context[key] = copy.deepcopy(value)
            c = {'candidate_id': cid, 'created_at': utc(), 'context': context, 'context_hash': digest(context),
                 'envelope_metadata': copy.deepcopy(self.case.get('candidate_envelope', {}))}
            c['certificate_id'] = digest(c)
            s['candidates'][cid] = c
            if s['after_checkpoint']: s['preview_ids'].append(cid)
            return {'status': 'ok', **copy.deepcopy(c)}
        if tool in ('verify', 'request_authorization'):
            c = s['candidates'].get(args['candidate_id'])
            reason = self.valid(c)
            if reason: return self.error(reason)
            if tool == 'verify': return {'status': 'ok', 'candidate_id': c['candidate_id'], 'verified': True}
            if not s['reviewer_active']: return self.error('REVIEWER_INVALID')
            for g in s['grants'].values():
                if g['status'] == 'active': g['status'] = 'superseded'
            s['grant_counter'] += 1
            aid = 'a' + str(s['grant_counter'])
            g = {'authorization_id': aid, 'reviewed_candidate_id': c['candidate_id'],
                'reviewed_candidate': copy.deepcopy(c), 'authorized_value': self.case['host_authorized_value'],
                'context': copy.deepcopy(c['context']), 'status': 'active', 'reviewer_id': 'trusted-host-reviewer',
                'issued_at': utc(), 'record_id': self.case['record_id'], 'field_key': self.case['field_key']}
            s['grants'][aid] = g
            return {**copy.deepcopy(g), 'status': 'ok', 'authorization_status': g['status']}
        if tool == 'get_receipt':
            if self.case['scenario'] == 'R' and s['transitions'] and not s['receipt_outage_used']:
                s['receipt_outage_used'] = True
                return self.error('CAPABILITY_UNAVAILABLE')
            r = s['receipts'].get(args['commit_request_id'])
            return copy.deepcopy(r) if r else self.error('RECEIPT_UNKNOWN')
        if tool == 'commit': return self.commit(args)
        raise AssertionError(tool)

    def commit(self, args):
        s = self.state
        key = args['idempotency_key']
        if key in s['idempotency']:
            saved = s['idempotency'][key]
            if canonical(saved['arguments']) == canonical(args): return copy.deepcopy(saved['result'])
            return self.error('IDEMPOTENCY_COLLISION')
        s['request_counter'] += 1
        rid = 'request-' + str(s['request_counter'])
        c, g = s['candidates'].get(args['candidate_id']), s['grants'].get(args['authorization_id'])
        flags = {'authorization_exists_active_unconsumed': bool(g and g['status'] == 'active'),
                 'reviewer_valid_at_commit_entry': s['reviewer_active']}
        reason = None
        if not flags['authorization_exists_active_unconsumed']: reason = 'AUTHORIZATION_INVALID'
        elif not flags['reviewer_valid_at_commit_entry']: reason = 'REVIEWER_INVALID'
        else: reason = self.valid(c)
        if not reason and (g['record_id'] != self.case['record_id'] or g['field_key'] != self.case['field_key']): reason = 'TARGET_INVALID'
        same_k = bool(c and g and canonical(c['context']) == canonical(g['context']))
        same_i = bool(c and g and c['candidate_id'] == g['reviewed_candidate_id'])
        if not reason and canonical(args['committed_value']) != canonical(g['authorized_value']): reason = 'AUTHORIZED_VALUE_MISMATCH'
        common_pass = reason is None
        if not reason and not same_k: reason = 'CONTEXT_MISMATCH'
        if not reason and self.policy == 'bound' and not same_i: reason = 'INSTANCE_MISMATCH'
        decision = {'common_guard_pass': common_pass, 'guard_results': flags, 'same_context': same_k,
                    'same_instance': same_i, 'same_value': bool(c and g and canonical(c['context']['proposal_value_payload']) == canonical(g['context']['proposal_value_payload']))}
        if reason: result = self.error(reason, commit_request_id=rid, decision=decision)
        else:
            pre = copy.deepcopy(s['head'])
            post = copy.deepcopy(pre)
            post['version'] += 1
            post['values'][self.case['field_key']] = copy.deepcopy(args['committed_value'])
            tid = 'transition-' + str(len(s['transitions']) + 1)
            post['sources'][self.case['field_key']] = tid
            t = {'transition_id': tid, 'pre': pre, 'post': post, 'candidate': copy.deepcopy(c),
                 'grant': copy.deepcopy(g), 'reviewer_active': s['reviewer_active'],
                 'evidence': copy.deepcopy(s['evidence']), 'current_evidence_ref':s['current_evidence_ref'], 'arguments': copy.deepcopy(args),
                 'commit_request_id': rid}
            s['transitions'].append(t)
            s['head'] = post
            s['versions'].append(copy.deepcopy(post))
            g['status'] = 'consumed'
            result = {'status': 'ok', 'commit_request_id': rid, 'transition_id': tid,
                      'version': post['version'], 'committed_value': args['committed_value'], 'decision': decision}
        s['receipts'][rid] = copy.deepcopy(result)
        s['idempotency'][key] = {'arguments': copy.deepcopy(args), 'result': copy.deepcopy(result)}
        return result

    def publish_evidence(self):
        value=copy.deepcopy(self.case['evidence_snapshots']['E2'])
        value['sha256']=hashlib.sha256(value['bytes'].encode()).hexdigest()
        self.state['evidence']['E2']=value
        self.state['current_evidence_ref']='E2'

    def advance(self, note):
        pre = copy.deepcopy(self.state['head'])
        post = copy.deepcopy(pre)
        post['version'] += 1
        post['values']['reference_note'] = note
        post['sources']['reference_note'] = 'external-v' + str(post['version'])
        self.state['external_advances'].append({'pre': pre, 'post': post})
        self.state['head'] = post
        self.state['versions'].append(copy.deepcopy(post))
