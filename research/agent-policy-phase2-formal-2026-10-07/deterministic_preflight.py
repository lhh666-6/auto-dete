"""Reproduce all 128 rendered host fixtures without any network/model call."""
import json, sys, tempfile, zipfile, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from phase2.kernel import canonical,utc
from phase2.generator import generate_tasks,COUNTS
from phase2.preflight import DeterministicAgent
from phase2.runner import execute_pair,validate_run

def run(destination):
    destination.mkdir(parents=True,exist_ok=False)
    records=[]
    with tempfile.TemporaryDirectory(prefix='phase2-host-preflight-') as temp:
        base=Path(temp)
        for case in generate_tasks():
            directory=base/case['task_instance_id']
            result=execute_pair(case,DeterministicAgent(),directory,['context','bound'])
            for policy in ['context','bound']:
                score=result[policy]; audit=validate_run(directory/policy)
                expected=0 if case['scenario']=='G' and policy=='context' else 1
                if not score['task_completion'] or score['I']!=expected or audit['errors'] or audit['violations']:
                    raise AssertionError((case['task_instance_id'],policy,score))
            records.append({'task_instance_id':case['task_instance_id'],'scenario':case['scenario'],
                'input_sha256':case['input_sha256'],'checkpoint_hashes':result['checkpoint_hashes'],
                'results':{p:result[p] for p in ['context','bound']},'online_model_calls':0})
        with zipfile.ZipFile(destination/'deterministic-traces.zip','x',compression=zipfile.ZIP_DEFLATED) as archive:
            for file in base.rglob('*'):
                if file.is_file(): archive.write(file,file.relative_to(base).as_posix())
    summary={'status':'PASS','timestamp_utc':utc(),'task_instances':128,'host_pairs':128,
        'engineering_policy_arms':256,'formal_online_arms':0,'online_model_calls':0,'scenario_counts':COUNTS,
        'records':records,'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(list((ROOT/'src').rglob('*.py'))+list((ROOT/'tests').rglob('*.py'))+list(ROOT.glob('*.py')))},'trace_archive_sha256':hashlib.sha256((destination/'deterministic-traces.zip').read_bytes()).hexdigest()}
    (destination/'deterministic-fixture-results.json').write_text(canonical(summary),encoding='utf-8')
    return summary

if __name__=='__main__':
    destination=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'preflight/deterministic-all-128'
    result=run(destination)
    print(canonical({k:v for k,v in result.items() if k!='records'}))
