"""Compare regenerated scientific outputs with the deposited reference values."""
from pathlib import Path
import argparse,csv,json
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def csv_rows(p):
    rows=list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
    for row in rows:
        for k,v in row.items():
            if v and v[0] in '[{':
                try:row[k]=json.loads(v)
                except ValueError:pass
    return rows
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    checks=[]
    def compare(expected,actual,kind='json',drop=()):
        x,y=(csv_rows(expected),csv_rows(actual)) if kind=='csv' else (read(expected),read(actual))
        if drop:x={k:v for k,v in x.items() if k not in drop};y={k:v for k,v in y.items() if k not in drop}
        assert x==y,f'Scientific output mismatch: {actual}'
        checks.append(str(actual.relative_to(a.work)))
    groups=[('revisions/2026-10-07-kais-followup/evidence/online','ase-primary'),('research/phase2-followup-analysis-2026-10-07/outputs','research/phase2-followup-analysis-2026-10-07/ase-reproduction')]
    for old,new in groups:
        compare(a.source/old/'analysis-summary.json',a.work/new/'analysis-summary.json')
        for p in (a.source/old).glob('*.csv'):compare(p,a.work/new/p.name,'csv')
    compare(a.source/'research/phase2-followup-sensitivity-2026-10-07/outputs/analysis-summary.json',a.work/'ase-posthoc/analysis-summary.json')
    for study in ['kais-revision-output-audit-2026-10-14','kais-budget-sensitivity-2026-10-14']:
        base='research/'+study
        compare(a.source/base/'summary.json',a.work/base/'summary.json',drop=('generated_utc',))
        for n in (['cells.csv','pairs.csv'] if 'budget' in study else ['arms.csv','attempts.csv','pairs.csv','invalid-output-arms.csv']):compare(a.source/base/n,a.work/base/n,'csv')
    paper='revisions/2026-10-21-narrative'
    compare(a.source/paper/'tables/recovery-cost-episodes.csv',a.work/'ase-reproduction-results/recovery/recovery-cost-episodes.csv','csv')
    compare(a.source/'revisions/2026-10-18-kais-recalibrated/qa/n-exposure.csv',a.work/'revisions/2026-10-18-kais-recalibrated/qa/n-exposure.csv','csv')
    a.output.write_text(json.dumps({'passed':True,'matched_outputs':checks,'ignored_fields':['budget summary generated_utc only'],'comparison':'JSON values and CSV rows; nested JSON cells decoded'},indent=2),encoding='utf-8')
    print('Matched '+str(len(checks))+' scientific outputs')
if __name__=='__main__':main()
