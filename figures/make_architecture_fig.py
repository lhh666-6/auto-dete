"""Generate the Auto-Decte pipeline architecture figure (Fig. 1)."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

stages = [
    ("Template design\n(QR + ArUco)", "print", "lightsteelblue"),
    ("Paper form\n(hand-filled)", "paper", "lavender"),
    ("Photo import\n(SHA-256 dedup)", "import", "lightsteelblue"),
    ("Quality gate\n(blur/dark/glare)", "quality", "lightsteelblue"),
    ("Template recognition\n(QR payload)", "qr", "lightsteelblue"),
    ("Perspective correction\n(ArUco 10-13)", "aruco", "lightsteelblue"),
    ("Field cropping\n+ digit/OMR candidates", "recog", "lightsteelblue"),
    ("AI suggestions\n(optional, read-only)", "ai", "lightyellow"),
    ("Human review workbench\n(confirm/correct/void)", "review", "lightsalmon"),
    ("Versioned records\n+ audit + XLSX export", "export", "lightgreen"),
]
positions = {
    "print": (0.5, 0.5),
    "paper": (0.5, 0.32),
    "import": (0.5, 0.14),
    "quality": (0.5, -0.04),
    "qr": (0.5, -0.22),
    "aruco": (0.5, -0.40),
    "recog": (0.5, -0.58),
    "ai": (0.82, -0.58),
    "review": (0.5, -0.76),
    "export": (0.5, -0.94),
}
edges = [
    ("print", "paper"), ("paper", "import"), ("import", "quality"),
    ("quality", "qr"), ("qr", "aruco"), ("aruco", "recog"),
    ("recog", "ai"), ("ai", "review"), ("recog", "review"),
    ("review", "export"),
]

fig, ax = plt.subplots(figsize=(7.5, 10))
ax.set_xlim(0, 1)
ax.set_ylim(-1.05, 0.62)
ax.axis("off")

boxes = {}
for label, key, color in stages:
    x, y = positions[key]
    box = FancyBboxPatch(
        (x - 0.24, y - 0.06), 0.48, 0.12,
        boxstyle="round,pad=0.008", linewidth=1.2,
        edgecolor="#333333", facecolor=color, zorder=3,
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=8.5, zorder=4)
    boxes[key] = (x, y)

for src, dst in edges:
    sx, sy = boxes[src]
    dx, dy = boxes[dst]
    start = (sx, sy - 0.06)
    end = (dx, dy + 0.06)
    style = "dashed" if src == "ai" else "-"
    arrow = FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=10,
        linewidth=1.1, color="#555555", linestyle=style, zorder=2,
    )
    ax.add_patch(arrow)

# side annotations
ax.text(0.02, -0.58, "Machine outputs\nare candidates,\nnever facts", fontsize=8,
        color="#8B0000", rotation=90, va="center", ha="center")
ax.text(0.98, -0.76, "Every value:\nconfirmed or\ncorrected by a human", fontsize=8,
        color="#8B0000", rotation=270, va="center", ha="center")

plt.savefig(
    r"D:\Claude_Design\auto-decte-paper\figures\architecture.png",
    dpi=200, bbox_inches="tight", facecolor="white",
)
print("figure saved")
