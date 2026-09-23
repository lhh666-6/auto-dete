"""Read-only verification and final manifest; does not modify measurements."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent/'dke-experiments'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def main():
    # Trust only the checkout created for this task, for these read-only commands.
    # Do not change the user's global Git configuration.
    git=['git','-c','core.longpaths=true','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO)]
    head=subprocess.check_output(git+['rev-parse','HEAD'],text=True).strip()
    status=subprocess.check_output(git+['status','--porcelain','--untracked-files=no'],text=True)
    assert head=='c6d512843c905cab6d8521dd8c914f7fb26d85ae' and not status
    src=list((REPO/'latest/code/implementation-fixed/app').rglob('*.py'))
    src+=list((REPO/'latest/code/implementation-fixed/benchmarks').glob('*.py'))
    src+=list((REPO/'latest/code/strong-baseline').rglob('*.py'))
    src+=[REPO/'r21-jss/source/performance-experiment/benchmarks/r21_feature_baseline.py']
    reference={'commit':head,'tracked_changes':0,'files':{str(p.relative_to(REPO)):sha(p) for p in src}}
    (ROOT/'source-integrity.json').write_text(json.dumps(reference,indent=2),encoding='utf-8')
    artifacts={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name!='artifact-manifest.json'}
    (ROOT/'artifact-manifest.json').write_text(json.dumps({'all_files_including_databases':True,'files':artifacts},indent=2),encoding='utf-8')
    print(json.dumps({'source_commit':head,'tracked_changes':0,'source_files_hashed':len(src),'artifact_files_hashed':len(artifacts)},indent=2))

if __name__=='__main__':main()
