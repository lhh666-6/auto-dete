"""Prepare and check the ASE deposit using archived data; never starts model collection."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,zipfile

REPO=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
PAPER='revisions/2026-10-21-narrative'
RAW={
 'cloud-handoff/replication-package.zip':'1bc17338d18f198811e0e58eca9b64bded29f9b01cd61558862455e7e0d469d8',
 'research/phase2-results-snapshots/2026-10-07-complete/quota-recovery-complete.zip':'536f8b7d784d1af118145affd90c3d613b67ad44d9c5b3607b463bcebeacbec1'}
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def check():
    records=read(HERE/'MANIFEST.json')['files']
    for rel,want in {**{i['path']:i['sha256'] for i in records},**RAW}.items():
        p=REPO/rel
        if not p.is_file() or digest(p)!=want:raise ValueError('Missing/changed input: '+rel)
    print(json.dumps({'passed':True,'manifest_files':len(records),'original_archives':len(RAW)}),flush=True)
def extract(archive,root):
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            dest=(root/item.filename).resolve()
            if not dest.is_relative_to(root.resolve()):raise ValueError('Archive path escapes output')
            if item.is_dir():dest.mkdir(parents=True,exist_ok=True);continue
            data=z.read(item)
            if dest.exists():
                if dest.read_bytes()!=data:raise ValueError('Conflicting archive input: '+str(dest))
            else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
def prepare(work):
    check()
    if work.exists() or work.is_relative_to(REPO):raise ValueError('Choose a NEW directory outside the repository')
    work.mkdir(parents=True)
    for rel in RAW:extract(REPO/rel,work)
    # Original archive member layout is also the source ledger used by recovery readbacks.
    for rel in RAW:
        dest=work/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(REPO/rel,dest)
    original=work/'revisions/2026-10-07-kais-continuity/replication-package.zip'
    original.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(REPO/'cloud-handoff/replication-package.zip',original)
    for name in ['research/phase2-followup-analysis-2026-10-07','research/phase2-followup-sensitivity-2026-10-07']:
        shutil.copytree(REPO/name,work/name,dirs_exist_ok=True)
    for item in read(HERE/'MANIFEST.json')['files']:
        rel=item['path'];dest=work/rel
        if dest.exists() and digest(dest)==item['sha256']:continue
        if dest.exists():raise ValueError('Curated input conflicts with original archive: '+rel)
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(REPO/rel,dest)
    extract(work/PAPER/'X1-X2-reproduction.zip',work/'ase-x1-x2')
    (work/'ASE-WORKSPACE.json').write_text(json.dumps({'source':str(REPO),'manifest_sha256':digest(HERE/'MANIFEST.json'),'mode':'disposable offline reanalysis'},indent=2))
    print('Prepared '+str(work),flush=True)
def run(work):
    if not (work/'ASE-WORKSPACE.json').is_file():raise ValueError('Run prepare first')
    check()
    if read(work/'ASE-WORKSPACE.json')['manifest_sha256']!=digest(HERE/'MANIFEST.json'):
        raise ValueError('Deposit changed after preparation; prepare a fresh workspace')
    receipts=work/'ase-reproduction-results';receipts.mkdir(exist_ok=False)
    cmds=[
      ('original-readiness',['research/agent-policy-phase2-formal-2026-10-07/run_formal.py','--verify-only']),
      ('original-analysis',['research/agent-policy-phase2-formal-2026-10-07/analyze_formal.py','--output','ase-primary']),
      ('supplementary-analysis',['research/phase2-followup-analysis-2026-10-07/analyze.py','--output','research/phase2-followup-analysis-2026-10-07/ase-reproduction']),
      ('supplementary-usage',['research/phase2-followup-analysis-2026-10-07/audit_usage.py','--output','research/phase2-followup-analysis-2026-10-07/ase-reproduction']),
      ('supplementary-verify',['research/phase2-followup-analysis-2026-10-07/verify_outputs.py','--output','research/phase2-followup-analysis-2026-10-07/ase-reproduction']),
      ('posthoc-sensitivity',['research/phase2-followup-sensitivity-2026-10-07/sensitivity.py','--output','ase-posthoc']),
      ('recovery',[PAPER+'/qa/recovery_costs.py','--repository-root',str(work),'--output',str(receipts/'recovery')]),
      ('recovery-example',[PAPER+'/qa/recovery_example.py','--repository-root',str(work),'--output',str(receipts/'recovery')]),
      ('x1-x2-saved',['ase-x1-x2/x1-x2/verify_saved.py']),
      ('truncation',['research/kais-revision-output-audit-2026-10-14/analysis.py']),
      ('budget-sensitivity',['research/kais-budget-sensitivity-2026-10-14/analysis.py']),
      ('later-evidence',['reproduction/ase/check_later.py','--output',str(receipts/'later-evidence.json')]),
      ('n-exposure',['revisions/2026-10-18-kais-recalibrated/qa/n_exposure.py']),
      ('compare',['reproduction/ase/compare_outputs.py','--source',str(REPO),'--work',str(work),'--output',str(receipts/'comparisons.json')]),
    ]
    results=[]
    for name,args in cmds:
        print('Running '+name,flush=True)
        env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONUTF8']='1'
        with (receipts/(name+'.log')).open('wb') as log:
            p=subprocess.run([sys.executable,'-B',*args],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT)
        results.append({'step':name,'exit_code':p.returncode,'log':name+'.log'})
        (receipts/'RUN.json').write_text(json.dumps({'passed':len(results)==len(cmds) and all(x['exit_code']==0 for x in results),'completed_steps':len(results),'planned_steps':len(cmds),'steps':results,'python':sys.version,'platform':sys.platform,'source_manifest_sha256':digest(HERE/'MANIFEST.json')},indent=2))
        if p.returncode:raise RuntimeError('Failed '+name+'; see '+str(receipts/(name+'.log')))
    check()
    print('All offline steps passed; see '+str(receipts/'RUN.json'),flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('command',choices=['verify','prepare','run']);ap.add_argument('--work',type=Path)
    args=ap.parse_args()
    if args.command=='verify':check()
    else:
        if args.work is None:ap.error('--work is required')
        {'prepare':prepare,'run':run}[args.command](args.work.resolve())
