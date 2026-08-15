"""Regenerate Fig.1 as a layered trust architecture (not a flat pipeline).

Layers: Evidence acquisition -> Candidate plane (recognition + LLM + retrieval,
all abstain/candidate-only) -> Human trust boundary -> Fact plane (versioned,
auditable records).
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = "DejaVu Sans"

BLUE = "#dbeafe"; BLUE_E = "#1d4ed8"
YELL = "#fef9c3"; YELL_E = "#a16207"
ORANGE = "#ffedd5"; ORANGE_E = "#c2410c"
GREEN = "#dcfce7"; GREEN_E = "#15803d"
GRAY = "#e5e7eb"; GRAY_E = "#374151"
EDGE = "#334155"


def box(ax, x, y, w, h, label, fill, ec, fs=8.0, lw=1.0):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.012", linewidth=lw, edgecolor=ec,
        facecolor=fill, zorder=3))
    ax.text(x, y, label, ha="center", va="center", fontsize=fs,
            color="#111827", zorder=4)


def arrow(ax, p0, p1, dashed=False, lw=1.2):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=12,
        linewidth=lw, color=EDGE, linestyle="--" if dashed else "-",
        zorder=2, shrinkA=0, shrinkB=0))


fig, ax = plt.subplots(figsize=(11.4, 7.2))
ax.set_xlim(0, 11.4)
ax.set_ylim(0, 7.2)
ax.axis("off")

ax.add_patch(plt.Rectangle((0.1, 5.7), 11.2, 1.3, facecolor="#f5f7fa", edgecolor="none", zorder=0))
ax.add_patch(plt.Rectangle((0.1, 3.6), 11.2, 1.7, facecolor="#f0f6ff", edgecolor="none", zorder=0))
ax.add_patch(plt.Rectangle((0.1, 2.35), 11.2, 0.9, facecolor="#fff7ed", edgecolor="none", zorder=0))
ax.add_patch(plt.Rectangle((0.1, 0.4), 11.2, 1.55, facecolor="#f0fdf4", edgecolor="none", zorder=0))

ax.text(0.28, 6.35, "Evidence\nlayer", ha="center", va="center", fontsize=9,
        color=GRAY_E, fontweight="bold")
ax.text(0.28, 4.45, "Candidate\nplane", ha="center", va="center", fontsize=9,
        color=BLUE_E, fontweight="bold")
ax.text(0.28, 2.8, "Trust\nboundary", ha="center", va="center", fontsize=8.5,
        color=ORANGE_E, fontweight="bold")
ax.text(0.28, 1.17, "Fact\nplane", ha="center", va="center", fontsize=9,
        color=GREEN_E, fontweight="bold")

box(ax, 4.6, 6.35, 1.6, 0.8, "Template design\n(versioned, QR+ArUco)", GRAY, GRAY_E)
box(ax, 7.2, 6.35, 1.6, 0.8, "Photo import\n(SHA-256 dedup)", GRAY, GRAY_E)
arrow(ax, (4.6 + 0.8, 6.35), (7.2 - 0.8, 6.35))

box(ax, 2.6, 4.45, 1.7, 1.0, "Fiducial perception\n(QR classify, ArUco\nperspective, crop)", BLUE, BLUE_E)
box(ax, 5.4, 4.45, 1.7, 1.0, "Selective recognition\n(digit / OMR\n+ ambiguity band)", BLUE, BLUE_E)
box(ax, 8.4, 4.45, 1.4, 1.0, "LLM suggestions\n(DeepSeek,\nread-only)", YELL, YELL_E)
box(ax, 10.5, 4.45, 1.3, 1.0, "Similarity\nretrieval\n(read-only)", YELL, YELL_E)
arrow(ax, (2.6 + 0.85, 4.45), (5.4 - 0.85, 4.45))
arrow(ax, (5.4 + 0.85, 4.45), (8.4 - 0.7, 4.45), dashed=True)
arrow(ax, (5.4 + 0.85, 4.45), (10.5 - 0.65, 4.45), dashed=True)
arrow(ax, (7.2, 6.35 - 0.4), (2.6, 4.45 + 0.5))

box(ax, 5.7, 2.8, 3.6, 0.72, "Human review workbench  (confirm / correct / void)",
    ORANGE, ORANGE_E, fs=8.4, lw=1.4)

arrow(ax, (5.4, 4.45 - 0.5), (5.7, 2.8 + 0.36))
arrow(ax, (8.4, 4.45 - 0.5), (5.7, 2.8 + 0.30), dashed=True)
arrow(ax, (10.5, 4.45 - 0.5), (5.7, 2.8 + 0.24), dashed=True)

box(ax, 3.6, 1.17, 1.9, 0.9, "Versioned facts\n(append-only\nRecordVersion)", GREEN, GREEN_E)
box(ax, 6.3, 1.17, 1.9, 0.9, "Audit lineage\n(before/after,\nback-traceable)", GREEN, GREEN_E)
box(ax, 9.0, 1.17, 1.9, 0.9, "XLSX export\n(re-exportable,\n4 worksheets)", GREEN, GREEN_E)
arrow(ax, (5.7, 2.8 - 0.36), (3.6, 1.17 + 0.45))
arrow(ax, (3.6 + 0.95, 1.17), (6.3 - 0.95, 1.17))
arrow(ax, (6.3 + 0.95, 1.17), (9.0 - 0.95, 1.17))

ax.text(11.0, 4.45, "candidates /\nreferences only", fontsize=7.0,
        color=BLUE_E, style="italic", ha="left", va="center")
ax.text(11.0, 2.8, "machine never\nwrites facts", fontsize=7.0,
        color=ORANGE_E, style="italic", ha="left", va="center")
ax.text(2.9, 0.05, "AI-off path: pipeline remains correct with LLM/retrieval disabled",
        fontsize=7.0, color=GREEN_E, style="italic", ha="left", va="center")

plt.savefig(r"D:\Claude_Design\auto-decte-paper\figures\architecture.png",
            dpi=220, bbox_inches="tight", facecolor="white")
print("figure saved")
