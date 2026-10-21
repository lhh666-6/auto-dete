"""Portable readback of saved later evidence. Frozen scorer bytes are unchanged.

For ToolGate only, translate source paths in the in-memory freeze document.
Authenticate each mapped file first; never rewrite deposited freezes or outcomes.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    mapping=read(ROOT/'reproduction/ase/path-map.json')
    for old,item in mapping.items():assert sha(ROOT/item['path'])==item['sha256'],item['path']
    result={'frozen_path_hashes':len(mapping),'source_files_modified':False,'new_experiments':False}
    p=ROOT/'research/kais-toolgate-public-reference-2026-10-20'
    m=module(p/'public_score.py','public_scoring');original_read=m.read
    def relocated_read(path):
        obj=original_read(path)
        if Path(path).name=='freeze.json':
            for group in ('files','protected_files'):
                for item in obj.get(group,[]):
                    entry=mapping[item['path'].replace('\\','/')]
                    assert entry['sha256']==item['sha256']
                    item['path']=str(ROOT/entry['path'])
        return obj
    m.read=relocated_read
    run=p/'runs/20261020T123319655459Z';rows,summary=m.score_run(run);saved=read(run/'SCORE.json')
    assert not summary['integrity_errors'],summary['integrity_errors']
    assert {k:v for k,v in summary.items() if k!='source_sha256'}=={k:v for k,v in saved.items() if k!='source_sha256'}
    assert sorted(summary['source_sha256'].values())==sorted(saved['source_sha256'].values())
    bad=[r for r in rows if r['status']!='PASS']
    assert len(bad)==1 and bad[0]['status']=='FAIL' and 'unexpected upstream diagnostic output' in bad[0]['errors'],bad
    result['public_toolgate']={'recomputed_matches_frozen':True,'by_method':summary['by_method'],'retained_failure':bad}
    p=ROOT/'research/kais-toolgate-feasibility-2026-10-20'
    m=module(p/'score_feasibility.py','feasibility_scoring');rows,summary=m.score_run(p/'runs/20261020T121403449662Z')
    assert summary==read(p/'runs/20261020T121403449662Z/SCORE.json')
    result['toolgate_development']={'recomputed_matches_frozen':True,'by_method':summary['by_method']}
    p=ROOT/'research/kais-commit-uncertainty-2026-10-14';m=module(p/'verify_outputs.py','uncertainty_scoring')
    for item in read(p/'freeze.json')['inputs']:assert sha(p/item['path'])==item['sha256']
    for item in read(p/'inputs.json')['files']:assert sha(ROOT/item['original'])==sha(p/item['copy'])==item['sha256']
    counts={n:m.audit_run(n) for n in ['initial','rebuild']}
    assert counts==read(p/'verification.json')['raw_audit']
    assert read(p/'runs/initial/normalized_summary.json')==read(p/'runs/rebuild/normalized_summary.json')
    result['uncertain_commit']={'recomputed_matches_frozen':True,'runs':counts}
    p=ROOT/'research/kais-approval-workflow-2026-10-14';m=module(p/'run_workflow.py','tofu_normalization')
    summaries=[]
    for run in sorted((p/'runs').iterdir()):
        if not (run/'results.json').is_file():continue
        raw=read(run/'results.json');normalized={group:[m.normalize(r) for r in raw[group]] for group in ['main','controls']}
        assert normalized==read(run/'normalized_summary.json')
        for group in ['main','controls']:
            for row in raw[group]:assert row==read(run/row['record_directory']/'result.json')
        assert len(raw['main'])==24 and len(raw['controls'])==8
        assert all(r['status']=='pass' and all(r['checks'].values()) for group in raw.values() for r in group)
        summaries.append(normalized)
    assert len(summaries)==2 and summaries[0]==summaries[1]
    result['opentofu']={'saved_rows_and_normalization_match':True,'runs':2,'records_per_run':32,'native_cli_rerun':False}
    result['passed']=True
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'passed':True,'toolgate_failure_retained':len(bad),'opentofu_runs_checked':2}))
if __name__=='__main__':main()
