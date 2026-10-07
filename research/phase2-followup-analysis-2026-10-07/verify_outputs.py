"""Cross-file integration checks and digest inventory of the reviewable package."""
import argparse
from collections import Counter
import csv
import importlib.metadata
import platform
from pathlib import Path
from analyze import ROOT, ORIGINAL, RECOVERY, read, sha, write, include_failure


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=ROOT/'outputs'); args=parser.parse_args()
    out=args.output.resolve()
    if ROOT not in out.parents: raise ValueError('OUTPUT_MUST_STAY_WITHIN_ANALYSIS_PACKAGE')
    summary=read(out/'analysis-summary.json'); scored=read(out/'scored-arms.json'); rows=read(out/'arm-rows.json')
    def table(name): return list(csv.DictReader((out/name).open(encoding='utf-8-sig',newline='')))
    tables={n:table(n) for n in ['table1-outcomes.csv','table2-continuity.csv','table3-recovery.csv','table4-utility-friction.csv','paired-effects.csv','failure-archaeology-all-arms.csv']}
    assert summary['collection_status']=='COMPLETE'
    assert len(rows)==len(scored)==len(tables['table4-utility-friction.csv'])==234
    assert len({r['task_instance_id'] for r in rows})==len(tables['paired-effects.csv'])==117
    assert len(tables['table1-outcomes.csv'])==12 and sum(int(r['planned']) for r in tables['table1-outcomes.csv'])==234
    assert len(tables['failure-archaeology-all-arms.csv'])==sum(include_failure(r['score']) for r in scored)
    assert {(r['pair_id'],r['policy']) for r in tables['failure-archaeology-all-arms.csv']}=={(r['pair_id'],r['policy']) for r in scored if include_failure(r['score'])}
    assert len(tables['table3-recovery.csv'])==sum(len(r['score'].get('episodes',[])) for r in scored)
    assert len(tables['table2-continuity.csv'])==sum(r['score']['transitions'] for r in scored)
    for t in tables['table1-outcomes.csv']:
        group=[r for r in scored if r['policy']==t['policy'] and r['scenario']==t['scenario']]
        assert int(t['task_completion'])==sum(r['score']['task_completion'] for r in group)
        for key,value in [('integrity_1',1),('integrity_0',0),('unknown','unknown')]: assert int(t[key])==sum(r['score']['I']==value for r in group)
    usage=read(out/'native-usage-summary.json'); ledger=read(out/'native-attempt-usage-ledger.json')
    assert not usage['provenance_errors'] and usage['unexpected_native_actions']==0
    assert usage['model_response_events']==sum(r['score']['model_responses'] for r in scored)+sum(r['model_responses'] for r in read(out/'prefix-accounting.json'))
    assert len(ledger)==usage['total']['native_provider_invocations']
    assert all(sha(RECOVERY/'results'/r['raw_path'])==r['sha256'] for r in ledger)
    manifest={'status':'PASS','python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),
              'checks':['all planned rows and policy pairs present','failure membership equals independent scorer including unknowns','episode and transition totals reconcile with scorer','all scenario outcome cells reconcile','native usage/request IDs match every model response','native file digests unchanged'],
              'counts':{name:len(value) for name,value in tables.items()},
              'input_freeze':summary['verification']['parent_freeze_master_sha256'],'input_recovery_manifest':summary['verification']['recovery_manifest_sha256'],
              'source_sha256':{p.name:sha(p) for p in sorted(ROOT.glob('*.py'))},
              'output_sha256':{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='verification.json'}}
    write(out/'verification.json',manifest)
    print('PASS: '+str(manifest['counts']))


if __name__=='__main__': main()
