from __future__ import annotations
import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from common import ROOT, REPO, canonical, db_digest, digest, environment, sha, write_json
from reference import Reference, packet
from journal import Journal

CASES = ('accept', 'correction', 'multi_field', 'same_value_substitution',
         'different_evidence_substitution', 'stale', 'replay', 'wrong_authorized_value',
         'rollback_after_cas', 'rollback_before_transition', 'rollback_before_commit')
ARMS = ('journal_context', 'journal_exact', 'reference')


def collect_inputs(output):
    archive = REPO / 'r21-jss/evidence/agent-authority-benchmark-v2/final/2026-09-01-three-config-10x'
    index = json.loads((archive/'normalized/runs.json').read_text(encoding='utf-8'))
    selection = []
    inputs = []
    for model in ('G1','G2','D1'):
        for scenario in ('B1','B2','B3','B4'):
            pool = sorted((r for r in index if r['model_config_id']==model and r['scenario_id']==scenario),key=lambda r:r['run_id'])
            chosen = None
            inspected = []
            for row in pool:
                path = archive/'runs'/row['run_id']/'events.json'
                events = json.loads(path.read_text(encoding='utf-8'))
                calls = [e for e in events if e.get('event_type')=='TOOL_CALL' and e.get('tool_name')=='auto_decte_propose'
                         and 'value' in e.get('tool_arguments',{})]
                inspected.append({'run_id':row['run_id'],'has_proposal':bool(calls)})
                if calls:
                    call = calls[0]
                    chosen = {'id':model+'-'+scenario, 'model_config':model, 'scenario':scenario,
                        'run_id':row['run_id'], 'requested_model':row['requested_model'],
                        'events_file':str(path.relative_to(REPO)), 'events_sha256':sha(path),
                        'event_index':call['event_index'], 'tool_arguments':call['tool_arguments'],
                        'value':call['tool_arguments']['value'],
                        'mapping':'first recorded propose value mapped to quantity; batch/operator and all reviews/faults constructed'}
                    break
            selection.append({'model':model,'scenario':scenario,'eligible_pool':len(pool),'inspected':inspected,'selected':chosen['run_id'] if chosen else None})
            if chosen:
                inputs.append(chosen)
    # Version-sensitive types supplement the archival inputs, explicitly synthetic.
    for name, before, after in [('int_float',2,2.0),('int_bool',1,True),('nested',{'k':1},{'k':1.0})]:
        inputs.append({'id':'synthetic-'+name,'value':after,'initial_quantity':before,
                       'origin':'synthetic canonical-JSON boundary control'})
    write_json(output/'inputs.json',inputs)
    write_json(output/'selection.json', {'rule':'lexicographically first run with a recorded proposal per model/scenario; no success-label filtering',
        'population_inference':False,'source_index_sha256':sha(archive/'normalized/runs.json'),'cells':selection})
    return inputs


def create_case(sample, name):
    now = datetime.now(timezone.utc)
    initial = {'quantity':sample.get('initial_quantity',90), 'batch':'B-INITIAL','operator':'OP-INITIAL'}
    x = sample['value']
    if canonical(x)==canonical(initial['quantity']):
        initial['quantity'] = {'prestate': 'different-from-candidate'}
    authorized = x
    if name in ('correction','same_value_substitution','different_evidence_substitution'):
        authorized = x+1 if isinstance(x,(int,float)) and not isinstance(x,bool) else {'corrected':x}
    final = initial | {'quantity':authorized}
    if name in ('multi_field','rollback_before_transition'):
        final['batch'] = 'B-UPDATED'
    seed = {f:packet(f,v,0,'seed-'+f,now=now,evidence='constructed initial state '+f) for f,v in initial.items()}
    reviewed = {f:packet(f, x if f=='quantity' else v,1,'reviewed-'+f,now=now,
        evidence='archived value '+canonical(x) if f=='quantity' else 'constructed batch update')
        for f,v in final.items() if canonical(v)!=canonical(initial[f])}
    original = reviewed['quantity']
    alternative = packet('quantity',original['proposed'],1,'alternative-quantity',now=now,
        evidence='different evidence' if name=='different_evidence_substitution' else 'archived value '+canonical(x))
    all_packets = list(seed.values())+list(reviewed.values())+[alternative]
    return initial,final,seed,reviewed,alternative,all_packets


def expected_query(initial, final, seed, reviewed, target_version=2):
    out={}
    for f,value in final.items():
        p = reviewed[f] if f in reviewed else seed[f]
        out[f]={'proposal':p['proposed'],'authorized':value,'reviewer':'reviewer',
            'reviewed_candidates':[p['id']], 'committed':value,
            'source_version':target_version if f in reviewed else 1}
    return out


def score_queries(actual, expected):
    rows=[]
    for f, answers in expected.items():
        for name,value in answers.items():
            got=actual.get(f,{}).get(name)
            if got is None:
                status='unavailable'
            elif name=='reviewed_candidates' and len(got)>1:
                status='ambiguous' if value[0] in got else 'wrong'
            else:
                status='correct' if canonical(got)==canonical(value) else 'wrong'
            rows.append({'field':f,'query':name,'expected':value,'actual':got,'status':status})
    return rows


