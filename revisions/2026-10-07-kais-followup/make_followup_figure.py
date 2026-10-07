# Academic Figure Skill Asset Confirmation (verified against assets/figures/)
# (a) Recovery composition -> cross-type inherit from local revised figure 4 -> param inherit
# (b) Paired G friction -> direct statistic annotation, matching local figure 4 -> param inherit
# RULE: Native-run raster panels are not used: all marks and labels remain vector.
# The generic SankeyDiagram asset simulates an eight-stage network and does not
# represent these two observed cohorts. The existing manuscript's palette,
# dimensions and typography take precedence over generic CNS layout defaults.
"""Compare G recovery in the original B and separately collected A cohorts.

Run from any directory:
  python make_followup_figure.py
  python make_followup_figure.py --followup-dir PATH_TO_FOLLOWUP_EXPORT

The export must contain table1-outcomes.csv, table2-continuity.csv,
table3-recovery.csv and paired-effects.csv. No partial data are rendered.
Outputs are confined to figures/followup-*; the original figures are unchanged.
"""

from pathlib import Path
import argparse
from collections import Counter
import csv
import hashlib
import json
import math
import statistics

import matplotlib as mpl
mpl.use("Agg")

# Academic Figure Skill Typography Baseline — COPY VERBATIM, place at TOP of script
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans"],
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 8,
    "figure.titlesize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.6,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.frameon": False,
})
# Academic Figure Skill Nature/Cell/Science Color Palette -- COPY VERBATIM
CATEGORICAL = ["#2166AC", "#B2182B", "#1B7837", "#F1A340", "#762A83", "#666666"]
CATEGORICAL_EXTENDED = [
    "#2166AC", "#B2182B", "#1B7837", "#F1A340", "#762A83", "#666666",
    "#4393C3", "#D6604D", "#5AAE61", "#B35806", "#9970AB", "#999999",
]
DIVERGING   = ["#2166AC", "#F7F7F7", "#B2182B"]
SEQUENTIAL  = ["#F7FBFF", "#6BAED6", "#08306B"]
ACCENT_RED  = "#B2182B"
GREY        = "#999999"
BLACK       = "#222222"
# Academic Figure Skill Export Baseline — COPY VERBATIM
mpl.rcParams.update({
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "savefig.bbox": "tight",
    "savefig.dpi": 300,
})


def save_cns_figure(fig, filename):
    """Standard Academic Figure Skill export: vector PDF + 300dpi PNG preview."""
    fig.savefig(f"{filename}.pdf", bbox_inches="tight", dpi=300)
    fig.savefig(f"{filename}.png", bbox_inches="tight", dpi=300)


# Explicit manuscript style override: exact 172 mm export, existing DejaVu
# typography and semantic pastel colours. Do not shrink with a tight bbox.
mpl.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 7.5,
    "mathtext.fontset": "dejavusans", "pdf.fonttype": 42,
    "ps.fonttype": 42, "svg.fonttype": "none", "savefig.bbox": None,
    "svg.hashsalt": "kais-followup-2026", "axes.unicode_minus": False,
    "savefig.facecolor": "white",
})

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "figures"
WIDTH, HEIGHT = 172, 74
INK, MUTED, LINE = "#18324A", "#536574", "#B8C6D0"
BLUE, BLUE_PALE, BLUE_MID = "#356799", "#EDF5FD", "#D8E9FA"
VIOLET, VIOLET_PALE, VIOLET_MID = "#675395", "#F3F0FC", "#E5DFF6"
TEAL, TEAL_PALE, TEAL_MID = "#147569", "#EDF8F2", "#D8EEE1"
FILES = ["table1-outcomes.csv", "table2-continuity.csv", "table3-recovery.csv", "paired-effects.csv"]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def source_key(path):
    """Use package-relative provenance when the evidence is bundled here."""
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(resolved)


def truth(value):
    return str(value).lower() in {"true", "1", "1.0"}


def subset(records, config, policy=None):
    return [r for r in records if r["scenario"] == "G" and r["config_id"] == config
            and (policy is None or r["policy"] == policy)]


