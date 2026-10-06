"""Generate/freeze deterministic formal inputs only. Never starts online collection."""
import hashlib,json,platform,shutil,subprocess,sys
from pathlib import Path
from importlib.metadata import version
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from phase2.kernel import canonical,digest,utc,MANIFEST
from phase2.generator import generate_tasks,generate_assignments,COUNTS,SEED,VERSION
from phase2.runner import initial_messages
from phase2.providers import ACTION_SCHEMA,OUTPUT_RULE
from freeze_documents import DOCUMENTS


def write_documents():
    directory=ROOT/'frozen-formal';directory.mkdir(exist_ok=True)
    if (directory/'master-sha256.json').exists():raise ValueError('REFUSE_TO_CHANGE_EXISTING_FREEZE')
    for name,text in DOCUMENTS.items():(directory/name).write_text(text,encoding='utf-8')
    manifest={k:MANIFEST[k] for k in ['context_field_whitelist','context_excludes','policy_definitions',
        'accountability_requirement','shared_guards','task_prompt_template','source_evidence_template']}
    manifest.update(status='FORMAL_PREPARATION',protocol_version='phase2-formal-v1.0',scenario_counts=COUNTS,
        recommended={'task_instances':128,'agent_configurations':2,'policies':['context','bound'],'repetitions':1,
                     'paired_units':256,'online_policy_arms':512},
        pilot={'case_ids':['PILOT-L-01','PILOT-N-01','PILOT-N-02','PILOT-G-01'],
               'status':'COMPLETE_IN_SEPARATE_IMMUTABLE_PACKAGE','excluded_from_formal_analysis':True})
    (ROOT/'frozen-design/protocol-manifest.json').write_text(canonical(manifest),encoding='utf-8')


