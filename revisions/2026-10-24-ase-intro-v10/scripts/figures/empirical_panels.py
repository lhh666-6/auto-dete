"""G protocol and all delivered-pair outcomes, read from frozen figure data.

This module owns only the paired-intervention and recovery figures/captions.
The shared figure_style module supplies the requested 8 pt typography baseline,
white structural shapes, font embedding and fixed 150 mm exports. It is not
modified here. No experiment, model call, resampling or simulated row is used.

Asset scan: SankeyDiagram produces multi-stage volume flows and PairedBoxScatter
produces distributions with boxes; neither represents this protocol or a complete
binary pair ledger. These panels inherit the project's approved ASE structural
style through figure_style, retaining editable vector text and 300 dpi previews.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import statistics
import matplotlib as mpl

from matplotlib.patches import Rectangle, Circle
from paper_objects import candidate, grant, gate, band, CONTEXT, INSTANCE, CONTEXT_TINT, INSTANCE_TINT

from figure_style import (
    BLUE, GREEN, INK, MUTED, PURPLE, RED, FIGURES,
    canvas, flow, node, panel, record, save_fixed, text,
)

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "figure-data.json"
COHORTS = [
    ("original_B", "Original B", 16),
    ("supplementary_A", "Supplementary A", 15),
    ("original_A", "Original A", 1),
]


def _read_data():
    raw = DATA_PATH.read_bytes()
    data = json.loads(raw)
    pairs = data["g_pairs"]
    assert len(pairs) == 32
    assert len({(r["collection"], r["id"]) for r in pairs}) == 32
    assert len({r["case_id"] for r in pairs}) == 16
    assert not data["g_unknown_or_unmatched_in_selected_32"]
    assert sum(r["contextU"] for r in pairs) == 30
    for r in pairs:
        assert r["contextU"] in (0, 1) and r["contextI"] == 0
        assert r["boundU"] == 1 and r["boundI"] == 1
        assert r["recovery_path"] in ("reuse-reviewed", "reauthorization")
        assert r["bound_delivered_recoverable"] == 1
        assert r["calls_delta"] == r["bound_calls"] - r["context_calls"]
        assert abs(r["seconds_delta"] - (r["bound_elapsed_ms"] - r["context_elapsed_ms"]) / 1000) < 1e-10
    groups = {}
    for cohort, _, expected_n in COHORTS:
        rows = sorted((r for r in pairs if r["cohort"] == cohort), key=lambda r: r["case_id"])
        assert len(rows) == expected_n
        groups[cohort] = rows
    return data, groups, hashlib.sha256(raw).hexdigest()


def _caption(name, caption, label):
    if name == "fig4-paired-intervention":
        caption += " Object glyphs were AI-generated; see the AI-assisted preparation declaration."
    (FIGURES / (name + ".tex")).write_text(
        "\\begin{figure}[tbp]\n\\centering\n"
        + "\\makebox[\\textwidth][c]{\\includegraphics[width=150mm]{figures/" + name + ".pdf}}\n"
        + "\\caption{" + caption + "}\n\\label{" + label + "}\n\\end{figure}\n",
        encoding="utf-8",
    )


def _text_qa(fig):
    """Check actual rendered text boxes, in addition to shared artboard QA."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    labels = [t for ax in fig.axes for t in ax.texts if t.get_text()]
    boxes = [(t, t.get_window_extent(renderer)) for t in labels]
    collisions = []
    for i, (left, a) in enumerate(boxes):
        for right, b in boxes[i + 1:]:
            overlap_x = min(a.x1, b.x1) - max(a.x0, b.x0)
            overlap_y = min(a.y1, b.y1) - max(a.y0, b.y0)
            if overlap_x > .25 and overlap_y > .25:
                collisions.append([left.get_text(), right.get_text()])
    if collisions:
        raise ValueError(f"Overlapping labels: {collisions}")
    minimum = min(t.get_fontsize() for t in labels)
    assert minimum >= 7.5
    return {"text_artists": len(labels), "text_collisions": collisions,
            "minimum_master_font_pt": minimum,
            "minimum_final_font_pt": minimum}


