# Academic Figure Skill Typography Baseline — COPY VERBATIM, place at TOP of script
import matplotlib as mpl
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
    "pdf.fonttype": 42,         # TrueType font embedding
    "svg.fonttype": "none",     # editable text in SVG
    "savefig.bbox": "tight",    # trim whitespace
    "savefig.dpi": 300,
})

def save_cns_figure(fig, filename):
    """Standard Academic Figure Skill export: vector PDF + 300dpi PNG preview."""
    fig.savefig(f"{filename}.pdf", bbox_inches="tight", dpi=300)
    fig.savefig(f"{filename}.png", bbox_inches="tight", dpi=300)


import csv
from pathlib import Path

import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "e1-comparison.csv"
FIGURE = HERE / "fig3_candidate_binding_comparison"

with DATA.open(encoding="utf-8-sig", newline="") as source:
    rows = {row["arm"]: row for row in csv.DictReader(source)}

arms = ("journal_context", "journal_exact", "reference")
assert set(rows) == set(arms)
assert all(int(rows[arm]["scored"]) == 165 for arm in arms)
assert all(int(rows[arm]["harness_errors"]) == 0 for arm in arms)
assert all(int(rows[arm]["accepted"]) - int(rows[arm]["instance_policy_violations"]) == 45 for arm in arms)

names = ("Context-only", "Exact journal", "Reference")
colors = (ACCENT_RED, CATEGORICAL[0], CATEGORICAL[2])
metrics = (
    ("instance_policy_violations", "Instance-policy violations", 17),
    ("query_ambiguous", "Ambiguous candidate answers", 65),
)

fig, axes = plt.subplots(1, 2, figsize=(183 / 25.4, 78 / 25.4))
fig.subplots_adjust(left=0.22, right=0.97, top=0.73, bottom=0.22, wspace=0.49)
fig.text(0.05, 0.975, "Exact binding separates equal-valued histories",
         fontsize=9, fontweight="bold", ha="left", va="top", color=BLACK)

for panel, (ax, (key, title, limit)) in enumerate(zip(axes, metrics)):
    values = [int(rows[arm][key]) for arm in arms]
    positions = [2, 1, 0]
    ax.barh(positions, values, color=colors, height=0.46, edgecolor="none")
    ax.scatter([0 for value in values if value == 0],
               [position for value, position in zip(values, positions) if value == 0],
               s=18, color=[color for value, color in zip(values, colors) if value == 0], zorder=3)
    for value, position in zip(values, positions):
        ax.text(value + limit * 0.025, position, str(value), va="center",
                ha="left", fontweight="bold", color=BLACK)
    ax.set_yticks(positions, names if panel == 0 else ["", "", ""])
    ax.set_xlim(0, limit)
    ax.set_ylim(-0.55, 2.55)
    ax.set_title(title, loc="left", pad=9, fontweight="bold")
    ax.set_xlabel("Count")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=5)
    ax.set_xticks([0, 5, 10, 15] if limit == 17 else [0, 20, 40, 60])

fig.text(0.05, 0.035, "Each mechanism: 165 constructed cases; all 45 legal cases admitted.",
         fontsize=7, color="#555555", ha="left", va="bottom")

save_cns_figure(fig, str(FIGURE))
fig.savefig(f"{FIGURE}.svg", bbox_inches="tight")
plt.close(fig)
