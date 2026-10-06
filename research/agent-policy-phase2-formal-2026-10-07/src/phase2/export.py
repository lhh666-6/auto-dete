"""Four tables, all failure arms, unique-prefix accounting, frozen paired effects."""
import csv, json
from pathlib import Path
from collections import defaultdict
from .oracle import encode,evidence_valid,sha,transition_outcomes
from .runner import score_run,validate_run
from .analysis import paired_estimates


def trivalent_and(values):
    values=list(values)
    return False if False in values else (None if None in values else True)


def read_events(directory):
    file=directory/'events.jsonl'
    return [json.loads(l) for l in file.read_text(encoding='utf-8').splitlines()] if file.exists() else []


def usage_totals(events):
    records=[e['payload'].get('usage') for e in events if e['event_type']=='model_response']
    keys=sorted({k for r in records if isinstance(r,dict) for k,v in r.items() if isinstance(v,(int,float))})
    return {k:sum(r[k] for r in records) if records and all(isinstance(r,dict) and isinstance(r.get(k),(int,float)) for r in records) else None for k in keys}


def csv_write(file,rows,columns):
    with file.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader()
        for row in rows: writer.writerow({k:(json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v) for k,v in row.items()})


def export_tables(freeze_dir,result_dir,destination,bootstrap_iterations=10000):
    destination.mkdir(parents=True,exist_ok=False)
    assignments=json.loads((freeze_dir/'assignment-manifest.json').read_text(encoding='utf-8'))['pairs']
    arm_rows=[]; transition_rows=[]; episode_rows=[]; failures=[]; prefixes=[]
    for pair in assignments:
        directory=result_dir/pair['pair_id']; prefix=read_events(directory/'prefix')
        reached=any(e['event_type']=='checkpoint' and e['payload']['reached'] for e in prefix)
        prefix_elapsed=prefix[-1]['elapsed_ms'] if prefix else None
        prefix_usage=usage_totals(prefix)
        prefixes.append({'pair_id':pair['pair_id'],'config_id':pair['config_id'],
            'responses':sum(e['event_type']=='model_response' for e in prefix),'usage':prefix_usage,
            'charged_once':True,'provider_cost_currency':None})
        for policy in pair['order']:
            arm=directory/policy; events=read_events(arm)
            score=score_run(arm) if arm.exists() else {'task_completion':False,'state_goal':False,'I':'unknown',
                'continuity_failure_incidence':None,'terminal':'not_started','episodes':[],'audit_errors':['arm_not_started']}
            identity={'task_instance_id':pair['case_id'],'scenario':pair['scenario'],'config_id':pair['config_id'],'policy':policy,'pair_id':pair['pair_id']}
            calls=[e for e in events if e['event_type']=='tool_call' and e['origin']=='agent']
            responses=[e for e in events if e['event_type']=='model_response']
            decisions=[e for e in events if e['event_type']=='admission_decision']
            runtime=score['terminal'] in ('runtime_error','prefix_failure','audit_state_missing')
            row={**identity,'planned':1,'checkpoint_reached':reached,
                'event_exposure':sum(bool(e['event_type']=='workflow_event' and (e['payload'].get('kind') or e['origin']=='harness_handoff')) for e in events),
                'rejection':sum(e['payload']['decision']=='rejected' for e in decisions),
                'task_completion':score['task_completion'],'state_goal':score['state_goal'],'I':score['I'],
                'continuity_failure_incidence':score.get('continuity_failure_incidence'),
                'runtime_failure':runtime,'terminal':score['terminal'],
                'suffix_agent_tool_calls':len(calls) if events else None,'suffix_model_turns':len(responses) if events else None,
                'suffix_authorization_requests':sum(e['payload']['tool_name']=='request_authorization' for e in calls) if events else None,
                'suffix_elapsed_ms':events[-1]['elapsed_ms'] if events else None,
                'logical_elapsed_ms':prefix_elapsed+events[-1]['elapsed_ms'] if prefix_elapsed is not None and events else None,
                'budget_capped_time_to_success_ms':min(720000,events[-1]['elapsed_ms']) if score['task_completion'] and events else 720000,
                'suffix_usage':usage_totals(events),'prefix_usage':prefix_usage,'audit_errors':score.get('audit_errors',[])}
            arm_rows.append(row)
            for episode in score.get('episodes',[]): episode_rows.append({**identity,**episode})
            for e in decisions:
                p=e['payload']
                if p['decision']!='accepted' or p.get('idempotent_receipt'): continue
                try:
                    state=json.loads((arm/p['post_state_ref']['relative_path']).read_text(encoding='utf-8'))
                    transition=next(t for t in state['transitions'] if t['commit_request_id']==p['commit_request_id'])
                    c,g=transition['candidate'],transition['grant'];field=state['case']['field_key'];tid=transition['transition_id']
                    same_value=c['context']['proposal_value_payload']==g['context']['proposal_value_payload']
                    same_context=encode(c['context'])==encode(g['context']); same_instance=c['candidate_id']==g['reviewed_candidate_id']
                    source=transition['post']['sources'][field]==tid and all(c['context'].get(k)==v for k,v in state['case'].get('retained_metadata',{}).items())
                    copy_forward=all(encode(transition['pre']['values'][k])==encode(transition['post']['values'][k]) and transition['pre']['sources'][k]==transition['post']['sources'][k] for k in transition['pre']['values'] if k!=field)
                    checks=transition_outcomes(state,transition)
                    guard=trivalent_and(value for name,value in checks.items() if name!='A_instance')
                    source=checks['source_provenance']; copy_forward=checks['copy_forward']
                    transition_rows.append({**identity,'transition_id':tid,'origin':p['caller_origin'],
                        'same_value':same_value,'same_context':same_context,'same_instance':same_instance,
                        'policy_admissible':trivalent_and([guard,same_context,policy=='context' or same_instance]),
                        'A_instance_compatible':trivalent_and([guard,same_context,same_instance]),'executed_substitution':not same_instance,
                        'source_provenance_integrity':source,'copy_forward':copy_forward})
                except (OSError,StopIteration,KeyError,ValueError):
                    transition_rows.append({**identity,'transition_id':'unclassifiable','origin':p['caller_origin']})
            if not score['task_completion'] or score['I'] in (0,'unknown'):
                labels=list(score.get('failure_labels',[]))
                if score['I']==0 and policy=='context' and score['task_completion']: labels.append('context_A_instance_incompatible_success')
                if not score['task_completion'] and score['state_goal'] and not score.get('preview_delivered',True): labels.append('business_preview_missing')
                if score.get('I')=='unknown': labels.append('integrity_unclassifiable')
                if runtime: labels.append('provider_or_runtime_failure')
                if not reached: stage='shared_prefix'
                elif score.get('audit_errors'): stage='audit_coverage'
                elif not score.get('accurate_report',False): stage='final_report_or_suffix'
                else: stage='task_deliverable_or_integrity'
                failures.append({**row,'failure_labels':list(dict.fromkeys(labels)),'failure_stage':stage,
                    'violations':score.get('violations',[]),'missing':score.get('missing',[]),
                    'episodes':score.get('episodes',[]),'bound_rejection_friction_observed':policy=='bound' and bool(score.get('episodes')) and not score['task_completion']})
    grouped=defaultdict(list)
    for row in arm_rows: grouped[row['scenario'],row['config_id'],row['policy']].append(row)
    table1=[]
    for (scenario,config,policy),rows in sorted(grouped.items()):
        table1.append({'scenario':scenario,'config_id':config,'policy':policy,'planned':len(rows),
            **{k:sum(bool(r[k]) for r in rows) for k in ['checkpoint_reached','event_exposure','rejection','task_completion','state_goal','runtime_failure']},
            'integrity_1':sum(r['I']==1 for r in rows),'integrity_0':sum(r['I']==0 for r in rows),'unknown':sum(r['I']=='unknown' for r in rows),
            'not_started':sum(r['terminal']=='not_started' for r in rows)})
    csv_write(destination/'table1-outcomes.csv',table1,list(table1[0]) if table1 else [])
    csv_write(destination/'table2-continuity.csv',transition_rows,['task_instance_id','scenario','config_id','policy','pair_id','transition_id','origin','same_value','same_context','same_instance','policy_admissible','A_instance_compatible','executed_substitution','source_provenance_integrity','copy_forward'])
    csv_write(destination/'table3-recovery.csv',episode_rows,['task_instance_id','scenario','config_id','policy','pair_id','origin','trigger_code','feedback_event_id','Delivered','RecoverableReject','first_meaningful_action','recovery_strategy','labels','U','I','additional_tool_calls','additional_model_turns','additional_authorizations','reproposals','reverifications','elapsed_ms','usage_records','recovered'])
    csv_write(destination/'table4-utility-friction.csv',arm_rows,['task_instance_id','scenario','config_id','policy','pair_id','task_completion','suffix_agent_tool_calls','suffix_model_turns','suffix_authorization_requests','suffix_elapsed_ms','logical_elapsed_ms','budget_capped_time_to_success_ms','suffix_usage','prefix_usage','terminal'])
    csv_write(destination/'failure-archaeology-all-arms.csv',failures,['task_instance_id','scenario','config_id','policy','pair_id','task_completion','I','terminal','failure_stage','failure_labels','violations','missing','episodes','audit_errors','bound_rejection_friction_observed'])
    effects=paired_estimates(arm_rows,iterations=bootstrap_iterations)
    lookup={(r['task_instance_id'],r['config_id'],r['policy']):r for r in arm_rows}
    paired=[]
    for pair in assignments:
        a,b=[lookup[pair['case_id'],pair['config_id'],p] for p in ['context','bound']]
        row={'task_instance_id':pair['case_id'],'scenario':pair['scenario'],'config_id':pair['config_id']}
        for metric in ['task_completion','suffix_agent_tool_calls','suffix_model_turns','suffix_authorization_requests','suffix_elapsed_ms','budget_capped_time_to_success_ms']:
            row['delta_'+metric]=float(b[metric])-float(a[metric]) if a[metric] is not None and b[metric] is not None else None
        usage_keys=set(a['suffix_usage'])|set(b['suffix_usage'])
        row['delta_usage']={key:b['suffix_usage'][key]-a['suffix_usage'][key] if a['suffix_usage'].get(key) is not None and b['suffix_usage'].get(key) is not None else None for key in usage_keys}
        paired.append(row)
    csv_write(destination/'paired-effects.csv',paired,list(paired[0]) if paired else [])
    status_file=result_dir/'collection-status.json'
    final_status=json.loads(status_file.read_text(encoding='utf-8')).get('status') if status_file.exists() else 'ENGINEERING_FIXTURE_OR_INCOMPLETE'
    result={'planned_arms':len(arm_rows),'paired_units':len(assignments),'task_clusters':128,'effects':effects,
        'collection_status':final_status,'formal_inference_allowed':final_status=='COMPLETE',
        'unique_shared_prefix_accounting':prefixes,'failure_arms':len(failures),
        'suffix_usage_records':[r['suffix_usage'] for r in arm_rows],'currency_cost':None,
        'recovery_conditioning':'post-treatment descriptive; G bound is the fixed standardized probe'}
    (destination/'analysis-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result