def freeze():
    directory=ROOT/'frozen-formal'
    if (directory/'master-sha256.json').exists():raise ValueError('REFUSE_TO_OVERWRITE_FREEZE')
    tasks=generate_tasks();pairs=generate_assignments(tasks);stamp=utc()
    observations=json.loads((ROOT/'preflight/deployment-identity/agent-config-observations.json').read_text(encoding='utf-8'))
    deterministic=json.loads((ROOT/'preflight/deterministic-final-128/deterministic-fixture-results.json').read_text(encoding='utf-8'))
    test=json.loads((ROOT/'preflight/test-summary.json').read_text(encoding='utf-8'))
    review=(ROOT/'reviews/final-review.md').read_text(encoding='utf-8')
    blockers=[]
    if len(observations)!=2 or any(o['status']!='AVAILABLE' for o in observations):blockers.append('deployment_availability_not_confirmed')
    if len(tasks)!=128 or len(pairs)!=256:blockers.append('task_assignment_count')
    if deterministic['status']!='PASS' or deterministic['task_instances']!=128 or deterministic['online_model_calls']!=0:blockers.append('deterministic_preflight')
    if test['status']!='PASS':blockers.append('runner_scorer_tests')
    if 'FINAL RETEST — PASS' not in review:blockers.append('independent_final_review')
    source_files=sorted(list((ROOT/'src').rglob('*.py'))+list((ROOT/'tests').rglob('*.py'))+list(ROOT.glob('*.py')))
    sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    if deterministic.get('source_sha256')!=sources:blockers.append('preflight_source_changed')
    if test.get('source_sha256')!=sources:blockers.append('tests_source_changed')
    freeze_id='phase2-formal-v1.0-'+digest({'timestamp':stamp,'inputs':[t['input_sha256'] for t in tasks],'sources':sources})[:16]
    configs=[]
    for observation in observations:
        config={**observation['config'],'actual_returned_identifier':observation['actual_returned_identifier'],
            'observable_revision':observation.get('observable_revision'),'identity_limitation':observation.get('identity_limitation'),
            'availability_probe_start_utc':observation['probe_start_utc'],'availability_probe_end_utc':observation['probe_end_utc']}
        configs.append(config)
    prompts=[{'task_instance_id':t['task_instance_id'],'messages':initial_messages(t),
              'messages_sha256':digest(initial_messages(t)), 'provider_prompt_sha256':hashlib.sha256((OUTPUT_RULE+'\nVISIBLE CONVERSATION:\n'+canonical(initial_messages(t))).encode()).hexdigest()} for t in tasks]
    environment={'python':platform.python_version(),'platform':platform.platform(),
        'dependencies':{name:version(name) for name in ['jsonschema','PyYAML','matplotlib']},
        'base_git_commit':subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,cwd=ROOT).stdout.strip(),
        'collection_window_utc':None,'collection_window_status':'NOT_STARTED; actual event timestamps define window',
        'source_version':'phase2-formal-v1.0','source_commit_note':'Final Git commit contains this byte-hashed source snapshot; no self-referential commit hash is claimed.'}
    objects={
        'formal-task-manifest.json':{'freeze_id':freeze_id,'generator_version':VERSION,'scenario_counts':COUNTS,'task_count':128,'tasks':tasks},
        'assignment-manifest.json':{'freeze_id':freeze_id,'seed':SEED,'pair_count':256,'arm_count':512,'repetition':1,
            'pairs':pairs,'arms':[{'pair_id':p['pair_id'],'task_instance_id':p['case_id'],'config_id':p['config_id'],
                                 'policy':policy,'arm_index_within_pair':i,'run_id':p['pair_id']+'-'+policy} for p in pairs for i,policy in enumerate(p['order'])]},
        'agent-config-manifest.json':{'freeze_id':freeze_id,'configs':configs,'workers':2,'per_config_concurrency':1,
            'resource_limits':{'prefix_tools':12,'prefix_responses':8,'prefix_seconds':300,'suffix_tools':24,'suffix_responses':20,
                'suffix_seconds':720,'request_seconds':90,'outer_transport_retries':2,'retry_wait_seconds':[2,8],
                'format_repairs_per_logical_history':1,'B_output_tokens':4096,'A_output_tokens':None,'currency_cap':None}},
        'prompt-manifest.json':{'freeze_id':freeze_id,'output_rule':OUTPUT_RULE,'output_rule_sha256':hashlib.sha256(OUTPUT_RULE.encode()).hexdigest(),
            'prompt_hash_definition':'UTF8 OUTPUT_RULE + newline VISIBLE CONVERSATION + canonical JSON of frozen initial messages; exact sent prompt.txt is retained and hashed at every request',
            'action_schema':ACTION_SCHEMA,'initial_prompts':prompts},
        'environment-manifest.json':environment,
        'source-version-hashes.json':{'freeze_id':freeze_id,'source_version':'phase2-formal-v1.0','sha256':sources},
        'task-input-hashes.json':{'freeze_id':freeze_id,'hash_definition':'canonical JSON of entire task excluding input_sha256',
            'sha256':{t['task_instance_id']:t['input_sha256'] for t in tasks}},
        'deterministic-fixture-results.json':{k:v for k,v in deterministic.items() if k!='records'},
        'readiness.json':{'status':'NO' if blockers else 'YES','FORMAL_FREEZE_READY':'NO' if blockers else 'YES','blockers':blockers,
            'freeze_id':freeze_id,'freeze_timestamp_utc':stamp,'workers':2,'formal_online_arms_collected':0,
            'pilot_excluded':True,'local_registration_only':True}}
    for name,obj in objects.items():(directory/name).write_text(canonical(obj),encoding='utf-8')
    shutil.copyfile(ROOT/'frozen-design/tool-definitions.json',directory/'tool-schema.json')
    shutil.copyfile(ROOT/'frozen-design/trajectory-event.schema.json',directory/'trajectory-event.schema.json')
    diversity={key:sorted({canonical(t['parameters'][key]) for t in tasks}) for key in tasks[0]['parameters']}
    (directory/'task-diversity-summary.json').write_text(canonical({'dimensions':diversity,'unique_parameter_vectors':len({canonical(t['parameters']) for t in tasks}),
        'business_templates':8,'full_factorial':False,'outcome_based_selection':False}),encoding='utf-8')
    include=source_files+list((ROOT/'frozen-design').glob('*.json'))+list(directory.iterdir())
    include += list((ROOT/'reviews').glob('*.md'))+list((ROOT/'preflight/deployment-identity').rglob('*'))
    include += list((ROOT/'preflight/deterministic-final-128').iterdir())+[ROOT/'preflight/test-summary.json',ROOT/'preflight/test-results-final.txt',ROOT/'requirements.txt']
    files={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(include)) if p.is_file() and p.name not in ('master-sha256.json','master-sha256.txt') and '__pycache__' not in p.parts}
    master={'freeze_id':freeze_id,'timestamp_utc':stamp,'status':objects['readiness.json']['status'],'files':files}
    (directory/'master-sha256.json').write_text(canonical(master),encoding='utf-8')
    master_hash=hashlib.sha256((directory/'master-sha256.json').read_bytes()).hexdigest()
    (directory/'master-sha256.txt').write_text(master_hash+'  master-sha256.json\n',encoding='utf-8')
    print(canonical({'FORMAL_FREEZE_READY':master['status'],'blockers':blockers,'master_hash':master_hash,'freeze_id':freeze_id,'timestamp_utc':stamp}))

if __name__=='__main__':
    if '--write-documents' in sys.argv:write_documents()
    else:freeze()
