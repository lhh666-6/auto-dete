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
FIGURE = HERE / "fig1_same_value_different_history"

fig, ax = plt.subplots(figsize=(183 / 25.4, 91 / 25.4))
ax.set(xlim=(0, 1), ylim=(0, 1))
ax.axis("off")

blue = CATEGORICAL[0]
red = ACCENT_RED
green = CATEGORICAL[2]
light_blue = "#EFF6FC"
light_red = "#FCF2F2"
light_grey = "#F6F7F8"


def box(x, y, w, h, text, edge, face, weight="normal"):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.013,rounding_size=0.013",
        linewidth=0.9, edgecolor=edge, facecolor=face,
    ))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            color=BLACK, fontsize=8, fontweight=weight, linespacing=1.55)


def arrow(x1, y, x2, color):
    ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=1.25,
                                 color=color, shrinkA=0, shrinkB=0))


ax.text(0.02, 0.96, "Same final value, different authorization history",
        fontsize=10, fontweight="bold", color=BLACK, va="top")
ax.text(0.02, 0.87, "Shared pre-state: quantity = 90", fontsize=8, color="#505050")

xs = [0.055, 0.303, 0.564, 0.799]
ws = [0.185, 0.200, 0.166, 0.169]
ys = [0.563, 0.195]
h = 0.205

ax.text(0.02, 0.792, "A  Candidate-bound admission", fontsize=8, fontweight="bold", color=blue)
box(xs[0], ys[0], ws[0], h, "Candidate $c_1$\nproposes 100", blue, light_blue)
box(xs[1], ys[0], ws[1], h, "Review $c_1$\nauthorizes 101", blue, light_blue)
box(xs[2], ys[0], ws[2], h, "Admit $c_1$", blue, light_blue, "bold")
box(xs[3], ys[0], ws[3], h, "quantity 101\nsource $t_1$\ntraces to $c_1$", green, "#F0F8F2")
for i in range(3):
    arrow(xs[i] + ws[i] + 0.015, ys[0] + h / 2, xs[i + 1] - 0.015, blue)

ax.text(0.02, 0.424, "B  Equal-valued candidate substitution", fontsize=8,
        fontweight="bold", color=red)
box(xs[0], ys[1], ws[0], h, "Candidates $c_1$, $c_2$\nboth propose 100", "#777777", light_grey)
box(xs[1], ys[1], ws[1], h, "Review $c_1$\nauthorizes 101", blue, light_blue)
box(xs[2], ys[1], ws[2], h, "Admit $c_2$", red, light_red, "bold")
box(xs[3], ys[1], ws[3], h, "quantity 101\nsource $t_2$\ntraces to $c_2$", red, light_red)
arrow(xs[0] + ws[0] + 0.015, ys[1] + h / 2, xs[1] - 0.015, "#777777")
arrow(xs[1] + ws[1] + 0.015, ys[1] + h / 2, xs[2] - 0.015, red)
arrow(xs[2] + ws[2] + 0.015, ys[1] + h / 2, xs[3] - 0.015, red)
ax.text(0.538, 0.172, "review target ≠ admitted candidate", color=red,
        fontsize=7, ha="center", va="top")

ax.text(0.02, 0.045,
        "$c_1$ and $c_2$ are distinct persisted instances with the same proposal and retained review context.",
        fontsize=7, color="#505050", va="bottom")

save_cns_figure(fig, str(FIGURE))
fig.savefig(f"{FIGURE}.svg", bbox_inches="tight")
plt.close(fig)
