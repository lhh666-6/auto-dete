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


from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


HERE = Path(__file__).resolve().parent
FIGURE = HERE / "fig2_admission_relation"

fig, ax = plt.subplots(figsize=(183 / 25.4, 107 / 25.4))
ax.set(xlim=(0, 1), ylim=(0, 1))
ax.axis("off")

blue = CATEGORICAL[0]
purple = CATEGORICAL[4]
green = CATEGORICAL[2]
dark = BLACK


def rounded(x, y, w, h, edge, fill):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.009,rounding_size=0.015",
                           edgecolor=edge, facecolor=fill, linewidth=1.0)
    ax.add_patch(patch)


def line(x1, y1, x2, y2, color=dark, width=1.2, style="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=width,
                                 linestyle=style, color=color,
                                 shrinkA=0, shrinkB=0))


def header(x, label, color):
    ax.text(x, 0.844, label, fontsize=8, fontweight="bold", color=color,
            ha="left", va="bottom")


ax.text(0.035, 0.963, "One admission links review intent to a complete record",
        fontsize=10, fontweight="bold", color=dark, va="top")

colx = [0.035, 0.285, 0.54, 0.78]
colw = [0.185, 0.195, 0.185, 0.185]
boxy, boxh = 0.47, 0.345

headers = [
    ("Persisted candidate", blue),
    ("Attributable review", purple),
    ("Admission", dark),
    ("Complete successor", green),
]
for x, (label, color) in zip(colx, headers):
    header(x, label, color)

rounded(colx[0], boxy, colw[0], boxh, blue, "#F0F6FC")
rounded(colx[1], boxy, colw[1], boxh, purple, "#F6F1FA")
rounded(colx[2], boxy, colw[2], boxh, dark, "#F6F6F6")
rounded(colx[3], boxy, colw[3], boxh, green, "#F1F8F2")

ax.text(colx[0]+0.016, 0.752, "$c_1$   exact identity", fontsize=8,
        fontweight="bold", color=blue)
ax.text(colx[0]+0.016, 0.670, "proposal: 100", fontsize=8, color=dark)
ax.text(colx[0]+0.016, 0.597, "evidence: $e_1$", fontsize=8, color=dark)
ax.text(colx[0]+0.016, 0.525, "record, field, version", fontsize=7, color="#555555")

ax.text(colx[1]+0.016, 0.752, "$a_1$   reviewer $q$", fontsize=8,
        fontweight="bold", color=purple)
ax.text(colx[1]+0.016, 0.670, "target: exact $c_1$", fontsize=8, color=dark)
ax.text(colx[1]+0.016, 0.597, "authorized: 101", fontsize=8, color=dark)
ax.text(colx[1]+0.016, 0.525, "Correction: 100 → 101", fontsize=7, color="#555555")

ax.text(colx[2]+0.016, 0.752, "Bind $a_1$ to $c_1$", fontsize=8,
        fontweight="bold", color=dark)
ax.text(colx[2]+0.016, 0.670, "check version", fontsize=8, color=dark)
ax.text(colx[2]+0.016, 0.597, "construct sources", fontsize=8, color=dark)
ax.text(colx[2]+0.016, 0.525, "one atomic commit", fontsize=7,
        fontweight="bold", color=dark)

ax.text(colx[3]+0.016, 0.752, "$S_{v+1}$", fontsize=8, fontweight="bold", color=green)
ax.text(colx[3]+0.016, 0.665, "quantity: 101 ← $t_1$", fontsize=7.4, color=dark)
ax.text(colx[3]+0.016, 0.595, "batch: B-008 ← $t_0$", fontsize=7.4, color=dark)
ax.text(colx[3]+0.016, 0.525, "operator: O7 ← $t'_0$", fontsize=7.4, color=dark)

for i, color in enumerate((blue, purple, dark)):
    line(colx[i]+colw[i]+0.013, 0.642, colx[i+1]-0.013, 0.642, color)

rounded(0.035, 0.158, 0.235, 0.203, "#777777", "#F7F7F7")
ax.text(0.051, 0.306, "Pre-state $S_v$", fontsize=8,
        fontweight="bold", color="#555555")
ax.text(0.051, 0.245, "quantity 90 from $t_{-1}$", fontsize=7)
ax.text(0.051, 0.187, "other sources $t_0$, $t'_0$", fontsize=7)

line(0.270, 0.257, 0.545, 0.42, "#777777", 1.0)
ax.text(0.369, 0.292, "fresh pre-state", fontsize=7, color="#555555")
line(0.270, 0.178, 0.790, 0.406, green, 1.0, "--")
ax.text(0.536, 0.154, "unchanged fields retain their exact prior sources", fontsize=7,
        color=green, ha="center")

ax.text(0.78, 0.345, "changed field: new $t_1$", fontsize=7, color=green)

save_cns_figure(fig, str(FIGURE))
fig.savefig(f"{FIGURE}.svg", bbox_inches="tight")
plt.close(fig)
