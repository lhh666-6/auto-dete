"""Read-only manuscript aggregation of the complete frozen formal ledger."""
from pathlib import Path
from collections import Counter
import json,csv,statistics,hashlib

ROOT=Path(__file__).resolve().parent
PACKAGE=ROOT.parents[1]/'research/agent-policy-phase2-formal-2026-10-07'
OUT=ROOT/'evidence/online'
def read(name):
    with (OUT/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
status=json.loads((PACKAGE/'formal-results/collection-status.json').read_text(encoding='utf-8-sig'))
assert status['status']=='COMPLETE' and len(status['pairs'])==256
friction_rows=read('table4-utility-friction.csv');failure_rows=read('failure-archaeology-all-arms.csv')
friction_lookup={(r['pair_id'],r['policy']):r for r in friction_rows}
failure_lookup={(r['pair_id'],r['policy']):r for r in failure_rows}
arms=[];prefix_errors=Counter();prefix_check=Counter();pair_mismatches=[]
for pid,p in status['pairs'].items():
    assert p['status']=='terminal'
    a=p['assignment']; r=p.get('result',{})
    prefix_file=PACKAGE/'formal-results'/pid/'prefix/events.jsonl'
    prefix_events=[json.loads(x) for x in prefix_file.read_text(encoding='utf-8').splitlines()] if prefix_file.exists() else []
    prefix_check[a['config_id']]+=any(e['event_type']=='checkpoint' and e['payload'].get('reached') for e in prefix_events)
    if r.get('prefix',{}).get('error'):prefix_errors[(a['config_id'],r['prefix']['error'])]+=1
    hashes=r.get('checkpoint_hashes',{})
    if hashes and hashes.get('bound')!=hashes.get('context'):pair_mismatches.append(pid)
    for policy in ('context','bound'):
        s=dict(r.get(policy,{}))
        # Recomputed exporter evidence supersedes a coordinator's cached score.
        f=friction_lookup[pid,policy]; bad=failure_lookup.get((pid,policy))
        s['task_completion']=f['task_completion']=='True';s['terminal']=f['terminal']
        s['I']=int(bad['I']) if bad and bad['I'] in ('0','1') else ('unknown' if bad else 1)
        if s['I']=='unknown':s['continuity_failure_incidence']=None
        arms.append(dict(pair_id=pid,scenario=a['scenario'],config=a['config_id'],policy=policy,**s))
assert len(arms)==512 and not pair_mismatches
episodes=read('table3-recovery.csv');friction=read('paired-effects.csv');failures=read('failure-archaeology-all-arms.csv')
transitions=read('table2-continuity.csv')
data={'collection_status':status['status'],'updated_utc':status['updated_utc'],'planned_arms':len(arms),
      'checkpoint_pairs':dict(prefix_check),'prefix_errors':{str(k):v for k,v in prefix_errors.items()},
      'checkpoint_hash_mismatches':pair_mismatches,'groups':{},'episodes':{},'friction':{},
      'failure_arms':len(failures),'failure_labels':dict(Counter(x for r in failures for x in json.loads(r['failure_labels']))),
      'transition_count':len(transitions),'substitutions':dict(Counter((r['config_id']+'-'+r['policy']+'-'+r['scenario']) for r in transitions if r['executed_substitution']=='True'))}
for config in ('A','B'):
    for policy in ('context','bound'):
        rows=[r for r in arms if r['config']==config and r['policy']==policy]
        def ui(r):return str(int(bool(r.get('task_completion'))))+','+str(r.get('I','unknown'))
        data['groups'][config+'-'+policy]={'arms':len(rows),'joint':dict(Counter(ui(r) for r in rows)),
            'terminal':dict(Counter(r.get('terminal','not_started') for r in rows)),
            'U':sum(bool(r.get('task_completion')) for r in rows),
            'continuity_failure':sum(r.get('continuity_failure_incidence')==1 for r in rows)}
for scenario in 'LNGEVR':
    for config in ('A','B'):
        for policy in ('context','bound'):
            rows=[r for r in episodes if r['scenario']==scenario and r['config_id']==config and r['policy']==policy]
            if not rows:continue
            data['episodes'][scenario+'-'+config+'-'+policy]={'n':len(rows),'arms':len(set(r['pair_id'] for r in rows)),
                'first_actions':dict(Counter(r['first_meaningful_action'] for r in rows)),
                'strategy':dict(Counter(r['recovery_strategy'] for r in rows)),
                'labels':dict(Counter(x for r in rows for x in json.loads(r['labels']))),
                'recovered':sum(r['recovered']=='True' for r in rows),'U':sum(r['U']=='True' for r in rows),
                'RecoverableReject':sum(r['RecoverableReject']=='True' for r in rows)}
for scenario in ['all','G','N','E','V','R','L']:
    for config in ('A','B'):
        rows=[r for r in friction if r['config_id']==config and (scenario=='all' or r['scenario']==scenario)]
        metrics={}
        for m in ['suffix_agent_tool_calls','suffix_model_turns','suffix_authorization_requests','suffix_elapsed_ms','budget_capped_time_to_success_ms']:
            vals=[float(r['delta_'+m]) for r in rows if r['delta_'+m]!='']
            metrics[m]={'n':len(vals),'mean':statistics.mean(vals) if vals else None,'median':statistics.median(vals) if vals else None}
        data['friction'][scenario+'-'+config]=metrics
data['input_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.csv')}
data['input_hashes']['collection-status.json']=hashlib.sha256((PACKAGE/'formal-results/collection-status.json').read_bytes()).hexdigest()
data['raw_provider_error_counts']={}
for config in ('A','B'):
    count=Counter()
    for pid,p in status['pairs'].items():
        if p['assignment']['config_id']!=config:continue
        for file in (PACKAGE/'formal-results'/pid).glob('*/provider-raw/**/stdout.jsonl'):
            for line in file.read_text(encoding='utf-8').splitlines():
                try:event=json.loads(line)
                except json.JSONDecodeError:continue
                if event.get('type')=='error':
                    msg=event.get('message','').lower()
                    count['usage_limit' if 'usage limit' in msg else 'other_provider_error']+=1
    data['raw_provider_error_counts'][config]=dict(count)
(OUT/'manuscript-aggregates.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(data,indent=2,ensure_ascii=False))
