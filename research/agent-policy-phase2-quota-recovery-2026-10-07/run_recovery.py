"""Additive, user-authorized recollection of quota-blocked A prefixes.

Original formal records and source remain read-only. New attempts have a new
batch identity and retain their own ledger. This is not the original freeze's
automatic --resume and must not silently replace original primary outcomes.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT.parent / 'agent-policy-phase2-formal-2026-10-07'
sys.path.insert(0, str(ORIGINAL))
sys.path.insert(0, str(ORIGINAL / 'src'))
from run_formal import verify_freeze
from phase2.kernel import canonical, utc
from phase2.orchestrator import IdentityProvider
from phase2.providers import TransportError
from phase2.runner import execute_pair


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w', encoding='utf-8') as handle:
        handle.write(canonical(value)); handle.flush(); os.fsync(handle.fileno())
    for attempt in range(8):
        try:
            tmp.replace(path)
            return
        except PermissionError:
            if attempt == 7: raise
            time.sleep(.25 * (attempt + 1))


def hash_tree(directory):
    return {p.relative_to(directory).as_posix():sha(p) for p in sorted(directory.rglob('*'))
            if p.is_file() and p.suffix.lower() not in ('.lock', '.pyc') and '__pycache__' not in p.parts}


def is_quota_text(text):
    text = text.lower()
    return 'usage limit' in text or 'usage_limit' in text or 'quota exhausted' in text


def quota_in(directory):
    for p in directory.rglob('stdout.jsonl'):
        for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
            try: event = json.loads(line)
            except ValueError: continue
            if event.get('type') == 'error' and is_quota_text(str(event.get('message', ''))): return True
    return False


def eligible_pairs(results, status):
    selected=[]
    for name, record in status['pairs'].items():
        if record.get('status') != 'terminal' or record['assignment']['config_id'] != 'A': continue
        if record.get('result', {}).get('checkpoint_reached') is not False: continue
        prefix=results/name/'prefix'
        events=[json.loads(line) for line in (prefix/'events.jsonl').read_text(encoding='utf-8').splitlines()]
        if any(e['event_type']=='model_response' for e in events): continue
        if quota_in(prefix): selected.append(name)
    return sorted(selected)


class RecoveryProvider(IdentityProvider):
    def decide(self, messages, directory, timeout=90):
        try: return super().decide(messages, directory, timeout)
        except TransportError:
            if quota_in(directory): raise TransportError('ACCOUNT_QUOTA_EXHAUSTED', False)
            raise


def lock_output(output):
    output.mkdir(parents=True,exist_ok=True)
    lock=(output/'COLLECTION.lock').open('a+b')
    lock.seek(0); lock.write(b'0'); lock.flush(); lock.seek(0)
    try:
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BaseException:
        lock.close(); raise
    return lock


def collect(manifest, output, execute=execute_pair, provider=None):
    lock=lock_output(output)
    try:
        state_path=output/'collection-status.json'
        state=read(state_path) if state_path.exists() else {'freeze_id':manifest['freeze_id'],'pairs':{}}
        if state['freeze_id'] != manifest['freeze_id']: raise ValueError('RECOVERY_FREEZE_CHANGED')
        provider=provider if provider is not None else RecoveryProvider({**manifest['agent_config'],'freeze_id':manifest['freeze_id']})
        state['status']='RUNNING'; state['updated_utc']=utc(); write(state_path,state)
        for assignment in manifest['pairs']:
            name=assignment['pair_id']; previous=state['pairs'].get(name,{})
            if previous.get('status')=='terminal': continue
            attempts=previous.get('attempts',[])
            if previous.get('status')=='running':
                attempt=attempts[-1]
            else:
                attempt={'directory':f'{name}/attempt-{len(attempts)+1:03d}','started_utc':utc()}
                attempts.append(attempt)
            destination=output/attempt['directory']
            state['pairs'][name]={'status':'running','assignment':assignment,'attempts':attempts}
            write(state_path,state)
            try:
                result=execute(manifest['tasks'][assignment['case_id']],provider,destination,assignment['order'],resume=destination.exists())
                attempt['finished_utc']=utc(); attempt['result']=result
                quota=result.get('prefix',{}).get('error')=='ACCOUNT_QUOTA_EXHAUSTED' or quota_in(destination)
                prefix=destination/'prefix/events.jsonl'
                events=[json.loads(line) for line in prefix.read_text(encoding='utf-8').splitlines()] if prefix.exists() else []
                # Retrying a prefix with no Agent response does not repeat a semantic action.
                no_response=not any(e['event_type']=='model_response' for e in events)
                state['pairs'][name]['status']='waiting_for_quota' if quota and no_response else 'terminal'
                if quota: state['status']='PAUSED_QUOTA'
                elif result.get('deployment_changed'): state['status']='PAUSED_DEPLOYMENT'
                elif any(result.get(p,{}).get('audit_errors') for p in assignment['order']): state['status']='PAUSED_AUDIT'
                state['updated_utc']=utc(); write(state_path,state)
                print(canonical({'pair':name,'status':state['pairs'][name]['status'],'batch_status':state['status'],
                    'terminal_pairs':sum(r['status']=='terminal' for r in state['pairs'].values()),
                    'planned_pairs':len(manifest['pairs'])}),flush=True)
                if state['status']!='RUNNING': return state
            except BaseException as exc:
                # Keep this attempt open for the original runner's safe-boundary resume.
                state['status']='PAUSED_INFRASTRUCTURE'; state['error']=type(exc).__name__+': '+str(exc)[:200]
                state['updated_utc']=utc(); write(state_path,state)
                raise
        state['status']='COMPLETE'; state['updated_utc']=utc()
        state['terminal_pairs']=sum(r['status']=='terminal' for r in state['pairs'].values())
        write(state_path,state); return state
    finally: lock.close()


def prepare():
    master=verify_freeze(ORIGINAL)
    results=ORIGINAL/'formal-results'; status=read(results/'collection-status.json')
    selected=eligible_pairs(results,status)
    if len(selected)!=117: raise ValueError(f'EXPECTED_117_QUOTA_BLOCKED_PAIRS_GOT_{len(selected)}')
    assignments=read(ORIGINAL/'frozen-formal/assignment-manifest.json')['pairs']
    tasks=read(ORIGINAL/'frozen-formal/formal-task-manifest.json')['tasks']
    config=next(c for c in read(ORIGINAL/'frozen-formal/agent-config-manifest.json')['configs'] if c['id']=='A')
    manifest={'created_utc':utc(),'parent_freeze_master':master,
        'authorization':'User explicitly authorized quota rerun and preservation of existing data on 2026-10-07.',
        'amendment':'Administrative quota-recovery recollection; original formal ledger is immutable. Report batches separately; no unlabelled replacement of primary outcomes.',
        'eligibility':'A, terminal before review checkpoint, zero model responses, raw provider usage-limit error; selection ignores U/I and behavioral outcomes.',
        'pairs':[a for a in assignments if a['pair_id'] in selected],
        'tasks':{t['task_instance_id']:t for t in tasks if t['task_instance_id']+'-A' in selected},
        'agent_config':config,'workers':1,'planned_pairs':117,'planned_arms':234,
        'source_script_sha256':sha(Path(__file__)),
        'test_script_sha256':sha(ROOT/'test_recovery.py'),
        'original_result_file_hashes':hash_tree(results),
        'failure_rule':'Quota before first Agent response pauses and keeps attempt; manual resume uses new attempt directory. Quota after a response preserves terminal attempt, pauses batch; ordinary terminal outcomes are never rerun. Interrupted work resumes only via original safe-boundary rules.',
        'analysis_rule':'Keep original 512-arm primary analysis. Recovery cohort has 117 selected tasks / 234 paired arms; analyze separately and label any joined sensitivity view with original/recovery provenance.'}
    manifest['freeze_id']='phase2-quota-recovery-v1-'+hashlib.sha256(canonical(manifest).encode()).hexdigest()[:12]
    destination=ROOT/'recovery-manifest.json'
    if destination.exists(): raise ValueError('RECOVERY_MANIFEST_ALREADY_EXISTS')
    write(destination,manifest)
    (ROOT/'recovery-manifest.sha256').write_text(sha(destination)+'\n',encoding='ascii')
    print(canonical({k:manifest[k] for k in ('freeze_id','planned_pairs','planned_arms','workers')}))


def verify():
    verify_freeze(ORIGINAL)
    path=ROOT/'recovery-manifest.json'
    if sha(path)!=(ROOT/'recovery-manifest.sha256').read_text().strip(): raise ValueError('RECOVERY_MANIFEST_CHANGED')
    m=read(path)
    if sha(Path(__file__))!=m['source_script_sha256'] or sha(ROOT/'test_recovery.py')!=m['test_script_sha256']: raise ValueError('RECOVERY_SOURCE_CHANGED')
    if hash_tree(ORIGINAL/'formal-results')!=m['original_result_file_hashes']: raise ValueError('ORIGINAL_DATA_CHANGED')
    return m


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--prepare',action='store_true'); parser.add_argument('--run',action='store_true')
    parser.add_argument('--verify-only',action='store_true'); args=parser.parse_args()
    if args.prepare: prepare()
    elif args.run:
        manifest=verify(); result=collect(manifest,ROOT/'results'); verify()
        print(canonical({'status':result['status']}),flush=True)
        sys.exit(0 if result['status']=='COMPLETE' else 2)
    elif args.verify_only:
        m=verify(); print(canonical({'status':'PASS','freeze_id':m['freeze_id'],'original_data':'UNCHANGED'}))
    else: parser.error('Choose --prepare, --run or --verify-only')
