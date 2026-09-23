"""Check that expected rejections were not arbitrary programming errors."""
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def rows(path):return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines()]
def main():
    e1=rows(ROOT/'results/e1/receipts.jsonl');e2=rows(ROOT/'results/e2/browser-observations.jsonl')
    counts=Counter()
    for r in e1:
        assert not r['harness_error']
        if not r['accepted']:counts[('E1',r['arm'],r['case'],r['error'])]+=1
    for r in e2:
        assert not r['harness_error']
        if not r['response']['accepted']:counts[('E2',r['mode'],r['case'],r['response']['error'])]+=1
    result=[dict(zip(['experiment','arm','case','error'],key))|{'count':n} for key,n in sorted(counts.items())]
    for r in result:
        case,arm,error=r['case'],r['arm'],r['error']
        if case.startswith('rollback'):
            point='before_commit' if case=='rollback' else case.removeprefix('rollback_')
            expected='RuntimeError: INJECTED:'+point
        elif r['experiment']=='E1':
            if case in ['stale','replay']:
                expected='ValueError: '+('STALE_OR_CONFLICT' if arm=='reference' else 'STALE_OR_REPLAY')
            elif arm=='reference':
                kind='authorized value' if case=='wrong_authorized_value' else 'certificate'
                expected='ValueError: invalid fact admission bundle: binding/transition '+kind+' mismatch for FORM-1:2:quantity'
            else:
                expected='ValueError: '+{'different_evidence_substitution':'REVIEW_CONTEXT_MISMATCH','same_value_substitution':'REVIEWED_INSTANCE_MISMATCH','wrong_authorized_value':'AUTHORIZED_VALUE_MISMATCH'}[case]
        elif case=='stale' or (case=='replay' and arm=='original_confirm'):
            expected='ConcurrentReviewError: Expected version 1, current is 2'
        else:
            expected='ValueError: SESSION_AUTHORIZATION_MISMATCH'
        assert error==expected,(r,expected)
    (ROOT/'rejection-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'groups':len(result),'rejections_checked':sum(r['count'] for r in result),'exact_expected_reasons':True},indent=2))
if __name__=='__main__':main()
