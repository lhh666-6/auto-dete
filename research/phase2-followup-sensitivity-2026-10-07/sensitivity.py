"""Explicit post-hoc completed-A sensitivity using the untouched frozen exporter.

Routes input paths only: no raw file is replaced, copied over or rescored by a
new oracle. The original 512-arm primary analysis remains a separate artifact.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT.parent / 'agent-policy-phase2-formal-2026-10-07'
RECOVERY = ROOT.parent / 'agent-policy-phase2-quota-recovery-2026-10-07'


class RoutedResults:
    def __init__(self, routes, status_file):
        self.routes, self.status_file = routes, status_file

    def __truediv__(self, key):
        return self.status_file if key == 'collection-status.json' else self.routes[key]


def choose_sources(original_pairs, selected, original_results, followup_results):
    originals = {p['pair_id']: p for p in original_pairs}
    if len(originals) != len(original_pairs):
        raise ValueError('DUPLICATE_ORIGINAL_PAIR')
    routes = {pid: original_results / pid for pid in originals}
    seen = set()
    for row in selected:
        pair = row['pair']; pid = pair['pair_id']
        if pid not in originals or pair['config_id'] != 'A' or originals[pid] != pair:
            raise ValueError('FOLLOWUP_ASSIGNMENT_MISMATCH')
        if pid in seen:
            raise ValueError('DUPLICATE_FOLLOWUP_PAIR')
        seen.add(pid)
        routes[pid] = followup_results / row['attempt']['directory']
    return routes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'outputs')
    args = parser.parse_args()
    sys.path.insert(0, str(ORIGINAL))
    sys.path.insert(0, str(ORIGINAL/'src'))
    sys.path.insert(0, str(ROOT.parent/'phase2-followup-analysis-2026-10-07'))
    from run_formal import verify_freeze
    from analyze import select_attempts
    from phase2.export import export_tables
    verify_freeze(ORIGINAL)
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    manifest = read(RECOVERY/'recovery-manifest.json')
    assert hashlib.sha256((RECOVERY/'recovery-manifest.json').read_bytes()).hexdigest() == (RECOVERY/'recovery-manifest.sha256').read_text().strip()
    original_pairs = read(ORIGINAL/'frozen-formal/assignment-manifest.json')['pairs']
    selections = select_attempts(manifest, read(RECOVERY/'results/collection-status.json'))
    selected = [{'pair': x['assignment'], 'attempt': x['attempt']} for x in selections]
    assert len(original_pairs) == 256 and len(selected) == 117
    original_state = read(ORIGINAL/'formal-results/collection-status.json')
    assert original_state['status'] == 'COMPLETE'
    routes = choose_sources(original_pairs, selected, ORIGINAL/'formal-results', RECOVERY/'results')
    args.output.mkdir(parents=True, exist_ok=False)
    status_path = args.output/'derived-collection-status.json'
    status_path.write_text(json.dumps({'status':'DERIVED_COMPLETE_POSTHOC_VIEW', 'note':'Not the frozen original primary collection; exploratory sensitivity.'}), encoding='utf-8')
    selected_ids = {x['pair']['pair_id'] for x in selected}
    provenance = [{**p, 'source_block':'supplementary_A' if p['pair_id'] in selected_ids else 'original',
                   'relative_source': routes[p['pair_id']].relative_to(ROOT.parent.parent).as_posix()}
                  for p in original_pairs]
    (args.output/'pair-source-map.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    summary = export_tables(ORIGINAL/'frozen-formal', RoutedResults(routes, status_path), args.output/'tables')
    assert summary['planned_arms'] == 512 and summary['paired_units'] == 256
    assert summary['formal_inference_allowed'] is False
    summary['analysis_role'] = 'Exploratory post-hoc completed-A sensitivity; not a replacement for the original primary estimator.'
    summary['source_counts'] = {'original_B_pairs':128, 'original_A_pairs':11, 'supplementary_A_pairs':117}
    summary['selection_rule'] = 'Use the final terminal supplementary attempt for exactly the 117 pre-response quota-selected A pairs; retain every other original pair and all failures.'
    summary['uncertainty_scope'] = 'Original scenario-stratified task-cluster bootstrap applied to a retrospectively assembled view; intervals condition on selected sources and do not remove collection-period effects.'
    (args.output/'analysis-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ['planned_arms','paired_units','formal_inference_allowed','source_counts','effects']}, indent=2))


if __name__ == '__main__': main()