def read_cohort(path, config, label, planned_pairs):
    tables = {name: read_csv(path / name) for name in FILES}
    out = subset(tables[FILES[0]], config, "bound")
    assert len(out) == 1, "Expected one G-bound outcome row per cohort"
    total_planned = sum(int(r["planned"]) for r in tables[FILES[0]] if r["config_id"] == config and r["policy"] == "bound")
    assert total_planned == planned_pairs
    episodes = [r for r in subset(tables[FILES[2]], config, "bound")
                if truth(r["Delivered"]) and truth(r["RecoverableReject"]) and r["trigger_code"] == "INSTANCE_MISMATCH"]
    assert len({r["pair_id"] for r in episodes}) == len(episodes), "Repeated episode per G pair requires explicit design update"
    paths = Counter(r["recovery_strategy"] for r in episodes)
    assert set(paths) <= {"reuse-reviewed", "reauthorization"}, f"Additional verified recovery paths need explicit labels: {paths}"
    assert 0 < len(episodes) <= int(out[0]["checkpoint_reached"]), "Delivered exposure must be a nonempty subset of checkpoint coverage"
    joint = sum(truth(r["U"]) and r["I"] == "1" and truth(r["recovered"]) for r in episodes)
    context = subset(tables[FILES[1]], config, "context")
    substitutions = [r for r in context if truth(r["executed_substitution"]) and truth(r["policy_admissible"])]
    selected_tasks = {r["task_instance_id"] for r in episodes}
    paired = [r for r in subset(tables[FILES[3]], config) if r["task_instance_id"] in selected_tasks]
    assert len(paired) == len(episodes), "Friction denominator must include every exposed pair"
    costs = {}
    for field, short, scale in [("delta_suffix_agent_tool_calls", "calls", 1), ("delta_suffix_elapsed_ms", "seconds", 1000)]:
        values = [float(r[field]) / scale for r in paired]
        assert values and all(math.isfinite(v) for v in values)
        costs[short] = {"n": len(values), "mean": statistics.mean(values), "median": statistics.median(values), "values": values}
    g_context = subset(tables[FILES[0]], config, "context")[0]
    result = {
        "label": label, "config_id": config, "collection_planned_pairs": total_planned,
        "g_planned_pairs": int(out[0]["planned"]), "g_checkpoint_pairs": int(out[0]["checkpoint_reached"]), "g_delivered_pairs": len(episodes),
        "g_paths": dict(paths), "g_joint_U1_I1": joint,
        "g_context_substitutions": len(substitutions), "g_paired_cost": costs,
        "g_context_U1": int(g_context["task_completion"]), "g_bound_U1": int(out[0]["task_completion"]),
        "source_hashes": {source_key(path / name): hashlib.sha256((path / name).read_bytes()).hexdigest() for name in FILES},
        "episode_pair_ids": sorted(r["pair_id"] for r in episodes),
    }
    return result


def txt(ax, x, y, value, size=7.5, color=INK, weight="normal", ha="left"):
    return ax.text(x, y, value, ha=ha, va="center", color=color, fontsize=size,
                   fontweight=weight, linespacing=1.30)


def card(ax, x, y, width, height, fill, edge, radius=1.3):
    ax.add_patch(FancyBboxPatch((x, y), width, height,
                              boxstyle=f"round,pad=0,rounding_size={radius}",
                              facecolor=fill, edgecolor=edge, linewidth=.6))


def arrow(ax, x1, x2, y):
    ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="-|>", mutation_scale=6,
                                 color=LINE, linewidth=.7, shrinkA=0, shrinkB=0))