def run(output, limit=None):
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    inputs=collect_inputs(output)
    if limit:
        inputs=inputs[:limit]
    receipts=[]
    for sample in inputs:
        for case in CASES:
            initial,final,seed,reviewed,alternative,packets=create_case(sample,case)
            ids={f:p['id'] for f,p in reviewed.items()}
            used=dict(ids)
            if case in ('same_value_substitution','different_evidence_substitution'):
                used['quantity']=alternative['id']
            for arm in ARMS:
                path=output/'databases'/sample['id']/case/(arm+'.db')
                system=Reference(path,initial) if arm=='reference' else Journal(path,initial,arm=='journal_exact')
                row={'sample':sample['id'],'case':case,'arm':arm,'database':str(path.relative_to(output)),
                    'expected_instance_accept':case in ('accept','correction','multi_field'),
                    'expected_value_accept':case in ('accept','correction','multi_field','same_value_substitution'),
                    'reviewed':ids,'used':used}
                try:
                    for p in packets:
                        system.add(p)
                    system.confirm(0,initial,{f:p['id'] for f,p in seed.items()})
                    approval=system.prepare(1,final,ids)
                    expected=expected_query(initial,final,seed,reviewed)
                    if case=='stale':
                        other=packet('operator','OP-CONCURRENT',1,'concurrent-operator',evidence='constructed concurrent update')
                        system.add(other)
                        system.confirm(1,initial|{'operator':'OP-CONCURRENT'},{'operator':other['id']})
                    if case=='replay':
                        system.admit(approval,ids)
                    before=db_digest(path)
                    try:
                        value_attack={'quantity':{'unauthorized':1}} if case=='wrong_authorized_value' else None
                        failpoint=case.removeprefix('rollback_') if case.startswith('rollback_') else None
                        system.admit(approval,used,values=value_attack,failpoint=failpoint)
                        row['accepted']=True
                        row['error']=None
                    except Exception as exc:
                        row['accepted']=False
                        row['error']=type(exc).__name__+': '+str(exc)
                    row['before_digest']=before
                    row['after_digest']=db_digest(path)
                    row['zero_write_on_reject']=not row['accepted'] and before==row['after_digest']
                    row['queries']=score_queries(system.query(),expected) if row['accepted'] else []
                    row['instance_policy_violation']=row['accepted'] and not row['expected_instance_accept']
                    row['value_policy_violation']=row['accepted'] and not row['expected_value_accept']
                    row['instance_false_rejection']=not row['accepted'] and row['expected_instance_accept']
                    row['value_false_rejection']=not row['accepted'] and row['expected_value_accept']
                    row['harness_error']=None
                except Exception as exc:
                    row['harness_error']=type(exc).__name__+': '+str(exc)
                finally:
                    system.close()
                receipts.append(row)
                with (output/'receipts.jsonl').open('a',encoding='utf-8') as stream:
                    stream.write(json.dumps(row,ensure_ascii=False)+'\n')
        print('E1 sample complete:',sample['id'],flush=True)
    summaries=[]
    for arm in ARMS:
        rs=[r for r in receipts if r['arm']==arm]
        scored=[r for r in rs if not r['harness_error']]
        queries=[q for r in scored for q in r['queries']]
        summaries.append({'arm':arm,'planned':len(rs),'scored':len(scored),'harness_errors':len(rs)-len(scored),
            'accepted':sum(r['accepted'] for r in scored),
            'instance_policy_violations':sum(r['instance_policy_violation'] for r in scored),
            'value_policy_violations':sum(r['value_policy_violation'] for r in scored),
            'instance_false_rejections':sum(r['instance_false_rejection'] for r in scored),
            'value_false_rejections':sum(r['value_false_rejection'] for r in scored),
            'rejections_with_writes':sum(not r['accepted'] and not r['zero_write_on_reject'] for r in scored),
            'query_counts':dict(Counter(q['status'] for q in queries))})
    comparisons=[]
    for sample in inputs:
        for case in CASES:
            rs={r['arm']:r for r in receipts if r['sample']==sample['id'] and r['case']==case}
            a,b=rs['journal_exact'],rs['reference']
            comparisons.append({'sample':sample['id'],'case':case,
                'acceptance_equal':a.get('accepted')==b.get('accepted') and not a['harness_error'] and not b['harness_error'],
                'query_answers_equal':a.get('queries')==b.get('queries')})
    result={'environment':environment(),'sample_count':len(inputs),'scenario_count':len(CASES),
            'arms':summaries,'exact_baseline_reference_comparisons':comparisons,
            'inference':'Constructed finite cases on archived inputs; no general failure-rate or provider inference.'}
    write_json(output/'summary.json',result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--limit',type=int)
    a=p.parse_args();print(json.dumps(run(a.output,a.limit)['arms'],indent=2))
