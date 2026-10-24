"""Regenerate all four manuscript figures without model calls or network access.

python scripts/figures/build_all_figures.py
The compact figure-data.json is a verbatim readback of frozen observations.
Re-extract it in the full repository using the script documented in README.
"""
import json
from pathlib import Path
from statistics import mean, median

def validate_data():
    data=json.loads(Path(__file__).with_name("figure-data.json").read_text(encoding="utf-8"))
    pairs=data["g_pairs"]
    assert len(pairs)==32 and len({(r['cohort'],r['id']) for r in pairs})==32
    assert sum(r["contextU"] for r in pairs)==30
    assert all(r["contextI"]==0 and r["boundU"]==1 and r["boundI"]==1 for r in pairs)
    for s in data["g_summary"]:
        rows=[r for r in pairs if r['cohort']==s['cohort']]
        assert len(rows)==s['pairs_evaluable']
        assert abs(mean(r['calls_delta'] for r in rows)-s['mean_calls_delta'])<1e-10
        assert abs(median(r['seconds_delta'] for r in rows)-s['median_seconds_delta'])<1e-10
        assert all(r['calls_delta']==r['bound_calls']-r['context_calls'] for r in rows)
    assert len(data['x2_routes'])==72
    return data

if __name__ == '__main__':
    validate_data()
    from conceptual_panels import build_gap,build_design_space
    from empirical_panels import build_paired,build_recovery
    build_gap(); build_design_space(); build_paired(); build_recovery()
    from build_binding_matrix import build
    build()
    print("PASS: 32 delivered pairs / 72 X2 routes validated; four figures exported as PDF/SVG/PNG.")