def draw_row(ax, cohort, y, label):
    n = cohort["g_delivered_pairs"]
    txt(ax, 3, y + 4, label, 8.4, BLUE if cohort["config_id"] == "B" else VIOLET, "bold")
    txt(ax, 3, y + 10, f"{n}/{cohort['g_planned_pairs']} G pairs", 7.5)
    txt(ax, 3, y + 15, "rejection delivered", 7.0, MUTED)

    # Count-labelled blocks express the observed composition without implying
    # a pooled rate. Zero-count categories stay explicitly labelled.
    card(ax, 36, y, 57, 21, "#F8FAFB", "#DCE4E9")
    reuse = cohort["g_paths"].get("reuse-reviewed", 0)
    reauth = cohort["g_paths"].get("reauthorization", 0)
    bar_x, bar_w, bar_y, bar_h = 39, 51, y + 14, 4.2
    txt(ax, 39, y + 4.5, f"Reuse reviewed: {reuse}/{n}", 7.5, BLUE, "bold")
    txt(ax, 39, y + 9.6, f"Reauthorize: {reauth}/{n}", 7.5, VIOLET)
    left = bar_x
    for count, fill, edge in [(reuse, BLUE_MID, BLUE), (reauth, VIOLET_MID, VIOLET)]:
        width = bar_w * count / n
        if count:
            ax.add_patch(Rectangle((left, bar_y), width, bar_h, facecolor=fill, edgecolor=edge, linewidth=.55))
            left += width
    arrow(ax, 94, 99, y + 10.5)

    card(ax, 100, y, 27, 21, TEAL_PALE, TEAL_MID)
    txt(ax, 113.5, y + 6.5, f"{cohort['g_joint_U1_I1']}/{n}", 12, TEAL, "bold", "center")
    txt(ax, 113.5, y + 15, r"$U=1, I=1$", 7.5, TEAL, ha="center")

    card(ax, 132, y, 37, 21, "#FFF4EC", "#FAE3CF")
    calls = cohort["g_paired_cost"]["calls"]
    seconds = cohort["g_paired_cost"]["seconds"]
    txt(ax, 135, y + 4.7, f"{calls['mean']:+.2f} calls (mean)", 7.6, INK, "bold")
    txt(ax, 135, y + 10.6, f"{seconds['median']:+.2f} s (median)", 7.6, INK, "bold")
    txt(ax, 135, y + 16.8, f"paired G: n = {calls['n']}", 7.0, MUTED)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--followup-dir", type=Path, default=ROOT / "evidence/followup")
    args = parser.parse_args()
    summary_path = args.followup_dir / "analysis-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["collection_status"] == "COMPLETE", "Refuse a partially collected follow-up"
    original = read_cohort(ROOT / "evidence/online", "B", "Original B", 128)
    followup = read_cohort(args.followup_dir, "A", "Supplementary A", 117)
    assert followup["g_planned_pairs"] == summary["G"]["scheduled_pairs"]
    assert followup["g_checkpoint_pairs"] == summary["G"]["checkpoint_reached_pairs"]
    assert followup["g_delivered_pairs"] == summary["G"]["bound_delivered_episodes"]
    followup["source_hashes"][source_key(summary_path)] = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    # Original frozen counts are invariants, not substituted follow-up estimates.
    assert original["g_paths"] == {"reuse-reviewed": 16}
    assert original["g_paired_cost"]["calls"]["median"] == 1
    assert original["g_paired_cost"]["calls"]["mean"] == 1
    assert math.isclose(original["g_paired_cost"]["seconds"]["median"], 14.539, abs_tol=1e-9)
    fig = plt.figure(figsize=(WIDTH / 25.4, HEIGHT / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, WIDTH), ylim=(HEIGHT, 0))
    ax.axis("off")
    txt(ax, 3, 4.5, "G  |  Recovery after delivered instance-mismatch rejection", 9, BLUE, "bold")
    txt(ax, 3, 10.5, "Collection cohort", 7.2, MUTED)
    txt(ax, 36, 10.5, "Observed bound recovery", 7.2, MUTED)
    txt(ax, 100, 10.5, "Joint outcome", 7.2, MUTED)
    txt(ax, 132, 10.5, "Paired bound − context", 7.0, MUTED)
    draw_row(ax, original, 15, "Original B")
    draw_row(ax, followup, 42, "Supplementary A")
    ax.plot([3, 169], [39, 39], color=LINE, lw=.55, linestyle=(0, (3, 3)))
    txt(ax, 3, 68, f"Context admitted {original['g_context_substitutions']} B and "
        f"{followup['g_context_substitutions']} A substitutions (I = 0).", 7.2, MUTED)
    txt(ax, 3, 72, f"Context task completion: B {original['g_context_U1']}/{original['g_planned_pairs']}; "
        f"A {followup['g_context_U1']}/{followup['g_planned_pairs']}. Separate collection cohorts.", 7.0, MUTED)
    OUTPUT.mkdir(exist_ok=True)
    basename = OUTPUT / "followup-behavior-comparison"
    for ext in ("pdf", "svg", "png"):
        fig.savefig(basename.with_suffix(f".{ext}"), dpi=600, bbox_inches=None)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = fig.bbox
    clipped = [t.get_text() for t in ax.texts if not bounds.contains(*t.get_window_extent(renderer).p0) or not bounds.contains(*t.get_window_extent(renderer).p1)]
    assert not clipped, f"Text outside the publication canvas: {clipped}"
    plt.close(fig)
    audit = {
        "figure": "followup-behavior-comparison", "width_mm": WIDTH, "height_mm": HEIGHT,
        "png_dpi": 600, "minimum_base_font_pt": 7.0,
        "cohort_pooling": False, "original_planned_arms": 512,
        "cohorts": [original, followup],
        "statistical_scope": {
            "unit": "Delivered G-bound instance-mismatch episode, one per exposed task pair",
            "path_counts": "Descriptive conditional on actual delivered rejection; no pooled inference",
            "cost": "Mean within-pair bound minus context suffix agent tool calls; median within-pair elapsed seconds",
            "interval_or_test": "None: descriptive cohort-specific summaries only",
            "multiple_testing": "Not applicable",
            "completion": "Joint U=1 and I=1 counted among delivered G-bound episodes",
        },
        "validation": {"source_counts": "PASS", "all_exposed_pairs_in_costs": "PASS", "text_inside_canvas": "PASS"},
    }
    audit_path = OUTPUT / "followup-figure-source-audit.json"
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"outputs": [str(basename.with_suffix('.' + e)) for e in ("pdf", "svg", "png")],
                      "cohorts": [{k: v for k, v in c.items() if k not in {"source_hashes", "episode_pair_ids", "g_paired_cost"}} for c in (original, followup)]}, indent=2))


if __name__ == "__main__":
    main()
