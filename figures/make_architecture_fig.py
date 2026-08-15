"""Regenerate a cleaner Auto-Decte architecture figure (swimlane layout)."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = "DejaVu Sans"

# Colors by role
C_BLUE = "#dbeafe"    # perception
C_BLUE_E = "#1d4ed8"
C_YELL = "#fef9c3"    # AI assistance
C_YELL_E = "#a16207"
C_ORANGE = "#ffedd5"  # human review
C_ORANGE_E = "#c2410c"
C_GREEN = "#dcfce7"   # records/export
C_GREEN_E = "#15803d"
C_GRAY = "#e5e7eb"    # preamble
C_GRAY_E = "#374151"

EDGE = "#334155"


def box(ax, x, y, w, h, label, fill, ec, fs=8.2):
    b = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.012", linewidth=1.0,
        edgecolor=ec, facecolor=fill, zorder=3,
    )
    ax.add_patch(b)
    ax.text(x, y, label, ha="center", va="center", fontsize=fs, color="#111827", zorder=4)


def arrow(ax, p0, p1, dashed=False, color=EDGE):
    ax.add_patch(
        FancyArrowPatch(
            p0, p1, arrowstyle="-|>", mutation_scale=11,
            linewidth=1.1, color=color,
            linestyle="--" if dashed else "-", zorder=2,
            shrinkA=0, shrinkB=0,
        )
    )


fig, ax = plt.subplots(figsize=(12.6, 4.6))
ax.set_xlim(0, 12.6)
ax.set_ylim(0, 4.6)
ax.axis("off")

# Lane backgrounds
ax.add_patch(plt.Rectangle((0.1, 3.05), 12.4, 1.45, facecolor="#f0f6ff", edgecolor="none", zorder=0))
ax.add_patch(plt.Rectangle((0.1, 0.15), 12.4, 2.05, facecolor="#fdfbf5", edgecolor="none", zorder=0))

# Lane labels
ax.text(0.35, 3.78, "Perception\nfront end", ha="center", va="center", fontsize=9,
        color=C_BLUE_E, fontweight="bold")
ax.text(0.35, 1.5, "AI assistance +\nhuman review", ha="center", va="center", fontsize=9,
        color=C_ORANGE_E, fontweight="bold")

# ---- Row 1: perception (y=3.78) ----
row1 = [
    ("Template\ndesign", C_GRAY, C_GRAY_E),
    ("Paper form\n(hand-filled)", C_GRAY, C_GRAY_E),
    ("Photo\nimport", C_BLUE, C_BLUE_E),
    ("Quality\ngate", C_BLUE, C_BLUE_E),
    ("QR\nclassification", C_BLUE, C_BLUE_E),
    ("ArUco\nperspective", C_BLUE, C_BLUE_E),
    ("Field\ncropping", C_BLUE, C_BLUE_E),
    ("Digit / OMR\ncandidates", C_BLUE, C_BLUE_E),
]
xs1 = [1.35, 2.55, 3.85, 5.05, 6.25, 7.45, 8.65, 9.95]
for (label, fill, ec), x in zip(row1, xs1):
    box(ax, x, 3.78, 1.12, 1.0, label, fill, ec)
for a, b in zip(xs1[:-1], xs1[1:]):
    arrow(ax, (a + 0.56, 3.78), (b - 0.56, 3.78))

# ---- Row 2: AI + review (y=1.8) ----
box(ax, 5.0, 1.8, 1.5, 0.85, "LLM suggestions\n(DeepSeek)", C_YELL, C_YELL_E)
box(ax, 7.0, 1.8, 1.5, 0.85, "Similarity\nretrieval", C_YELL, C_YELL_E)
box(ax, 9.6, 1.8, 1.7, 1.05, "Human review\nworkbench", C_ORANGE, C_ORANGE_E)
box(ax, 11.75, 1.8, 1.4, 1.05, "Versioned\nrecords + export", C_GREEN, C_GREEN_E)

# perception -> review (main candidate flow)
arrow(ax, (9.95, 3.78 - 0.5), (9.6, 1.8 + 0.52))
# AI -> review (dashed, optional/read-only)
arrow(ax, (5.0 + 0.75, 1.8), (9.6 - 0.85, 1.8 + 0.0), dashed=True)
arrow(ax, (7.0 + 0.75, 1.8), (9.6 - 0.85, 1.8 - 0.05), dashed=True)
# review -> records
arrow(ax, (9.6 + 0.85, 1.8), (11.75 - 0.7, 1.8))

# annotations
ax.text(9.6, 2.95, "candidates only\n(machine never writes facts)", ha="center", va="center",
        fontsize=7.4, color=C_ORANGE_E, style="italic")
ax.text(5.35, 2.62, "read-only, optional", ha="left", va="center",
        fontsize=6.8, color=C_YELL_E, style="italic")

plt.savefig(
    r"D:\Claude_Design\auto-decte-paper\figures\architecture.png",
    dpi=220, bbox_inches="tight", facecolor="white",
)
print("figure saved")
