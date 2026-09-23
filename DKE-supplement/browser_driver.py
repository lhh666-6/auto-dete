"""Independent DOM observer and scripted user of the local fixture."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

CASES=['accept','correction','reselect','request_substitution','value_substitution','principal_substitution','stale','replay','rollback','dom_only_substitution']
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def run(base,out,limit):
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
        page=browser.new_page(viewport={'width':1280,'height':850})
        def post(path,data):
            r=page.request.post(base+path,data=data).json()
            assert not r.get('harness_error'),r
            return r
        samples=[('integer',100),('decimal',2.5),('boolean',True)]
        if limit:samples=samples[:1]
        for label,value in samples:
            for mode in ['original_confirm','session_gate']:
                for case in CASES:
                    row={'label':label,'mode':mode,'case':case}
                    try:
                        ids=post('/setup',row|{'value':value})
                        page.goto(base);page.wait_for_function('window.ready===true')
                        if case=='reselect':page.evaluate("async()=>{await window.selectCandidate('B')}")
                        if case=='dom_only_substitution':
                            page.locator('#candidate').evaluate('(el,id)=>el.textContent=id',ids['B'])
                        if case=='correction':page.locator('#value').fill(canonical({'corrected':value}))
                        observed={'candidate':page.locator('#candidate').inner_text(),
                            'proposal':json.loads(page.locator('#proposal').inner_text()),
                            'authorized':json.loads(page.locator('#value').input_value()),'actor':'reviewer'}
                        # These observations are taken from the DOM before clicking, not from the server's labels.
                        page.locator('#authorize').click();page.wait_for_function("window.last && window.last.phase==='authorized'")
                        if case=='request_substitution':page.evaluate('(id)=>window.client.candidate=id',ids['B'])
                        if case=='value_substitution':page.evaluate("()=>window.client.value={unauthorized:1}")
                        if case=='principal_substitution':page.evaluate("()=>window.client.actor='reviewer-2'")
                        if case=='stale':post('/perturb',{})
                        page.evaluate('()=>window.last=null');page.locator('#confirm').click();page.wait_for_function('window.last && window.last.accepted!==undefined')
                        response=page.evaluate('window.last')
                        if case=='replay':
                            row['first_confirmation']=response
                            page.evaluate('()=>window.last=null');page.locator('#confirm').click();page.wait_for_function('window.last && window.last.accepted!==undefined')
                            response=page.evaluate('window.last')
                        q=response['query'].get('quantity',{})
                        violations=[]
                        if response['accepted']:
                            if q.get('reviewed_candidates')!=[observed['candidate']]:violations.append('displayed_candidate')
                            if canonical(q.get('authorized'))!=canonical(observed['authorized']):violations.append('authorized_value')
                            if q.get('reviewer')!=observed['actor']:violations.append('reviewer')
                        row.update({'observed_dom':observed,'response':response,'review_mismatches':violations,'harness_error':None})
                        if label=='integer' and case in ['correction','dom_only_substitution']:
                            page.screenshot(path=str(out/(mode+'-'+case+'.png')),full_page=True)
                    except Exception as exc:row['harness_error']=repr(exc)
                    results.append(row)
                    with (out/'browser-observations.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row)+'\n')
                    print('E2',label,mode,case,'ERROR' if row['harness_error'] else ('accepted' if row['response']['accepted'] else 'rejected'),flush=True)
        (out/'browser-environment.json').write_text(json.dumps({'browser_version':browser.version,'driver':'Playwright','automated_not_human':True},indent=2))
        browser.close()
    summary=[]
    for mode in ['original_confirm','session_gate']:
        rows=[r for r in results if r['mode']==mode];scored=[r for r in rows if not r['harness_error']]
        summary.append({'mode':mode,'planned':len(rows),'scored':len(scored),'harness_errors':len(rows)-len(scored),
            'accepted':sum(r['response']['accepted'] for r in scored),'review_mismatch_cases':sum(bool(r['review_mismatches']) for r in scored),
            'rejections_with_writes':sum(not r['response']['accepted'] and not r['response']['zero_write_on_reject'] for r in scored),
            'cases':[{k:r[k] for k in ['label','case','review_mismatches']}|{'accepted':r['response']['accepted']} for r in scored]})
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--limit',action='store_true');a=p.parse_args();run(a.base,a.output,a.limit)