def build_paired():
    """Draw only G: shared review copied into two isolated policy swimlanes."""
    _, groups, source_hash = _read_data()
    fig, ax = canvas(106)
    text(ax,7,102,"Shared prospective review",size=8.5,ha='left')
    mpl.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial',
                         'mathtext.it': 'Arial:italic'})
    candidate(ax,7,84,'c1',lines=('context K',r'proposal $x_c$'))
    grant(ax,44,86.1,'a1 → c1',width=33)
    ax.plot([41,45],[90,90],color=INK,lw=.6)
    flow(ax,[(78,90),(100,90)])
    text(ax,89,95,'save',size=7.5,color=MUTED)
    ax.add_patch(Rectangle((101,82),43,16,facecolor='white',edgecolor=INK,lw=.7))
    ax.add_patch(Rectangle((101,93),43,5,facecolor='#F4F0E6',edgecolor=INK,lw=.5))
    text(ax,122.5,95.5,'Checkpoint',size=8.5)
    text(ax,122.5,87.5,'conversation + state',size=7.5)

    # A single saved checkpoint is copied into isolated arms. The neutral trunk
    # is not a policy path or a transition from one arm to the other.
    ax.plot([122.5,122.5,3,3],[82,77,77,20],color=INK,lw=.65)
    ax.plot([3],[50],marker='o',markersize=2.3,color=INK)
    for cy in (50,20):
        flow(ax,[(3,cy),(8,cy)])
    text(ax,70,79.8,'Two isolated checkpoint copies',size=7.5,color=MUTED)
    text(ax,37,72,'Harness exposure',size=8.5)
    text(ax,109,72,'Measured continuation',size=8.5)
    ax.plot([7,68],[68.5,68.5],color=INK,lw=.5)
    ax.plot([73,145],[68.5,68.5],color=INK,lw=.5)
    ax.plot([70,70],[7.5,68.5],color='#B0B4B9',lw=.5,ls=(0,(1.5,2.5)))
    for cy, policy, color, tint, is_instance in [
        (50,'Context binding',CONTEXT,CONTEXT_TINT,False),
        (20,'Instance binding',INSTANCE,INSTANCE_TINT,True),
    ]:
        band(ax,6,cy-11,140,26,tint)
        text(ax,9,cy+17,policy,size=7.5,ha='left',color=color)
        candidate(ax,8,cy-6.3,'c2',changed=True,descriptor='c1 → c2',lines=('same context K','harness request'))
        gate(ax,58,cy,color=color,identity=is_instance)
        node(ax,73,cy-6.5,25,13,'Mismatch\nfeedback' if is_instance else 'Accepted\nfeedback',size=7.5)
        ax.add_patch(Circle((112,cy+1),3.2,facecolor='white',edgecolor=INK,lw=.7))
        text(ax,112,cy+1,'A',size=8.5)
        text(ax,112,cy-7,'Agent\ncontinuation',size=7.5)
        node(ax,132,cy-6,13,12,'Audit\nU / I',size=7.5)
        for start,end in [(42,47.5),(68.5,73),(98,108.5),(115.5,132)]:
            flow(ax,[(start,cy+1 if start in (98,115.5) else cy),(end,cy+1 if start in (98,115.5) else cy)])
    text(ax,75,3.3,'G handoff only · shared checks in both arms · K: context match; ID: instance match',size=7.5)
    name = "fig4-paired-intervention"
    qa = _text_qa(fig)
    save_fixed(fig, name)
    _caption(name,
        r"At standardized G handoffs, paired gates differ only in instance equality. The reviewed candidate c1 and its authorization a1 are saved with the conversation and state, then copied into two isolated, directly labelled policy arms. The harness submits c2 with the same context and a different identifier. K denotes $K_{\mathrm{eq}}$; the instance gate adds ID, denoting $I_{\mathrm{eq}}$, while all other checks are shared. Both admission and rejection produce actual feedback for the next sampled agent decision (A), followed by an independent $U/I$ audit. A rejected request makes no commit but leaves the continuation active; subsequent requests must still pass their arm's gate. Measured G outcomes cover 32 delivered pairs from 16 task definitions. N leaves preview management to the agent and is not depicted.",
        "fig:paired")
    return {"name": name, "size_mm": [150, 106], "source_sha256": source_hash,
            "scope": "G standardized handoff only", "delivered_pairs": sum(map(len, groups.values())),
            "task_definitions": 16, "minimum_font_pt": 7.5, "qa": qa}


