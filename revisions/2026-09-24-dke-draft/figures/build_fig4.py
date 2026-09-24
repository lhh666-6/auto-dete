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
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "e3-trace-summary.csv"
FIGURE = HERE / "fig4_trace_cost"

with DATA.open(encoding="utf-8-sig", newline="") as source:
    rows = list(csv.DictReader(source))

cells = defaultdict(dict)
for row in rows:
    key = tuple(int(row[name]) for name in ("fields", "versions", "records"))
    assert row["arm"] in ("batch", "point_lookup")
    assert row["arm"] not in cells[key]
    assert int(row["n"]) == 200
    cells[key][row["arm"]] = float(row["p50_ms"])

assert len(rows) == 72 and len(cells) == 36
assert all(set(cell) == {"batch", "point_lookup"} for cell in cells.values())
assert {key[0] for key in cells} == {1, 8, 32, 128}
assert {key[1] for key in cells} == {1, 10, 100}
assert {key[2] for key in cells} == {1, 100, 1000}
assert all(cell["point_lookup"] > cell["batch"] for cell in cells.values())

large = cells[(128, 100, 1000)]
assert round(large["batch"], 2) == 170.24
assert round(large["point_lookup"], 2) == 509.09

fig, ax = plt.subplots(figsize=(183 / 25.4, 103 / 25.4))
fig.subplots_adjust(left=0.12, right=0.96, top=0.82, bottom=0.16)
fig.text(0.055, 0.97, "Trace cost across all 36 paired workload cells",
         fontsize=9, fontweight="bold", ha="left", va="top", color=BLACK)

field_styles = {
    1: ("o", CATEGORICAL[0]),
    8: ("s", CATEGORICAL[2]),
    32: ("^", CATEGORICAL[3]),
    128: ("D", CATEGORICAL[4]),
}
for fields, (marker, color) in field_styles.items():
    points = [cell for key, cell in sorted(cells.items()) if key[0] == fields]
    ax.scatter([cell["batch"] for cell in points],
               [cell["point_lookup"] for cell in points],
               marker=marker, s=35, color=color, alpha=0.82,
               edgecolor="white", linewidth=0.5,
               label=f"{fields} fields", zorder=3)

ax.plot([4, 850], [4, 850], color=GREY, linewidth=1, linestyle="--", zorder=1)
ax.text(5.5, 5.3, "Equal latency", fontsize=7, color="#666666",
        rotation=37, ha="left", va="bottom")
ax.annotate("128 fields · 100 versions · 1,000 records\n170.24 ms / 509.09 ms",
            xy=(large["batch"], large["point_lookup"]),
            xytext=(27, 610), fontsize=7, color=BLACK,
            arrowprops={"arrowstyle": "-", "color": "#555555", "lw": 0.8},
            ha="left", va="bottom")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(4, 850)
ax.set_ylim(4, 850)
ax.set_xticks([5, 10, 20, 50, 100, 200, 500])
ax.set_yticks([5, 10, 20, 50, 100, 200, 500])
ax.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax.get_yaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax.set_xlabel("Bulk retrieval median trace latency (ms)")
ax.set_ylabel("Point lookup median trace latency (ms)")
ax.grid(which="major", color="#E7E7E7", linewidth=0.6, zorder=0)
ax.legend(loc="lower right", ncol=2, title="Record width", title_fontsize=7,
          handletextpad=0.3, columnspacing=0.7)
fig.text(0.055, 0.035, "Each cell: 200 measured traces per arm; the verifier and returned trace were held fixed.",
         fontsize=7, color="#555555", ha="left", va="bottom")

save_cns_figure(fig, str(FIGURE))
fig.savefig(f"{FIGURE}.svg", bbox_inches="tight")
plt.close(fig)
