"""Independent supplementary A-only extraction; frozen scorer, immutable inputs.

Table extraction is adapted from the frozen phase2/export.py; its hard-coded
A+B/128-task analysis entry points are deliberately not called.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT.parent / 'agent-policy-phase2-formal-2026-10-07'
RECOVERY = ROOT.parent / 'agent-policy-phase2-quota-recovery-2026-10-07'
sys.path.insert(0, str(ORIGINAL))
sys.path.insert(0, str(ORIGINAL / 'src'))
from run_formal import verify_freeze
from phase2.export import read_events, usage_totals, csv_write, trivalent_and
from phase2.kernel import digest
from phase2.oracle import encode, transition_outcomes
from phase2.runner import score_run, validate_run, PROTOCOL_HASH, MANIFEST


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, obj): path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
def file_hashes(root):
    return {p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and p.suffix.lower() not in ('.lock','.pyc') and '__pycache__' not in p.parts}


def select_attempts(manifest, status):
    pairs=manifest['pairs']; ids=[p['pair_id'] for p in pairs]
    if len(ids)!=len(set(ids)): raise ValueError('DUPLICATE_MANIFEST_PAIR')
    if len({p['case_id'] for p in pairs})!=len(pairs): raise ValueError('DUPLICATE_TASK')
    if set(ids)!=set(status['pairs']): raise ValueError('PAIR_SET_MISMATCH')
    if status['freeze_id']!=manifest['freeze_id']: raise ValueError('FREEZE_ID_MISMATCH')
    if status['status']!='COMPLETE': raise ValueError('NONTERMINAL_BATCH')
    if len(pairs)!=manifest['planned_pairs'] or len(pairs)*2!=manifest['planned_arms']: raise ValueError('PLANNED_COUNT_MISMATCH')
    selected=[]; directories=set()
    for pair in pairs:
        record=status['pairs'][pair['pair_id']]
        if record['status']!='terminal': raise ValueError('NONTERMINAL_PAIR')
        if record['assignment']!=pair: raise ValueError('ASSIGNMENT_DRIFT')
        if pair['config_id']!='A' or sorted(pair['order'])!=['bound','context']: raise ValueError('ASSIGNMENT_POLICY_OR_CONFIG')
        attempts=record['attempts']
        if not attempts: raise ValueError('MISSING_ATTEMPTS')
        for index, attempt in enumerate(attempts,1):
            if attempt['directory'] in directories: raise ValueError('DUPLICATE_ATTEMPT')
            directories.add(attempt['directory'])
            if attempt['directory']!=f"{pair['pair_id']}/attempt-{index:03d}": raise ValueError('ATTEMPT_DIRECTORY_DRIFT')
            if not attempt.get('finished_utc') or not attempt.get('result'): raise ValueError('UNFINISHED_ATTEMPT')
        selected.append({'assignment':pair,'attempt':attempts[-1],'attempts':attempts})
    if status.get('terminal_pairs',len(pairs))!=len(pairs): raise ValueError('TERMINAL_COUNT_MISMATCH')
    return selected


def check_identity(events, expected, label):
    if not events: raise ValueError('MISSING_EVENTS:'+label)
    for e in events:
        for field,value in expected.items():
            if e.get(field)!=value: raise ValueError('EVENT_IDENTITY_DRIFT:'+label+':'+field)


def include_failure(score): return not score['task_completion'] or score['I'] in (0,'unknown')


def terminal_error_code(payload):
    return (payload.get('runtime_error') or {}).get('code',payload.get('error_code',payload.get('error','unspecified')))


def check_attempt_inventory(expected, observed):
    if set(expected)!=set(observed): raise ValueError('ATTEMPT_INVENTORY_MISMATCH')


def paired_summary(rows, field, iterations=10000, seed=20261007, unknown=None):
    lookup={}; strata=defaultdict(list)
    for r in rows:
        key=(r['task_instance_id'],r['policy'])
        if key in lookup: raise ValueError('DUPLICATE_ARM')
        lookup[key]=r
    tasks=sorted({t for t,p in lookup}); values={}
    for task in tasks:
        if any((task,p) not in lookup for p in ['context','bound']): raise ValueError('MISSING_ARM')
        a,b=[lookup[task,p] for p in ['context','bound']]
        if a['scenario']!=b['scenario']: raise ValueError('PAIR_SCENARIO_DRIFT')
        strata[a['scenario']].append(task); av,bv=a[field],b[field]
        if av is None or bv is None:
            if unknown=='lower': av=1 if av is None else av; bv=0 if bv is None else bv
            elif unknown=='upper': av=0 if av is None else av; bv=1 if bv is None else bv
            else: values[task]=None; continue
        values[task]=float(bv)-float(av)
    base={'paired_units':len(tasks),'direction':'bound_minus_context','unknown_pairs':sum(v is None for v in values.values())}
    if any(v is None for v in values.values()): return {**base,'estimate':None,'interval':None}
    rng=random.Random(seed); blocks=[strata[s] for s in sorted(strata)]; n=len(tasks)
    draws=sorted(sum(values[rng.choice(block)] for block in blocks for _ in block)/n for _ in range(iterations))
    return {**base,'estimate':sum(values.values())/n,'interval':[draws[int(.025*(iterations-1))],draws[int(.975*(iterations-1))]],
            'median_paired_difference':statistics.median(values.values()),'bootstrap_iterations':iterations,'bootstrap_seed':seed}


def verify_sources():
    master=verify_freeze(ORIGINAL); path=RECOVERY/'recovery-manifest.json'; m=read(path)
    if sha(path)!=(RECOVERY/'recovery-manifest.sha256').read_text().strip(): raise ValueError('RECOVERY_MANIFEST_HASH_MISMATCH')
    if master!=m['parent_freeze_master']: raise ValueError('PARENT_FREEZE_DRIFT')
    payload={k:v for k,v in m.items() if k!='freeze_id'}
    if m['freeze_id']!='phase2-quota-recovery-v1-'+digest(payload)[:12]: raise ValueError('RECOVERY_FREEZE_DIGEST_MISMATCH')
    if sha(RECOVERY/'run_recovery.py')!=m['source_script_sha256'] or sha(RECOVERY/'test_recovery.py')!=m['test_script_sha256']: raise ValueError('RECOVERY_SOURCE_DRIFT')
    if file_hashes(ORIGINAL/'formal-results')!=m['original_result_file_hashes']: raise ValueError('ORIGINAL_RESULT_DRIFT')
    original_pairs={p['pair_id']:p for p in read(ORIGINAL/'frozen-formal/assignment-manifest.json')['pairs']}
    original_tasks={t['task_instance_id']:t for t in read(ORIGINAL/'frozen-formal/formal-task-manifest.json')['tasks']}
    original_config=next(c for c in read(ORIGINAL/'frozen-formal/agent-config-manifest.json')['configs'] if c['id']=='A')
    if m['agent_config']!=original_config: raise ValueError('CONFIG_DRIFT')
    for pair in m['pairs']:
        if original_pairs.get(pair['pair_id'])!=pair: raise ValueError('FROZEN_ASSIGNMENT_DRIFT')
        if original_tasks.get(pair['case_id'])!=m['tasks'][pair['case_id']]: raise ValueError('FROZEN_TASK_DRIFT')
    original_status=read(ORIGINAL/'formal-results/collection-status.json'); eligible=[]
    for name,rec in original_status['pairs'].items():
        if rec['status']!='terminal' or rec['assignment']['config_id']!='A' or rec['result']['checkpoint_reached'] is not False: continue
        d=ORIGINAL/'formal-results'/name/'prefix'; events=read_events(d)
        if any(e['event_type']=='model_response' for e in events): continue
        quota=False
        for f in d.rglob('stdout.jsonl'):
            for line in f.read_text(encoding='utf-8').splitlines():
                e=json.loads(line); msg=str(e.get('message','')).lower()
                if e.get('type')=='error' and any(t in msg for t in ('usage limit','usage_limit','quota exhausted')): quota=True
        if quota: eligible.append(name)
    if set(eligible)!={p['pair_id'] for p in m['pairs']}: raise ValueError('ELIGIBILITY_SET_DRIFT')
    return m,{'parent_freeze_master_sha256':master,'recovery_manifest_sha256':sha(path),'eligibility_reproduced_pairs':len(eligible),
              'original_result_files_unchanged':len(m['original_result_file_hashes']),'original_planned_arms':512,
              'frozen_scorer_sha256':sha(ORIGINAL/'src/phase2/runner.py'),'event_schema_sha256':sha(ORIGINAL/'frozen-design/trajectory-event.schema.json')}


def extract(manifest, selected, destination):
    rows=[]; transitions=[]; episodes=[]; failures=[]; attempts_out=[]; scores=[]; audit_rows=[]; prefixes=[]
    model_metadata=Counter(); runtime_errors=Counter(); event_count=0; cached_comparisons=0
    for index,selected_pair in enumerate(selected,1):
        pair=selected_pair['assignment']
        for attempt in selected_pair['attempts']:
            directory=RECOVERY/'results'/attempt['directory']; selected_flag=attempt is selected_pair['attempt']
            if not directory.is_dir(): raise ValueError('MISSING_ATTEMPT_DIRECTORY')
            result=read(directory/'pair-result.json')
            if result!=attempt['result']: raise ValueError('PAIR_RESULT_CACHE_MISMATCH:'+attempt['directory'])
            prefix=read_events(directory/'prefix'); reached=any(e['event_type']=='checkpoint' and e['payload']['reached'] for e in prefix)
            if reached!=result['checkpoint_reached']: raise ValueError('CHECKPOINT_CACHE_MISMATCH')
            if not selected_flag and (any(e['event_type']=='model_response' for e in prefix) or result.get('prefix',{}).get('error')!='ACCOUNT_QUOTA_EXHAUSTED'):
                raise ValueError('RETRIED_BEHAVIORAL_ATTEMPT')
            expected={'freeze_id':manifest['freeze_id'],'task_instance_id':pair['case_id'],'pair_id':pair['pair_id'],
                      'scenario':pair['scenario'],'agent_config_id':'A','schema_version':'phase2.event.v2',
                      'protocol_sha256':PROTOCOL_HASH,'protocol_version':MANIFEST['protocol_version'],
                      'agent_config_sha256':digest({**manifest['agent_config'],'freeze_id':manifest['freeze_id']})}
            prefix_audit=validate_run(directory/'prefix',check_prefix=False)
            check_identity(prefix,{**expected,'policy':'pre_policy','phase':'shared_prefix','run_id':pair['pair_id']+'-pre_policy'},attempt['directory']+'/prefix')
            audit_rows.append({'directory':attempt['directory']+'/prefix','selected':selected_flag,'errors':prefix_audit['errors'],'violations':prefix_audit['violations']})
            prefix_elapsed=prefix[-1]['elapsed_ms']; prefix_usage=usage_totals(prefix)
            prefixes.append({'pair_id':pair['pair_id'],'attempt_directory':attempt['directory'],'selected':selected_flag,'checkpoint_reached':reached,
                'model_responses':sum(e['event_type']=='model_response' for e in prefix),'usage':prefix_usage,'elapsed_ms':prefix_elapsed,'charged_once':True,'provider_cost_currency':None})
            attempt_summary={'pair_id':pair['pair_id'],'directory':attempt['directory'],'selected':selected_flag,'started_utc':attempt['started_utc'],
                'finished_utc':attempt['finished_utc'],'checkpoint_reached':reached,'prefix_responses':sum(e['event_type']=='model_response' for e in prefix),
                'prefix':result.get('prefix'),'deployment_changed':result.get('deployment_changed',False)}
            attempts_out.append(attempt_summary)
            all_events=[('prefix',prefix)]
            for policy in pair['order']:
                arm=directory/policy
                if not arm.is_dir(): raise ValueError('MISSING_ARM_DIRECTORY:'+str(arm))
                events=read_events(arm); all_events.append((policy,events))
                check_identity(events,{**expected,'policy':policy,'phase':'arm','run_id':pair['pair_id']+'-'+policy},attempt['directory']+'/'+policy)
                for e in events+prefix:
                    if e['event_type']=='initialization':
                        st=read((arm if e in events else directory/'prefix')/e['payload']['state_ref']['relative_path'])
                        if st['case']!=manifest['tasks'][pair['case_id']]: raise ValueError('RAW_TASK_IDENTITY_DRIFT')
                audit=validate_run(arm); score=score_run(arm)
                if score!=read(arm/'score.json') or score!=result[policy]: raise ValueError('INDEPENDENT_SCORE_MISMATCH:'+attempt['directory']+'/'+policy)
                cached_comparisons+=2
                audit_rows.append({'directory':attempt['directory']+'/'+policy,'selected':selected_flag,'errors':audit['errors'],'violations':audit['violations']})
                identity={'task_instance_id':pair['case_id'],'scenario':pair['scenario'],'config_id':'A','policy':policy,'pair_id':pair['pair_id']}
                scores.append({**identity,'attempt_directory':attempt['directory'],'selected':selected_flag,'score':score})
                if not selected_flag: continue
                calls=[e for e in events if e['event_type']=='tool_call' and e['origin']=='agent']; responses=[e for e in events if e['event_type']=='model_response']
                decisions=[e for e in events if e['event_type']=='admission_decision']; runtime=score['terminal'] in ('runtime_error','prefix_failure','audit_state_missing')
                term=next((e['payload'] for e in reversed(events) if e['event_type']=='termination'),{})
                row={**identity,'planned':1,'checkpoint_reached':reached,'event_exposure':sum(bool(e['event_type']=='workflow_event' and (e['payload'].get('kind') or e['origin']=='harness_handoff')) for e in events),
                    'rejection':sum(e['payload']['decision']=='rejected' for e in decisions),'task_completion':score['task_completion'],'state_goal':score['state_goal'],
                    'I':score['I'],'continuity_failure_incidence':score.get('continuity_failure_incidence'),'runtime_failure':runtime,'terminal':score['terminal'],
                    'suffix_agent_tool_calls':len(calls),'suffix_model_turns':len(responses),'suffix_authorization_requests':sum(e['payload']['tool_name']=='request_authorization' for e in calls),
                    'suffix_elapsed_ms':events[-1]['elapsed_ms'],'logical_elapsed_ms':prefix_elapsed+events[-1]['elapsed_ms'],
                    'budget_capped_time_to_success_ms':min(720000,events[-1]['elapsed_ms']) if score['task_completion'] else 720000,
                    'suffix_usage':usage_totals(events),'prefix_usage':prefix_usage,'audit_errors':score.get('audit_errors',[]),'termination_payload':term,
                    'attempt_directory':attempt['directory'],'recovery_path':score.get('recovery_path'),'delivered_recoverable':score.get('delivered_recoverable',0),
                    'G_standardized_recovery_success':score.get('G_standardized_recovery_success',False)}
                rows.append(row)
                if runtime: runtime_errors[str(terminal_error_code(term))]+=1
                for episode in score.get('episodes',[]): episodes.append({**identity,**episode})
                for e in decisions:
                    p=e['payload']
                    if p['decision']!='accepted' or p.get('idempotent_receipt'): continue
                    state=read(arm/p['post_state_ref']['relative_path']); t=next(t for t in state['transitions'] if t['commit_request_id']==p['commit_request_id'])
                    c,g=t['candidate'],t['grant']; checks=transition_outcomes(state,t); guard=trivalent_and(v for k,v in checks.items() if k!='A_instance')
                    same_context=encode(c['context'])==encode(g['context']); same_instance=c['candidate_id']==g['reviewed_candidate_id']
                    transitions.append({**identity,'transition_id':t['transition_id'],'origin':p['caller_origin'],
                        'same_value':c['context']['proposal_value_payload']==g['context']['proposal_value_payload'],'same_context':same_context,'same_instance':same_instance,
                        'policy_admissible':trivalent_and([guard,same_context,policy=='context' or same_instance]),
                        'A_instance_compatible':trivalent_and([guard,same_context,same_instance]),'executed_substitution':not same_instance,
                        'source_provenance_integrity':checks['source_provenance'],'copy_forward':checks['copy_forward']})
                if include_failure(score):
                    labels=list(score.get('failure_labels',[]))
                    if score['I']==0 and policy=='context' and score['task_completion']: labels.append('context_A_instance_incompatible_success')
                    if not score['task_completion'] and score['state_goal'] and not score.get('preview_delivered',True): labels.append('business_preview_missing')
                    if score['I']=='unknown': labels.append('integrity_unclassifiable')
                    if runtime: labels.append('provider_or_runtime_failure')
                    stage='shared_prefix' if not reached else ('audit_coverage' if score.get('audit_errors') else ('final_report_or_suffix' if not score.get('accurate_report',False) else 'task_deliverable_or_integrity'))
                    failures.append({**row,'failure_labels':list(dict.fromkeys(labels)),'failure_stage':stage,'violations':score.get('violations',[]),
                        'missing':score.get('missing',[]),'episodes':score.get('episodes',[]),'bound_rejection_friction_observed':policy=='bound' and bool(score.get('episodes')) and not score['task_completion']})
            for label,events in all_events:
                event_count+=len(events)
                for e in events:
                    if e['event_type']=='model_response':
                        p=e['payload']; model_metadata[json.dumps({k:p.get(k) for k in ('requested_model','returned_model','returned_revision')},sort_keys=True)]+=1
            if index%20==0: print(f'Independently rescored {index}/{len(selected)} pairs',flush=True)
    write(destination/'scored-arms.json',scores); write(destination/'arm-rows.json',rows); write(destination/'attempt-ledger.json',attempts_out)
    write(destination/'validation-ledger.json',audit_rows); write(destination/'prefix-accounting.json',prefixes)
    return rows,transitions,episodes,failures,{'events_checked':event_count,'cached_score_exact_comparisons':cached_comparisons,
        'validation_errors':sum(len(a['errors']) for a in audit_rows),'validation_violations':sum(len(a['violations']) for a in audit_rows),
        'attempt_count':len(attempts_out),'pair_cache_exact_comparisons':len(attempts_out),'model_response_metadata':[{**json.loads(k),'responses':v} for k,v in model_metadata.items()],
        'runtime_error_codes':dict(runtime_errors),'unique_shared_prefix_accounting':prefixes,'collection_start_utc':min(a['started_utc'] for a in attempts_out),
        'collection_end_utc':max(a['finished_utc'] for a in attempts_out)}


def summarize(rows,transitions,episodes,failures,verification,manifest,status,iterations):
    grouped=defaultdict(list)
    for r in rows: grouped[r['scenario'],r['config_id'],r['policy']].append(r)
    table1=[]
    for (scenario,config,policy),group in sorted(grouped.items()):
        table1.append({'scenario':scenario,'config_id':config,'policy':policy,'planned':len(group),
            **{k:sum(bool(r[k]) for r in group) for k in ['checkpoint_reached','event_exposure','rejection','task_completion','state_goal','runtime_failure']},
            'integrity_1':sum(r['I']==1 for r in group),'integrity_0':sum(r['I']==0 for r in group),'unknown':sum(r['I']=='unknown' for r in group),
            'not_started':sum(r['terminal']=='not_started' for r in group)})
    pairs=[]; lookup={(r['task_instance_id'],r['policy']):r for r in rows}
    metrics=['task_completion','suffix_agent_tool_calls','suffix_model_turns','suffix_authorization_requests','suffix_elapsed_ms','budget_capped_time_to_success_ms']
    for p in manifest['pairs']:
        a,b=[lookup[p['case_id'],policy] for policy in ['context','bound']]
        pair={'task_instance_id':p['case_id'],'scenario':p['scenario'],'config_id':'A'}
        for metric in metrics: pair['delta_'+metric]=float(b[metric])-float(a[metric]) if a[metric] is not None and b[metric] is not None else None
        pair['delta_usage']={k:b['suffix_usage'][k]-a['suffix_usage'][k] if a['suffix_usage'].get(k) is not None and b['suffix_usage'].get(k) is not None else None for k in sorted(set(a['suffix_usage'])|set(b['suffix_usage']))}
        pairs.append(pair)
    policy_summary={}
    for policy in ['context','bound']:
        group=[r for r in rows if r['policy']==policy]
        policy_summary[policy]={'scheduled':len(group),'checkpoint_reached':sum(r['checkpoint_reached'] for r in group),
            'completion':sum(r['task_completion'] for r in group),'integrity_1':sum(r['I']==1 for r in group),'integrity_0':sum(r['I']==0 for r in group),
            'integrity_unknown':sum(r['I']=='unknown' for r in group),'runtime_failure':sum(r['runtime_failure'] for r in group),
            'U_I_joint_cells':dict(Counter(f"U={int(r['task_completion'])},I={r['I']}" for r in group))}
    effects={'completion':paired_summary(rows,'task_completion',iterations), 'continuity':paired_summary(rows,'continuity_failure_incidence',iterations)}
    effects['continuity']['identification_lower']=paired_summary(rows,'continuity_failure_incidence',iterations,unknown='lower')
    effects['continuity']['identification_upper']=paired_summary(rows,'continuity_failure_incidence',iterations,unknown='upper')
    effects['by_scenario']={s:{metric:paired_summary([r for r in rows if r['scenario']==s],metric,iterations) for metric in ['task_completion','suffix_agent_tool_calls','suffix_elapsed_ms']} for s in sorted({r['scenario'] for r in rows})}
    g_rows=[r for r in rows if r['scenario']=='G']; g_bound=[r for r in g_rows if r['policy']=='bound']; g_eps=[e for e in episodes if e['scenario']=='G' and e['policy']=='bound']
    g={'scheduled_pairs':len(g_bound),'checkpoint_reached_pairs':sum(r['checkpoint_reached'] for r in g_bound),
        'bound_delivered_episodes':sum(e['Delivered'] for e in g_eps),'bound_delivered_recoverable_episodes':sum(e['Delivered'] and e['RecoverableReject'] for e in g_eps),
        'bound_recovery_paths':dict(Counter(r['recovery_path'] or 'none' for r in g_bound)),'bound_recovery_success':sum(r['G_standardized_recovery_success'] for r in g_bound),
        'bound_U_I_cells':dict(Counter(f"U={int(r['task_completion'])},I={r['I']}" for r in g_bound)),
        'context_substitution_transitions':sum(t['scenario']=='G' and t['policy']=='context' and t['executed_substitution'] for t in transitions),
        'paired_suffix_calls':paired_summary(g_rows,'suffix_agent_tool_calls',iterations),'paired_suffix_elapsed_ms':paired_summary(g_rows,'suffix_elapsed_ms',iterations),
        'bound_episode_details':g_eps}
    n={'transitions':len([t for t in transitions if t['scenario']=='N']),
       'transition_cells':dict(Counter(f"{t['policy']};same_instance={t['same_instance']};admissible={t['policy_admissible']};compatible={t['A_instance_compatible']}" for t in transitions if t['scenario']=='N'))}
    cb=sum(lookup[t,'context']['task_completion'] and not lookup[t,'bound']['task_completion'] for t in {r['task_instance_id'] for r in rows})
    bc=sum(lookup[t,'bound']['task_completion'] and not lookup[t,'context']['task_completion'] for t in {r['task_instance_id'] for r in rows}); nd=cb+bc
    effects['mcnemar']={'context_only':cb,'bound_only':bc,'exact_two_sided_p':min(1,2*sum(math.comb(nd,k) for k in range(min(cb,bc)+1))/(2**nd)) if nd else 1,'secondary':True}
    summary={'title':'Supplementary paired evaluation of deployment A','collection_status':status['status'],'freeze_id':manifest['freeze_id'],
        'planned_arms':len(rows),'paired_units':len(manifest['pairs']),'task_clusters':len(manifest['pairs']),'policy_summary':policy_summary,
        'scenario_counts':dict(Counter(p['scenario'] for p in manifest['pairs'])),'table1':table1,'effects':effects,'G':g,'N':n,
        'delivered_feedback':{'episodes':len(episodes),'delivered':sum(e['Delivered'] for e in episodes),'delivered_recoverable':sum(e['Delivered'] and e['RecoverableReject'] for e in episodes)},
        'failure_arms':len(failures),'runtime_failure_arms':[{'pair_id':r['pair_id'],'policy':r['policy'],'scenario':r['scenario'],'terminal':r['terminal'],'termination_payload':r['termination_payload']} for r in rows if r['runtime_failure']],
        'verification':verification,'currency_cost':None,'formal_inference_allowed':False,
        'analysis_scope':'Conditional/exploratory supplementary A-only paired application of original task-stratified bootstrap method; not the preregistered A+B estimator. Selection by pre-response quota; later separately frozen collection. Original 512 arms unchanged; no pooled estimate.',
        'bootstrap':{'iterations':iterations,'seed':20261007,'unit':'task/pair; retain both policies','stratification':'scenario; retain observed scenario counts','interval':'percentile 95%; order indices int(.025*(B-1)), int(.975*(B-1))'},
        'recovery_conditioning':'post-treatment descriptive; G bound is the fixed standardized probe',
        'deployment_identity_limitation':'Requested alias and SDK are recorded. Actual returned model/revision are not exposed. DEPLOYMENT_CHANGED denotes runtime identity-check failure, not proof of a model revision change.'}
    return table1,pairs,summary


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=ROOT/'outputs'); parser.add_argument('--bootstrap-iterations',type=int,default=10000); args=parser.parse_args()
    destination=args.output.resolve()
    if ROOT not in destination.parents: raise ValueError('OUTPUT_MUST_STAY_WITHIN_ANALYSIS_PACKAGE')
    destination.mkdir(parents=True,exist_ok=True)
    manifest,verification=verify_sources(); status=read(RECOVERY/'results/collection-status.json'); selected=select_attempts(manifest,status)
    check_attempt_inventory([a['directory'] for p in selected for a in p['attempts']],
                            [p.relative_to(RECOVERY/'results').as_posix() for p in (RECOVERY/'results').glob('*/attempt-*') if p.is_dir()])
    before=file_hashes(RECOVERY/'results'); write(destination/'source-file-hashes.json',before)
    rows,transitions,episodes,failures,checks=extract(manifest,selected,destination); verification.update(checks)
    table1,pairs,summary=summarize(rows,transitions,episodes,failures,verification,manifest,status,args.bootstrap_iterations)
    tables={'table1-outcomes.csv':table1,'table2-continuity.csv':transitions,'table3-recovery.csv':episodes,'paired-effects.csv':pairs}
    columns={
        'table2-continuity.csv':['task_instance_id','scenario','config_id','policy','pair_id','transition_id','origin','same_value','same_context','same_instance','policy_admissible','A_instance_compatible','executed_substitution','source_provenance_integrity','copy_forward'],
        'table3-recovery.csv':['task_instance_id','scenario','config_id','policy','pair_id','origin','trigger_code','feedback_event_id','Delivered','RecoverableReject','first_meaningful_action','recovery_strategy','labels','U','I','additional_tool_calls','additional_model_turns','additional_authorizations','reproposals','reverifications','elapsed_ms','usage_records','recovered']}
    for name,table in tables.items(): csv_write(destination/name,table,columns.get(name,list(table[0]) if table else []))
    csv_write(destination/'table4-utility-friction.csv',rows,['task_instance_id','scenario','config_id','policy','pair_id','task_completion','suffix_agent_tool_calls','suffix_model_turns','suffix_authorization_requests','suffix_elapsed_ms','logical_elapsed_ms','budget_capped_time_to_success_ms','suffix_usage','prefix_usage','terminal'])
    csv_write(destination/'failure-archaeology-all-arms.csv',failures,['task_instance_id','scenario','config_id','policy','pair_id','task_completion','I','terminal','failure_stage','failure_labels','violations','missing','episodes','audit_errors','bound_rejection_friction_observed'])
    write(destination/'analysis-summary.json',summary)
    if file_hashes(RECOVERY/'results')!=before: raise ValueError('RAW_RESULTS_CHANGED_DURING_ANALYSIS')
    verify_sources()
    print(json.dumps({k:summary[k] for k in ['planned_arms','paired_units','policy_summary','scenario_counts','G','N','runtime_failure_arms']},ensure_ascii=False),flush=True)


if __name__=='__main__': main()
