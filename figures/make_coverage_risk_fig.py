"""Coverage vs selective-risk curve (Fig. 2) from the abstention sweep."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "DejaVu Sans"

# Measured sweep (frozen): tau -> coverage, selective_risk, accepted_acc
TAUS = [0.000, 0.005, 0.010, 0.020, 0.030, 0.050, 0.080, 0.120]
COVERAGE = [1.000, 0.967, 0.952, 0.937, 0.903, 0.614, 0.411, 0.105]
RISK = [0.062, 0.053, 0.052, 0.053, 0.054, 0.000, 0.000, 0.000]
ACC = [0.938, 0.947, 0.948, 0.947, 0.946, 1.000, 1.000, 1.000]

fig, ax1 = plt.subplots(figsize=(6.4, 4.2))

ax1.plot(COVERAGE, RISK, "o-", color="#c2410c", linewidth=1.8, zorder=3)
ax1.set_xlabel("Coverage (fraction of cells auto-accepted)")
ax1.set_ylabel("Selective risk (1 - accepted accuracy)", color="#c2410c")
ax1.set_xlim(0, 1.05)
ax1.set_ylim(-0.005, 0.075)
ax1.tick_params(axis="y", labelcolor="#c2410c")
ax1.grid(alpha=0.25, linewidth=0.5)

# annotate operating point and conservative point
ax1.annotate("operating $\\tau{=}0.02$", xy=(0.937, 0.053), xytext=(0.62, 0.062),
             arrowprops=dict(arrowstyle="->", color="#334155"), fontsize=8, color="#334155")
ax1.annotate("$\\tau{=}0.05$: zero observed\nsilent error", xy=(0.614, 0.0), xytext=(0.30, 0.028),
             arrowprops=dict(arrowstyle="->", color="#334155"), fontsize=8, color="#334155")

# accepted accuracy on a second axis
ax2 = ax1.twinx()
ax2.plot(COVERAGE, ACC, "s--", color="#1d4ed8", linewidth=1.4, alpha=0.8)
ax2.set_ylabel("Accepted accuracy", color="#1d4ed8")
ax2.set_ylim(0.90, 1.02)
ax2.tick_params(axis="y", labelcolor="#1d4ed8")

plt.tight_layout()
plt.savefig(r"D:\Claude_Design\auto-decte-paper\figures\coverage_risk.png",
            dpi=220, bbox_inches="tight", facecolor="white")
print("figure saved")
