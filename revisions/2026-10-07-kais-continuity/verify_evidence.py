"""Verify the complete data-to-manuscript aggregation and archived check receipts."""
from pathlib import Path
from collections import Counter
import csv,json,subprocess,hashlib,re

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
OUT=ROOT/'evidence/online'
def read(name):
    with (OUT/name).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
counts=read('table1-outcomes.csv');ep=read('table3-recovery.csv');trans=read('table2-continuity.csv')
friction=read('table4-utility-friction.csv');fail=read('failure-archaeology-all-arms.csv')
agg=json.loads((OUT/'manuscript-aggregates.json').read_text(encoding='utf-8'))
checks={}
checks['planned_ledger']=sum(int(r['planned']) for r in counts)==512 and len(friction)==512
checks['unique_arms']=len(set((r['pair_id'],r['policy']) for r in friction))==512
checks['task_clusters']=len(set(r['task_instance_id'] for r in friction))==128
checks['outcome_partition']=all(sum(int(r[k]) for k in ('integrity_1','integrity_0','unknown'))==int(r['planned']) for r in counts)
checks['all_failure_arms']=len(fail)==273 and len(set((r['pair_id'],r['policy']) for r in fail))==273
checks['unknowns_retained']=sum(r['I']=='unknown' for r in fail)==2
checks['feedback_episodes']=len(ep)==99 and sum(r['config_id']=='B' for r in ep)==93
checks['recoverability']=all(r['Delivered']=='True' and r['RecoverableReject']=='True' for r in ep)
g=[r for r in ep if r['scenario']=='G']
checks['G_feedback']=len(g)==17 and all(r['policy']=='bound' and r['U']=='True' and r['I']=='1' for r in g)
checks['G_recovery_strategies']=Counter(r['recovery_strategy'] for r in g)=={'reuse-reviewed':16,'reauthorization':1}
checks['N_no_feedback']=not any(r['scenario']=='N' for r in ep)
checks['transitions']=len(trans)==261
subs=[r for r in trans if r['executed_substitution']=='True']
checks['substitutions']=len(subs)==17 and all(r['policy']=='context' and r['scenario']=='G' and r['policy_admissible']=='True' and r['A_instance_compatible']=='False' for r in subs)
checks['substitution_sources']=all(r['source_provenance_integrity']=='True' and r['copy_forward']=='True' for r in subs)
checks['N_exact_transitions']=Counter((r['config_id'],r['policy']) for r in trans if r['scenario']=='N')=={('A','context'):3,('A','bound'):3,('B','context'):30,('B','bound'):30} and all(r['same_instance']=='True' for r in trans if r['scenario']=='N')
checks['checkpoint_coverage']=agg['checkpoint_pairs']=={'A':11,'B':128}
checks['raw_usage_limit']=agg['raw_provider_error_counts']['A']=={'usage_limit':357}
checks['joint_cells']=all(sum(v['joint'].values())==128 for v in agg['groups'].values())
checks['joint_total_completion']=sum(v['U'] for k,v in agg['groups'].items() if k.endswith('context'))==126 and sum(v['U'] for k,v in agg['groups'].items() if k.endswith('bound'))==128
source_manifest=json.loads((ROOT/'evidence/source-manifest.json').read_text(encoding='utf-8'))
checks['baseline_and_controlled_hashes']=all(hashlib.sha256((ROOT/path.replace('\\', '/')).read_bytes()).hexdigest()==expected for path,expected in source_manifest['files'].items())
chains=[json.loads(x) for x in (REPO/'research/authorization-granularity-phase1-2026-10-06/correction-chains.jsonl').read_text(encoding='utf-8').splitlines()]
checks['historical_84_chains']=len(chains)==84 and all(not r['failures'] for r in chains)
checks['historical_associations']=sum(r['metrics']['evidence_checks'] for r in chains)==252 and sum(r['metrics']['record_versions_checked'] for r in chains)==168 and sum(r['metrics']['P6_traces_checked'] for r in chains)==168
commit='c6d512843c905cab6d8521dd8c914f7fb26d85ae'
base='latest/code/implementation-fixed/conformance/raw-results/formal-refinement-r2-v1/'
dest=ROOT/'evidence/formal/projection-receipts';dest.mkdir(exist_ok=True)
receipt_manifest=ROOT/'evidence/formal/projection-receipts.json'
if receipt_manifest.exists():
    # Standalone artifact inspection does not require the original Git objects.
    records=json.loads(receipt_manifest.read_text(encoding='utf-8'))
    for record in records:
        assert record['path'].startswith(base)
        name=record['path'][len(base):].replace('/','__')
        raw=(dest/name).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==record['sha256']
        assert json.loads(raw.decode('utf-8-sig'))==record['receipt']
else:
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,base],cwd=REPO,text=True).splitlines()
    receipts=[p for p in paths if p.endswith('alloy-result/receipt.json')]
    records=[]
    for path in receipts:
        raw=subprocess.check_output(['git','show',commit+':'+path],cwd=REPO)
        obj=json.loads(raw.decode('utf-8-sig'))
        name=path[len(base):].replace('/','__')
        (dest/name).write_bytes(raw)
        records.append({'path':path,'sha256':hashlib.sha256(raw).hexdigest(),'receipt':obj})
    receipt_manifest.write_text(json.dumps(records,indent=2),encoding='utf-8')
projection_outcomes=Counter()
for r in records:
    sat=any(s.get('instances') for c in r['receipt']['commands'].values() for s in c.get('solution',[]))
    projection_outcomes['mutant_SAT' if sat and '/mutants/' in r['path'] else 'mutant_UNSAT' if '/mutants/' in r['path'] else 'intended_SAT' if sat else 'intended_UNSAT']+=1
checks['projection_receipts']=projection_outcomes=={'intended_SAT':9,'mutant_UNSAT':20}
commands=json.loads((ROOT/'evidence/formal/command_results.json').read_text(encoding='utf-8-sig'))
checks['bounded_commands']=len(commands)==72 and all(r['status']=='PASS' and r['expected']==r['actual'] for r in commands)
main=(ROOT/'main.tex').read_text(encoding='utf-8')
keys=set(re.findall(r'\\bibitem\{([^}]+)\}',main))
cited=set(k.strip() for block in re.findall(r'\\cite\w*\{([^}]+)\}',main) for k in block.split(','))
checks['citations_resolve']=keys==cited and len(keys)==17
checks['nine_sections']=len(re.findall(r'\\section\{',main))==9
checks['no_draft_placeholders']=not re.search(r'\\pending|TODO|TBD|awaiting final|working.draft|completed.data subsection',main,re.I)
abstract=main.split(r'\begin{abstract}',1)[1].split(r'\end{abstract}',1)[0]
abstract_words=len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*",abstract))
checks['abstract_length']=150<=abstract_words<=250
checks['six_keywords']=main.split(r'\textbf{Keywords:}',1)[1].split('\n')[0].count(';')==5
report={'checks':checks,'all_pass':all(checks.values()),'abstract_words':abstract_words,'projection_receipt_count':len(records),
    'projection_outcomes':dict(projection_outcomes),
    'alloy_outcomes':dict(Counter(r['actual'] for r in commands)),
    'coverage_note':'Exporter freshly rescored every planned arm. This audit checks derived counts, not model generalization or natural prevalence.'}
(ROOT/'evidence/final-number-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
if not report['all_pass']:raise SystemExit(1)