def _cell(ax, x, y, value, *, color, style="-", bold=False, filled=False):
    ax.add_patch(Rectangle((x - 2.8, y - 2.5), 5.6, 5.0,
                           facecolor='#666B6A' if filled else "white", edgecolor=color, lw=.6, ls=style))
    text(ax, x, y, value, size=7.5, color='white' if filled else color, weight="bold" if bold else "normal")


def _metric_axis(ax, x0, x1, baseline, minimum, maximum, ticks):
    ax.plot([x0, x1], [baseline, baseline], color=INK, lw=.6)
    for value in ticks:
        x = x0 + (x1 - x0) * (value-minimum) / (maximum-minimum)
        ax.plot([x, x], [baseline, baseline - 1.1], color=INK, lw=.6)
        text(ax, x, baseline - 3.3, f"{value:g}", size=7.5, color=MUTED)


def build_recovery():
    """Display all 32 delivered G pairs and cohort-specific descriptive costs."""
    data, groups, source_hash = _read_data()
    fig, ax = canvas(125)
    text(ax,3,121,'(a)',size=8.5,ha='left')
    text(ax, 12, 121, "G outcomes and recovery", size=8.5, weight="bold", ha="left")
    text(ax, 147, 121, "32 pairs / 16 task definitions", size=7.5, ha="right", color=MUTED)

    # Fixed task columns across cohorts. Dashes mark non-membership in the
    # displayed cohort, not failures or additional experimental observations.
    task_ids = list(range(1, 17))
    columns = {task_id: 34 + (task_id-1)*7.05 for task_id in task_ids}
    block_headers = [113.5, 90.5, 67.5]
    alignment = []
    for (cohort, label, expected_n), header_y in zip(COHORTS, block_headers):
        rows = groups[cohort]
        reuse = sum(r["recovery_path"] == "reuse-reviewed" for r in rows)
        fresh = sum(r["recovery_path"] == "reauthorization" for r in rows)
        text(ax, 3, header_y, f"{label}  (n = {expected_n})", ha="left", weight="bold", size=8.5)
        text(ax, 147, header_y, f"{reuse} reuse / {fresh} fresh authorization", ha="right", color=MUTED, size=7.5)
        task_y, context_y, bound_y = header_y - 5.2, header_y - 11.2, header_y - 17.2
        text(ax, 3, task_y, "Task ID", ha="left", color=MUTED, size=7.5)
        text(ax, 3, context_y, "Context U", ha="left", color=CONTEXT, size=7.5)
        text(ax, 3, bound_y, "Instance route", ha="left", color=INSTANCE, size=7.5)
        by_task = {int(row['case_id'].rsplit('-',1)[1]): row for row in rows}
        assert len(by_task) == len(rows)
        for task_id in task_ids:
            x = columns[task_id]
            text(ax, x, task_y, f"{task_id:02d}", size=7.5, color=MUTED)
            row = by_task.get(task_id)
            alignment.append({'cohort':cohort,'task_id':task_id,'x_mm':x,
                              'present':row is not None})
            if row is None:
                for y in (context_y, bound_y):
                    text(ax,x,y,'–',size=7.5,color='#999999')
                continue
            if row['contextU']:
                text(ax,x,context_y,'1',size=7.5,color=MUTED)
            else:
                _cell(ax,x,context_y,'0',color=INK,bold=True)
            path = "R" if row["recovery_path"] == "reuse-reviewed" else "F"
            _cell(ax, x, bound_y, '', color=INK, filled=path=='R')

    text(ax, 3, 45.8, "Instance-rule conformance I: Context 0/32; Instance 32/32.", ha="left", size=7.5)
    text(ax, 111, 45.8, "Instance U: 32/32.", ha="left", size=7.5)
    _cell(ax,6,39,'',color=INK,filled=True)
    text(ax,11,39,'Reuse',ha='left',size=7.5)
    _cell(ax,33,39,'',color=INK)
    text(ax,38,39,'Fresh authorization',ha='left',size=7.5)
    text(ax,93,39,'–  Not in this cohort',ha='left',size=7.5,color=MUTED)

    text(ax,3,33.3,'(b)',size=8.5,ha='left')
    text(ax, 12, 33.3, "Paired suffix cost", size=8.5, ha="left")
    text(ax, 77, 33.3, "Mean Δcalls", size=7.5)
    text(ax, 126, 33.3, "Median Δseconds", size=7.5)
    calls_x = (60, 94)
    seconds_x = (112, 140)
    _metric_axis(ax, *calls_x, baseline=7, minimum=-1, maximum=4, ticks=[-1,0,2,4])
    _metric_axis(ax, *seconds_x, baseline=7, minimum=-25, maximum=55, ticks=[-20,0,25,50])
    summary = []
    for (cohort, label, n), y in zip(COHORTS, [26, 19, 12]):
        rows = groups[cohort]
        # No clipping or absolute-value conversion: signed zero and negative
        # within-pair observations remain in these exact summary calculations.
        call_values = [r["calls_delta"] for r in rows]
        second_values = [r["seconds_delta"] for r in rows]
        mean_calls = statistics.mean(call_values)
        median_seconds = statistics.median(second_values)
        display_label = "Supp. A" if cohort == "supplementary_A" else label
        text(ax, 3, y, f"{display_label} (n = {n})", ha="left", size=7.5)
        for value, vals, (x0,x1), minimum, maximum in [(mean_calls,call_values,calls_x,-1,4),(median_seconds,second_values,seconds_x,-25,55)]:
            transform=lambda v:x0+(x1-x0)*(v-minimum)/(maximum-minimum)
            x=transform(value)
            ax.plot([transform(min(vals)),transform(max(vals))],[y,y],color='#898780',lw=1)
            ax.plot([x], [y], marker="D", markersize=3.5, markerfacecolor=INK,
                    markeredgecolor=INK, markeredgewidth=.9, linestyle="none")
            text(ax, x, y+2.5, f"{value:.2f}", size=7.5)
        summary.append({"cohort": cohort, "n": n, "mean_calls_delta": mean_calls,
                        "median_seconds_delta": median_seconds,
                        "negative_call_differences": sum(v < 0 for v in call_values),
                        "zero_call_differences": sum(v == 0 for v in call_values),
                        "negative_second_differences": sum(v < 0 for v in second_values)})
    name = "fig5-recovery-cost"
    qa = _text_qa(fig)
    save_fixed(fig, name)
    _caption(name,
        r"All 32 delivered G pairs across 16 task definitions. (a) Task columns align across cohorts; dashes mean absent from that cohort's delivered pairs, not failure. Supplementary A omits 04; Original A includes only 04. $I$ denotes instance-rule conformance, not safety under the context policy. Context has $I=0$ throughout and $U=1$ in 30 pairs; all bound arms end with $U=1,I=1$. Filled/open squares denote reuse/fresh authorization. (b) Diamonds show mean call and median elapsed-time differences for complete paired suffixes ($\Delta=$ bound minus context); segments show observed minima--maxima, not confidence intervals. Time includes decisions, tool interactions and terminal paths. Table~\ref{tab:recovery-decomposition} separates recovery calls.",
        "fig:recovery")
    return {"name": name, "size_mm": [150, 125], "source_sha256": source_hash,
            "task_column_alignment": alignment,
            "pairs_displayed": len(data["g_pairs"]), "individual_outcome_and_route_entries": 64,
            "task_definitions": 16, "minimum_font_pt": 7.5, "summary": summary, "qa": qa}


def main():
    result = [build_paired(), build_recovery()]
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
