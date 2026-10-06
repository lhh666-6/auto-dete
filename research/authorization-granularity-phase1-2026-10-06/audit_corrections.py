"""Offline audit. Frozen databases are opened mode=ro; no model/API calls."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sqlite3
import sys
import unicodedata
from urllib.parse import quote, unquote

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
FINAL = ROOT / 'revisions/2026-08-27-jss-r21-live-agent-performance/evidence/agent-authority-benchmark-v2/final/2026-09-01-three-config-10x'
TABLES = ('forms', 'form_fields', 'record_versions', 'candidate_certificates', 'human_decisions', 'authorization_bindings', 'fact_transitions', 'evidence_files')
AUTHORITY = ROOT / 'revisions/2026-09-12-r30-submission-candidate/code/implementation-fixed/app/domain/authority.py'
spec = importlib.util.spec_from_file_location('phase1_authority', AUTHORITY)
authority = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = authority
spec.loader.exec_module(authority)
CONTENT_KEYS = ('candidate_id', 'field_key', 'value_payload', 'evidence_hash', 'evidence_locator', 'template_id', 'template_version', 'source_kind', 'producer_id', 'producer_version', 'selection_artifact_id', 'confidence', 'selection_state', 'lineage_parent_ids', 'target_record_id', 'expected_fact_version', 'created_at')

def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))

def timestamp(value):
    parsed = datetime.fromisoformat(value)
    # SQLAlchemy's historical SQLite adapter strips the offset; it stored UTC.
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed

def certificate_content(row):
    content = {k: row[k] for k in CONTENT_KEYS}
    content['lineage_parent_ids'] = json.loads(content['lineage_parent_ids'])
    content['created_at'] = timestamp(content['created_at']).isoformat()
    return content

def locator(evidence):
    uri = unicodedata.normalize('NFC', evidence['uri']).replace('\\', '/')
    parts = [unicodedata.normalize('NFC', unquote(s)) for s in uri.split('/')]
    if uri.startswith('/') or (len(uri) >= 2 and uri[1] == ':') or any(s in ('', '.', '..') for s in parts):
        raise ValueError('nonportable evidence URI')
    return json.dumps({'form_id': unicodedata.normalize('NFC', evidence['form_id']), 'related_field_id': unicodedata.normalize('NFC', evidence['related_field_id']) if evidence['related_field_id'] else None, 'uri': '/'.join(quote(s, safe='-._~') for s in parts), 'v': 1}, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def load_snapshot(run):
    with sqlite3.connect((run / 'data/database/demo.db').resolve().as_uri() + '?mode=ro', uri=True) as con:
        con.row_factory = sqlite3.Row
        data = {t: [dict(r) for r in con.execute('SELECT * FROM ' + t)] for t in TABLES}
    data.update({n: read(run / (n + '.json')) for n in ('prepared', 'host-challenge', 'events')})
    data['evidence_bytes'] = {e['file_id']: (run / 'data/evidence' / e['uri']).read_bytes() for e in data['evidence_files']}
    return data

def audit_snapshot(data, target_id):
    failures, details = [], []
    metrics = Counter()
    def check(ok, code, detail=''):
        if not ok:
            if code not in failures:
                failures.append(code)
            details.append({'code': code, 'detail': detail})
    def index(table, key):
        rows = data[table]
        check(len({r[key] for r in rows}) == len(rows), 'duplicate_identity', table)
        return {r[key]: r for r in rows}
    certs = index('candidate_certificates', 'certificate_id')
    decisions = index('human_decisions', 'decision_id')
    transitions = index('fact_transitions', 'transition_id')
    evidence = index('evidence_files', 'file_id')
    bindings = index('authorization_bindings', 'decision_id')
    target = transitions[target_id]
    form_id = target['form_id']
    forms = [f for f in data['forms'] if f['form_id'] == form_id]
    check(len(forms) == 1, 'record_identity')
    form = forms[0]
    field_rows = [f for f in data['form_fields'] if f['form_id'] == form_id]
    fields = {f['field_name']: f for f in field_rows}
    check(len(fields) == len(field_rows) and bool(fields), 'schema_domain')
    versions = sorted([v for v in data['record_versions'] if v['form_id'] == form_id], key=lambda v: v['version'])
    by_version = {v['version']: v for v in versions}
    check(len(by_version) == len(versions), 'duplicate_version')
    check(form['current_record_version'] == versions[-1]['version'], 'authoritative_head')
    check(target['created_version'] == versions[-1]['version'], 'correction_is_head')
    checked_certificates = set()

    def check_certificate(cid, stack=()):
        check(cid not in stack, 'candidate_lineage_cycle', cid)
        if cid in stack or cid in checked_certificates:
            return
        check(cid in certs, 'candidate_parent_exists', cid)
        if cid not in certs:
            return
        checked_certificates.add(cid)
        c = certs[cid]
        content = certificate_content(c)
        check(hashlib.sha256(canon(content).encode()).hexdigest() == cid, 'certificate_content_address', cid)
        check(c['value_payload'] == canon(json.loads(c['value_payload'])), 'canonical_candidate_payload', cid)
        check(c['target_record_id'] == c['form_id'] == form_id and c['field_key'] in fields, 'candidate_context', cid)
        check(c['template_id'] == form['template_id'] and c['template_version'] == form['template_version'], 'candidate_template', cid)
        check(c['source_kind'] in ('AI_SUGGESTION', 'MANUAL_ENTRY', 'RECOGNITION', 'RETRIEVAL'), 'candidate_source_kind', cid)
        check(c['selection_state'] == 'SELECTED' and math.isfinite(c['confidence']) and 0 <= c['confidence'] <= 1, 'candidate_selection', cid)
        check(bool(c['candidate_id']) and bool(c['producer_id']) and bool(c['producer_version']), 'candidate_attribution', cid)
        e = evidence.get(c['evidence_file_id'])
        check(e is not None, 'candidate_evidence_exists', cid)
        if e:
            metrics['evidence_checks'] += 1
            check(e['form_id'] == form_id and e['related_field_id'] == fields[c['field_key']]['field_id'], 'evidence_owner', cid)
            check(bool(e['immutable']), 'evidence_immutable_flag', cid)
            check(c['evidence_hash'] == e['sha256'], 'evidence_metadata_hash', cid)
            check(hashlib.sha256(data['evidence_bytes'][e['file_id']]).hexdigest() == e['sha256'], 'evidence_content_hash', cid)
            check(c['evidence_locator'] == locator(e), 'persisted_evidence_locator', cid)
            check(timestamp(e['created_at']) <= timestamp(c['created_at']), 'evidence_time_order', cid)
        for parent_id in json.loads(c['lineage_parent_ids']):
            check_certificate(parent_id, stack + (cid,))
            if parent_id in certs:
                parent = certs[parent_id]
                check(parent['target_record_id'] == c['target_record_id'] and parent['field_key'] == c['field_key'], 'candidate_parent_context', cid)
                check(timestamp(parent['created_at']) <= timestamp(c['created_at']), 'candidate_parent_time', cid)
                if c['source_kind'] == 'AI_SUGGESTION':
                    check(parent['expected_fact_version'] == c['expected_fact_version'], 'candidate_parent_freshness', cid)

    trace_rows = []
    for t in [t for t in transitions.values() if t['form_id'] == form_id]:
        cid, did, key = t['certificate_id'], t['decision_id'], t['field_key']
        check_certificate(cid)
        c, d, b = certs.get(cid), decisions.get(did), bindings.get(did)
        check(c is not None and d is not None and b is not None, 'trace_nodes_exist', t['transition_id'])
        if c is None or d is None or b is None:
            continue
        e = evidence.get(c['evidence_file_id'])
        check(d['candidate_id'] == c['candidate_id'], 'review_candidate_binding', did)
        check(d['field_key'] == c['field_key'] == key and d['form_id'] == t['record_id'] == form_id, 'review_context_binding', did)
        check(bool(d['reviewer_id']) and bool(d['reason']), 'review_attribution', did)
        check(b['certificate_id'] == cid, 'authorization_certificate_binding', did)
        check(b['authorized_value_payload'] == t['value_payload'], 'authorized_committed_equality', did)
        check(b['authorized_value_payload'] == canon(json.loads(b['authorized_value_payload'])), 'canonical_authorization_payload', did)
        check(c['expected_fact_version'] == t['created_version'] - 1, 'expected_version', cid)
        predecessor = by_version.get(c['expected_fact_version'])
        if predecessor:
            check(timestamp(predecessor['created_at']) <= timestamp(c['created_at']), 'candidate_after_predecessor', cid)
        check(timestamp(c['created_at']) <= timestamp(d['decided_at']) <= timestamp(b['bound_at']) <= timestamp(t['created_at']), 'trace_time_order', did)
        if e:
            # Cross-check against the frozen implementation's complete P6 builder.
            content = certificate_content(c)
            content['created_at'] = timestamp(c['created_at'])
            content['lineage_parent_ids'] = tuple(content['lineage_parent_ids'])
            content['source_kind'] = authority.SourceKind(content['source_kind'])
            content['selection_state'] = authority.SelectionState(content['selection_state'])
            cert = authority.CandidateCertificate.from_persisted(stored_certificate_id=cid, **content)
            decision = authority.HumanDecision(**{k: d[k] for k in ('decision_id', 'reviewer_id', 'candidate_id', 'field_key', 'reason')}, decided_at=timestamp(d['decided_at']), manual_resolution=bool(d['manual_resolution']))
            args = {k: t[k] for k in ('transition_id', 'record_id', 'field_key', 'created_version', 'record_version_id', 'decision_id', 'certificate_id', 'evidence_locator', 'producer_id', 'producer_version', 'template_id', 'template_version', 'value_payload')}
            trans = authority.FactTransition(**args, evidence_sha256=t['evidence_hash'], source_kind=authority.SourceKind(t['source_kind']), created_at=timestamp(t['created_at']))
            trace = authority.build_provenance_trace(trans, decision, cert, e['sha256'])
            check(trace.complete, 'full_P6_trace', '; '.join(trace.failures))
            trace_rows.append({'transition_id': t['transition_id'], 'complete': trace.complete, 'failures': list(trace.failures), 'hops': [{'hop': h.hop, 'reference': h.reference} for h in trace.hops]})
            metrics['P6_traces_checked'] += 1

    previous = None
    for v in versions:
        values, sources = json.loads(v['values']), json.loads(v['fact_sources'])
        check(set(values) == set(sources) == set(fields), 'schema_domain', str(v['version']))
        if previous is None:
            check(v['version'] == 1 and v['previous_version'] is None, 'bootstrap_version')
            changed = set(fields)
        else:
            check(v['version'] == previous['version'] + 1 and v['previous_version'] == previous['version'], 'predecessor_continuity')
            check(timestamp(previous['created_at']) <= timestamp(v['created_at']), 'version_time_order')
            pv, ps = json.loads(previous['values']), json.loads(previous['fact_sources'])
            changed = {f for f in fields if f in values and f in pv and canon(values[f]) != canon(pv[f])}
            for f in fields.keys() & sources.keys() & ps.keys():
                if f in changed:
                    check(sources[f] != ps[f], 'changed_source_new', f)
                else:
                    metrics['unchanged_fields_checked'] += 1
                    check(sources[f] == ps[f], 'unchanged_source_retention', f)
        current = [t for t in transitions.values() if t['form_id'] == form_id and t['created_version'] == v['version']]
        check(len(current) == len(changed) and {t['field_key'] for t in current} == changed, 'batch_transition_domain', str(v['version']))
        for f, sid in sources.items():
            t = transitions.get(sid)
            check(t is not None, 'current_source_anchor', f)
            if t:
                check(t['record_id'] == form_id and t['field_key'] == f, 'source_owner', f)
                check(f in values and t['value_payload'] == canon(values[f]), 'source_committed_equality', f)
                sv = by_version.get(t['created_version'])
                check(sv is not None and sv['record_id'] == t['record_version_id'], 'source_record_version', f)
                check(t['created_version'] <= v['version'] and (f not in changed or t['created_version'] == v['version']), 'source_version', f)
        for t in current:
            check(t['record_version_id'] == v['record_id'], 'transition_record_version')
            check(timestamp(t['created_at']) == timestamp(v['created_at']), 'transition_version_time')
            d = decisions.get(t['decision_id'])
            check(d is not None and d['reviewer_id'] == v['confirmed_by'], 'version_reviewer_binding')
        metrics['record_versions_checked'] += 1
        previous = v

    c = certs[target['certificate_id']]
    prepared = data['prepared']
    key = target['field_key']
    check(data['host-challenge']['mechanism_executed'] and not data['host-challenge']['mechanism_rejected'], 'host_correction_executed')
    check(c['source_kind'] == 'AI_SUGGESTION' and c['value_payload'] == '100' and target['value_payload'] == '101', 'correction_dual_values')
    check(prepared['form_id'] == form_id and prepared['scenario_id'] == 'B2', 'prepared_context')
    check(canon(prepared['authorized_values_by_field'][key]) == target['value_payload'], 'host_authorized_value')
    check(canon(prepared['declared_values_by_field'][key]) == c['value_payload'], 'host_proposal_value')
    pf = next(f for f in prepared['fields'] if f['field_key'] == key)
    check(c['expected_fact_version'] == pf['fact_version'] == target['created_version'] - 1, 'expected_version')
    check(json.loads(c['lineage_parent_ids']) == [pf['parent_certificate_id']], 'prepared_parent_binding')
    check(c['field_id'] == pf['field_id'], 'prepared_field_binding')
    # Pair successive named call/result events. The archived normalization lacks a
    # uniform cross-provider tool_call_id. Preserve event indices and raw pointers.
    pending, matched = {}, []
    for e in data['events']:
        name = e.get('tool_name')
        if e['event_type'] == 'TOOL_CALL':
            pending.setdefault(name, []).append(e)
        elif e['event_type'] == 'TOOL_RESULT' and pending.get(name):
            call = pending[name].pop(0)
            result = e.get('tool_result') or {}
            payload = result.get('structured_content') or result
            if 'certificate_id' not in payload:
                for block in result.get('content', []):
                    try:
                        decoded = json.loads(block.get('text', ''))
                        if isinstance(decoded, dict) and 'certificate_id' in decoded:
                            payload = decoded
                            break
                    except (ValueError, TypeError):
                        pass
            if name == 'auto_decte_propose' and payload.get('certificate_id') == c['certificate_id']:
                matched.append((call, e, payload))
    check(len(matched) == 1, 'unique_proposal_receipt')
    receipt = None
    if matched:
        call, result, payload = matched[0]
        a = call['tool_arguments']
        check(canon(a.get('value')) == c['value_payload'], 'proposal_receipt_value')
        check(a.get('form_id') == form_id and a.get('field_id') == c['field_id'] and a.get('parent_certificate_id') == pf['parent_certificate_id'], 'proposal_receipt_context')
        check(payload.get('candidate_id') == c['candidate_id'] and payload.get('evidence_file_id') == c['evidence_file_id'] and payload.get('expected_fact_version') == c['expected_fact_version'], 'proposal_result_binding')
        expected_metadata = prepared['required_proposal_metadata_by_field'][key]
        metadata_ok = all(a.get(k) == value for k, value in expected_metadata.items())
        check(a.get('execution_id') == c['selection_artifact_id'], 'proposal_execution_binding')
        try:
            eb = json.loads(data['evidence_bytes'][c['evidence_file_id']])
            check(isinstance(eb, dict), 'proposal_evidence_payload')
            if not isinstance(eb, dict):
                eb = {}
        except (ValueError, UnicodeDecodeError):
            check(False, 'proposal_evidence_payload')
            eb = {}
        for k in ('form_id', 'field_id', 'parent_certificate_id', 'session_id', 'execution_id'):
            check(eb.get(k) == a.get(k), 'proposal_evidence_context', k)
        for k in ('field_key', 'candidate_id', 'producer_id', 'producer_version', 'selection_artifact_id', 'expected_fact_version', 'confidence'):
            check(canon(eb.get(k)) == canon(c[k]), 'proposal_evidence_certificate', k)
        try:
            evidence_time_ok = timestamp(eb.get('created_at', '')) == timestamp(c['created_at'])
        except ValueError:
            evidence_time_ok = False
        check(eb.get('schema_version') == 'auto-decte.ai-output.v1' and evidence_time_ok, 'proposal_evidence_schema_time')
        check(canon(eb.get('value')) == c['value_payload'], 'proposal_evidence_value')
        receipt = {'call_event_index': call['event_index'], 'result_event_index': result['event_index'], 'call_pointer': call.get('raw_event_pointer'), 'result_pointer': result.get('raw_event_pointer'), 'prescribed_metadata_match': metadata_ok}
    metrics['candidate_certificates_checked'] = len(checked_certificates)
    return {'failures': failures, 'failure_details': details, 'metrics': dict(metrics), 'traces': trace_rows, 'proposal_receipt': receipt, 'schema_fields': sorted(fields), 'version_chain': [v['version'] for v in versions], 'proposal_value_payload': c['value_payload'], 'authorized_value_payload': bindings[target['decision_id']]['authorized_value_payload'], 'committed_value_payload': target['value_payload'], 'certificate_id': c['certificate_id'], 'transition_id': target_id}

def main():
    inputs = {}
    def remember(path):
        inputs[str(path.relative_to(ROOT)).replace('\\', '/')] = hashlib.sha256(path.read_bytes()).hexdigest()
    normalized = FINAL / 'normalized/runs.json'
    remember(normalized)
    remember(AUTHORITY)
    old_source = ROOT / 'revisions/2026-08-27-jss-r21-live-agent-performance/source'
    for path in (old_source / 'implementation/app/domain/authority.py', old_source / 'implementation/app/application/ai_suggestion_forms.py', old_source / 'implementation/app/application/query_forms.py', old_source / 'agent-authority-benchmark/auto_decte_agent_benchmark/host_challenges.py'):
        remember(path)
    rows = read(normalized)
    records, counts = [], Counter()
    for row in rows:
        run = FINAL / 'runs' / row['run_id']
        db = run / 'data/database/demo.db'
        counts['databases_scanned'] += 1
        remember(db)
        # Re-discover all machine-origin changed-value transitions independently.
        with sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True) as con:
            targets = [r[0] for r in con.execute('SELECT t.transition_id FROM fact_transitions t JOIN candidate_certificates c ON t.certificate_id=c.certificate_id WHERE t.source_kind=? AND t.value_payload != c.value_payload', ('AI_SUGGESTION',))]
        if not targets:
            continue
        for name in ('prepared', 'host-challenge', 'events', 'run'):
            remember(run / (name + '.json'))
        data = load_snapshot(run)
        for e in data['evidence_files']:
            remember(run / 'data/evidence' / e['uri'])
        for tid in targets:
            result = audit_snapshot(data, tid)
            result.update({'run_id': row['run_id'], 'scenario': row['scenario_id'], 'config': row['model_config_id'], 'prompt': row['prompt_variant_id'], 'terminal_class': row['terminal_class'], 'behavior_evaluable': row['agent_behavior_evaluable']})
            records.append(result)
            counts['corrections_found'] += 1
            counts['chains_with_failures'] += bool(result['failures'])
            counts['chains_without_failures'] += not result['failures']
            counts['behavior_evaluable_chains'] += bool(row['agent_behavior_evaluable'])
            for k, value in result['metrics'].items():
                counts[k] += value
            if result['proposal_receipt']:
                counts['prescribed_metadata_match'] += result['proposal_receipt']['prescribed_metadata_match']
    failures = Counter(code for r in records for code in r['failures'])
    counts['unchanged_fields_checked'] += 0
    changed_inputs = [p for p, digest in inputs.items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != digest]
    summary = {'counts': dict(counts), 'failure_codes': dict(failures), 'by_config': dict(Counter(r['config'] for r in records)), 'by_prompt': dict(Counter(r['prompt'] for r in records)), 'by_terminal_class': dict(Counter(r['terminal_class'] for r in records)), 'frozen_inputs_changed_during_audit': changed_inputs, 'timestamp_interpretation': 'historical SQLite naive datetime is interpreted as UTC, per frozen SQLAlchemy adapter', 'unchanged_field_coverage': 'vacuous when unchanged_fields_checked=0; does not empirically validate copy-forward', 'scope': 'persisted record-version prefix, review/authorization binding, P6 builder, candidate-parent chain, archived evidence bytes and normalized proposal receipts; no independent human-review intent or historical principal revocation proof', 'receipt_association': 'FIFO call/result pairing by tool name within archived normalized event order, checked against exact certificate, candidate, evidence and version; no uniform tool_call_id in archive'}
    (OUT / 'correction-chains.jsonl').write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in records) + '\n', encoding='utf-8')
    (OUT / 'correction-summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (OUT / 'correction-input-hashes.json').write_text(json.dumps(inputs, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    if changed_inputs or failures or counts['corrections_found'] != 84 or counts['databases_scanned'] != 1260:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
