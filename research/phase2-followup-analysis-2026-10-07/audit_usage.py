"""Account for every native provider attempt, including retained transport retries."""
from collections import Counter, defaultdict
import argparse
import json
from pathlib import Path
from analyze import ROOT, RECOVERY, read, read_events, sha, write


def total(records):
    keys=sorted({k for r in records if isinstance(r,dict) for k,v in r.items() if isinstance(v,(int,float))})
    return {k:sum(r[k] for r in records) if records and all(isinstance(r,dict) and isinstance(r.get(k),(int,float)) for r in records) else None for k in keys}


def unexpected_actions(native):
    # CLI error items are diagnostics; they do not execute tools.
    return [r['item'].get('type') for r in native if r.get('type')=='item.completed'
            and r.get('item',{}).get('type') not in ('agent_message','reasoning','error')]


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=ROOT/'outputs'); args=parser.parse_args()
    out=args.output.resolve()
    if ROOT not in out.parents: raise ValueError('OUTPUT_MUST_STAY_WITHIN_ANALYSIS_PACKAGE')
    out.mkdir(parents=True,exist_ok=True)
    status=read(RECOVERY/'results/collection-status.json'); rows=[]; identities=Counter(); error_codes=Counter(); phases=defaultdict(list)
    provenance_errors=[]; response_count=0; expected_raw=set(); native_files=set()
    for pair_id,record in status['pairs'].items():
        for attempt in record['attempts']:
            directory=RECOVERY/'results'/attempt['directory']
            for phase in ['prefix','context','bound']:
                arm=directory/phase; events=read_events(arm); mapping={}
                for e in events:
                    p=e['payload']
                    if e['event_type']=='model_error' and p.get('error_code'): error_codes[p['error_code']]+=1
                    if e['event_type']!='model_response': continue
                    response_count+=1
                    refs=[r for r in e['artifacts'] if r['relative_path'].endswith('stdout.jsonl')]
                    if len(refs)!=1: provenance_errors.append(e['event_id']+':raw_stdout_reference_count'); continue
                    f=(arm/refs[0]['relative_path']).resolve(); expected_raw.add(f)
                    if f in mapping: provenance_errors.append(e['event_id']+':duplicate_native_response_reference')
                    mapping[f]=e
                    identities[json.dumps({k:p.get(k) for k in ('requested_model','returned_model','returned_revision')},sort_keys=True)]+=1
                for f in sorted((arm/'provider-raw').glob('*/stdout.jsonl')):
                    native_files.add(f.resolve()); native=[]; invalid=[]
                    for i,line in enumerate(f.read_text(encoding='utf-8').splitlines()):
                        if not line.strip(): continue
                        try: native.append(json.loads(line))
                        except ValueError: invalid.append(i+1)
                    completions=[e for e in native if e.get('type')=='turn.completed']; e=mapping.get(f.resolve())
                    if e:
                        returned=next((r.get('usage',{}) for r in reversed(native) if r.get('type')=='turn.completed'),{})
                        if returned!=e['payload']['usage']: provenance_errors.append(e['event_id']+':native_usage_mismatch')
                        thread=next((r.get('thread_id') for r in native if r.get('type')=='thread.started'),None)
                        if thread!=e['payload']['provider_request_id']: provenance_errors.append(e['event_id']+':native_request_id_mismatch')
                    native_actions=unexpected_actions(native)
                    row={'pair_id':pair_id,'attempt_directory':attempt['directory'],'phase':phase,'raw_path':f.relative_to(RECOVERY/'results').as_posix(),
                        'sha256':sha(f),'maps_to_model_response':e is not None,'model_response_event_id':e['event_id'] if e else None,
                        'native_turn_completed_records':len(completions),'native_usage_records':[r.get('usage') for r in completions],
                        'native_error_types':dict(Counter(r.get('type') for r in native if r.get('type') in ('error','turn.failed'))),
                        'unexpected_native_actions':native_actions,'native_diagnostic_error_items':sum(r.get('type')=='item.completed' and r.get('item',{}).get('type')=='error' for r in native),'unparseable_line_numbers':invalid}
                    rows.append(row); phases[phase].append(row)
    for missing in expected_raw-native_files: provenance_errors.append(str(missing)+':referenced_stdout_missing')
    def rollup(group):
        usages=[u for r in group for u in r['native_usage_records']]
        return {'native_provider_invocations':len(group),'mapped_model_responses':sum(r['maps_to_model_response'] for r in group),
                'native_turn_completed_records':len(usages),'unmapped_invocations':sum(not r['maps_to_model_response'] for r in group),
                'invocations_without_completed_usage':sum(not r['native_usage_records'] for r in group),'observed_completed_usage_totals':total(usages),
                'all_invocation_usage_complete':all(r['native_usage_records'] for r in group)}
    summary={'scope':'All retained pair attempts and native transport attempts; prefix counted once per attempt.',
             'model_response_events':response_count,'provenance_errors':provenance_errors,'by_phase':{p:rollup(g) for p,g in phases.items()},
             'total':rollup(rows),'model_request_error_codes':dict(error_codes),
             'returned_identity':[dict(json.loads(k),responses=v) for k,v in identities.items()],
             'unexpected_native_actions':sum(len(r['unexpected_native_actions']) for r in rows),
             'incomplete_raw_jsonl_files':sum(bool(r['unparseable_line_numbers']) for r in rows),
             'usage_caveat':'Totals cover observed native turn.completed usage only. Missing usage for failed attempts is unknown; totals are not complete billable usage and are not monetary cost.'}
    write(out/'native-attempt-usage-ledger.json',rows); write(out/'native-usage-summary.json',summary)
    if provenance_errors: raise ValueError('NATIVE_USAGE_PROVENANCE_ERRORS:'+str(provenance_errors))
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__': main()
