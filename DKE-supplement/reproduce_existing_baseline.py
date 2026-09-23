"""Untimed continuity check of the paper's original strengthened baseline."""
import json
import sys
from common import ROOT, REPO, write_json
sys.path.insert(0,str(REPO/'latest/code/strong-baseline'))
from strong_baseline import cases
from strong_baseline.policies import POLICY_B1, POLICY_FULL

def main():
    out=ROOT/'results/original-baseline-continuity';out.mkdir(exist_ok=False)
    summary={}
    for name,policy in [('B1',POLICY_B1),('Full',POLICY_FULL)]:
        runs,databases=cases.run_all_cases(policy,out/name)
        comparison=cases.compare_with_reference(runs)
        summary[name]={'runs':len(runs),'comparison':comparison}
        write_json(out/(name+'-runs.json'),runs)
    write_json(out/'summary.json',summary)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
