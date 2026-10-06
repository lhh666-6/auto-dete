"""Two fixed provider lanes; durable status and full planned denominators."""
import json, threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from .kernel import utc, canonical
from .providers import Provider, TransportError
from .runner import execute_pair, durable_json, score_run


def validate_start(freeze, author_start, workers):
    if freeze.get('status')!='YES': raise ValueError('FORMAL_FREEZE_NOT_READY')
    if author_start!='RUN_512_FORMAL_ARMS': raise ValueError('EXPLICIT_AUTHOR_START_REQUIRED')
    if workers!=freeze['workers']: raise ValueError('CONCURRENCY_CHANGED_AFTER_FREEZE')


class IdentityProvider(Provider):
    def __init__(self,config,stop_event=None):
        super().__init__(config); self.stop_event=stop_event
    def drift(self):
        if self.stop_event is not None: self.stop_event.set()
        raise TransportError('DEPLOYMENT_CHANGED')
    def decide(self,*args,**kwargs):
        import subprocess
        if self.stop_event is not None and self.stop_event.is_set(): raise TransportError('COLLECTION_PAUSED')
        if self.config['id']=='A':
            current=subprocess.run(['codex','--version'],capture_output=True,text=True).stdout.strip()
            if current!=self.config['sdk']: self.drift()
        reply=super().decide(*args,**kwargs)
        expected=self.config.get('actual_returned_identifier')
        if expected is not None and reply.get('model')!=expected: self.drift()
        return reply


def collect(freeze_dir,output,author_start,resume=False):
    from run_formal import verify_freeze
    verify_freeze(freeze_dir.parent)
    freeze=json.loads((freeze_dir/'readiness.json').read_text(encoding='utf-8'))
    validate_start(freeze,author_start,2)
    output=Path(output); output.mkdir(parents=True,exist_ok=resume)
    lock_path=output/'COLLECTION.lock'
    # OS-held lock is released automatically on process death; stale files are harmless.
    lock=lock_path.open('a+b'); lock.seek(0); lock.write(b'0'); lock.flush(); lock.seek(0)
    import os
    if os.name=='nt':
        import msvcrt
        msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    else:
        import fcntl
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    try:
        return _collect_locked(freeze_dir,output,freeze,resume)
    finally: lock.close()


def _collect_locked(freeze_dir,output,freeze,resume):
    tasks={t['task_instance_id']:t for t in json.loads((freeze_dir/'formal-task-manifest.json').read_text(encoding='utf-8'))['tasks']}
    assignments=json.loads((freeze_dir/'assignment-manifest.json').read_text(encoding='utf-8'))['pairs']
    configs={c['id']:c for c in json.loads((freeze_dir/'agent-config-manifest.json').read_text(encoding='utf-8'))['configs']}
    status_path=output/'collection-status.json'
    statuses=json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else {}
    if statuses and statuses.get('freeze_id')!=freeze['freeze_id']: raise ValueError('RESUME_FREEZE_CHANGED')
    statuses.setdefault('freeze_id',freeze['freeze_id']); statuses.setdefault('pairs',{})
    mutex=threading.Lock(); paused=threading.Event()
    def save(): durable_json(status_path,statuses)
    def lane(config_id):
        config={**configs[config_id],'freeze_id':freeze['freeze_id']}
        provider=IdentityProvider(config,paused)
        for assignment in [p for p in assignments if p['config_id']==config_id]:
            if paused.is_set(): return
            pair_id=assignment['pair_id']; dest=output/pair_id
            with mutex:
                old=statuses['pairs'].get(pair_id,{})
                if old.get('status')=='terminal':
                    # Failure is terminal too. No selective retries.
                    continue
                statuses['pairs'][pair_id]={'status':'running','assignment':assignment,'started_utc':old.get('started_utc',utc())}; save()
            try:
                result=execute_pair(tasks[assignment['case_id']],provider,dest,assignment['order'],resume=resume and dest.exists())
                errors=[result[p].get('audit_errors',[]) for p in assignment['order']]
                drift=result.get('deployment_changed',False) or any(json.loads(line).get('payload',{}).get('error_code')=='DEPLOYMENT_CHANGED' for file in dest.rglob('events.jsonl') for line in file.read_text(encoding='utf-8').splitlines())
                if drift: paused.set()
                record={'status':'terminal','assignment':assignment,'finished_utc':utc(),'result':result,'audit_errors':errors}
            except Exception as exc:
                # Preserve partial records; unclassifiable arms stay in planned denominator.
                record={'status':'terminal','assignment':assignment,'finished_utc':utc(),
                    'infrastructure_error':type(exc).__name__,'error_code':str(exc)[:150],
                    'result':{p:score_run(dest/p) if (dest/p).exists() else {'task_completion':False,'I':'unknown',
                        'continuity_failure_incidence':None,'terminal':'runtime_error','audit_errors':['arm_not_started']} for p in assignment['order']}}
                paused.set()  # Unexpected design/audit exception requires inspection, never silent skipping.
            with mutex: statuses['pairs'][pair_id]=record; statuses['updated_utc']=utc(); save()
    save()
    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(lane,['A','B']))
    statuses['status']='PAUSED' if paused.is_set() else 'COMPLETE'
    statuses['formal_arms_planned']=512
    statuses['terminal_pairs']=sum(p['status']=='terminal' for p in statuses['pairs'].values())
    save(); return statuses
