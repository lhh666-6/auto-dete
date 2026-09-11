"""Revised Figures 3 and 4 for the r22 review-response revision.

Changes requested by the 2026-09-08 review:
* Figure 3 (cost-characterization): enlarge ordinary labels, drop the 36 dense
  in-cell values (they remain in the trace table) and add a colorbar.
* Figure 4 (behavior-vs-authority): report the strict-trajectory and
  endpoint-completion task verdicts separately (R4); move the rule-hit
  acknowledgment counts to the manuscript table (R2/R3) and keep the host
  operation panel.

Both figures use the same fixed 432 pt (6 in) canvas as the refined Figures 1
and 2, so a 9.5 pt label renders at about 8.2 pt in the 0.96-textwidth
placement instead of the 4-5.8 pt measured in the v8 figures.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_figures as bf  # noqa: E402
from figure_narrative_data import load_cost_extensions  # noqa: E402

CATEGORICAL = bf.CATEGORICAL
SEQUENTIAL = bf.SEQUENTIAL
BLACK = bf.BLACK
DARK_GREY = bf.DARK_GREY
GREY = bf.GREY
LIGHT_BLUE = bf.LIGHT_BLUE
LIGHT_GREEN = bf.LIGHT_GREEN

CANVAS_INCHES = 6.0  # same fixed canvas as figures 1--2 (432 pt)
FONT = {
    "base": 9.5,
    "title": 10.0,
    "label": 9.5,
    "tick": 9.0,
    "annot": 9.0,
    "legend": 8.5,
    "note": 9.0,
}


def _qa(fig: plt.Figure, stem: Path) -> dict[str, object]:
    """Fail loudly on clipped or overlapping text instead of shipping it."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    items: list[tuple[object, bool]] = [(text, False) for text in fig.texts]
    for ax in fig.axes:
        items.extend((text, False) for text in ax.texts)
        items.extend((text, False) for text in (ax.title, ax.xaxis.label, ax.yaxis.label))
        legend = ax.get_legend()
        if legend is not None:
            items.extend((text, False) for text in legend.get_texts())
            if legend.get_title() is not None:
                items.append((legend.get_title(), False))
        # Tick labels outside the current view are clipped by matplotlib; skip them.
        for axis in (ax.xaxis, ax.yaxis):
            for tick in axis.get_major_ticks():
                label = tick.label1
                low, high = sorted(axis.get_view_interval())
                if ax.axison and axis.get_visible() and label.get_visible() and low <= tick.get_loc() <= high and label.get_text().strip():
                    items.append((label, True))
    def _intersect(a, b) -> bool:
        return not (a.x1 <= b.x0 or b.x1 <= a.x0 or a.y1 <= b.y0 or b.y1 <= a.y0)

    axes_boxes = [ax.get_window_extent(renderer) for ax in fig.axes]
    errors: list[str] = []
    sizes: list[float] = []
    visible: list[object] = []
    for text, is_tick in items:
        if not text.get_text().strip():
            continue
        box = text.get_window_extent(renderer)
        sizes.append(float(text.get_fontsize()))
        visible.append(text)
        if box.x0 < -1 or box.y0 < -1 or box.x1 > fig.bbox.x1 + 1 or box.y1 > fig.bbox.y1 + 1:
            errors.append(f"outside figure: {text.get_text()!r}")
    for index, first in enumerate(visible):
        first_box = first.get_window_extent(renderer)
        for second in visible[index + 1 :]:
            second_box = second.get_window_extent(renderer)
            if not _intersect(first_box, second_box):
                continue
            overlap_w = min(first_box.x1, second_box.x1) - max(first_box.x0, second_box.x0)
            overlap_h = min(first_box.y1, second_box.y1) - max(first_box.y0, second_box.y0)
            area = overlap_w * overlap_h
            smaller = min(first_box.width * first_box.height, second_box.width * second_box.height)
            if smaller > 0 and area / smaller > 0.12:
                errors.append(
                    f"text overlap: {first.get_text()!r} / {second.get_text()!r}"
                )
    if errors:
        raise ValueError(f"{stem.name}: " + "; ".join(errors))
    return {
        "canvas_pt": CANVAS_INCHES * 72,
        "text_count": len(sizes),
        "minimum_font_pt": min(sizes),
        "text_overlap_count": 0,
    }


def _export(fig: plt.Figure, stem: Path, *, title: str, description: str) -> dict[str, object]:
    qa = _qa(fig, stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    with mpl.rc_context({"savefig.bbox": None}):
        fig.savefig(stem.with_suffix(".pdf"), metadata={"Title": title, "Creator": "Auto-Decte figure revision"})
        fig.savefig(stem.with_suffix(".svg"))
        fig.savefig(stem.with_suffix(".png"), dpi=300)
    plt.close(fig)
    return qa


def build_cost_characterization(stem: Path) -> dict[str, object]:
    feature, optimized = load_cost_extensions()
    admission = sorted(feature["results"], key=lambda r: (r["fields"], r["changed"]))
    trace = optimized["results"]
    fig, axes = plt.subplots(2, 2, figsize=(CANVAS_INCHES, 5.2))
    fig.subplots_adjust(left=0.115, right=0.955, top=0.90, bottom=0.235, hspace=0.95, wspace=0.58)
    aa, ab, ac, ad = axes.flat
    x = np.arange(len(admission))
    labels = [f"{r['fields']}/{r['changed']}" for r in admission]
    aa.plot(x, [r["full_p50_ms"] for r in admission], color=CATEGORICAL[0], marker="o",
            markersize=3.2, linewidth=1.0, label="Full admission")
    aa.plot(x, [r["materialization_p50_ms"] for r in admission], color=CATEGORICAL[2],
            marker="s", markersize=3.2, linewidth=1.0, label="Equivalent materialization")
    aa.set_title("a  Equivalent admission", loc="left", fontweight="bold",
                 fontsize=FONT["title"])
    aa.set_ylabel("Median latency (ms)", fontsize=FONT["label"])
    aa.set_ylim(0, 225)
    aa.legend(loc="upper left", fontsize=FONT["legend"], handlelength=1.4)
    ab.bar(x, [r["paired_mean_validation_and_planning_delta_ms"] for r in admission],
           color=CATEGORICAL[0], width=0.58)
    ab.set_title("b  Paired gap", loc="left", fontweight="bold", fontsize=FONT["title"])
    ab.set_ylabel("Paired mean difference (ms)", fontsize=FONT["label"])
    ab.set_ylim(0, 215)
    ab.text(0.02, 0.95, "validation/planning\n+ path differences", transform=ab.transAxes,
            va="top", fontsize=FONT["legend"], color=DARK_GREY)
    for ax in (aa, ab):
        ax.set_xticks(x, labels, rotation=90, fontsize=FONT["tick"])
        ax.tick_params(axis="y", labelsize=FONT["tick"])
        ax.set_xlabel("Total/changed fields", fontsize=FONT["label"])
        ax.grid(axis="y", color="#e5e5e5", linewidth=0.45)
        ax.set_axisbelow(True)

    fields = [1, 8, 32, 128]
    combinations = [(v, r) for v in (1, 10, 100) for r in (1, 100, 1000)]
    lookup = {(r["fields"], r["versions"], r["records"]): r for r in trace}
    matrix = np.array(
        [[lookup[(f, v, r)]["current_p50_ms"] for v, r in combinations] for f in fields]
    )
    cmap = mpl.colors.LinearSegmentedColormap.from_list("optimized-trace", SEQUENTIAL)
    mesh = ac.pcolormesh(np.arange(10), np.arange(5), matrix, cmap=cmap,
                         vmin=0, vmax=55, edgecolors="white", linewidth=0.6)
    ac.set_ylim(4, 0)
    ac.set_yticks(np.arange(4) + 0.5, [str(f) for f in fields], fontsize=FONT["tick"])
    ac.set_xticks(np.arange(9) + 0.5, [f"{v}/{r}" for v, r in combinations],
                  rotation=90, fontsize=FONT["tick"])
    ac.set_xlabel("Versions/records", fontsize=FONT["label"])
    ac.set_ylabel("Fields", fontsize=FONT["label"])
    ac.set_title("c  Optimized trace", loc="left", fontweight="bold",
                 fontsize=FONT["title"], pad=18)
    ac.text(0, 1.06, "p50 ms; 12 SQL statements; values in supplement",
            transform=ac.transAxes, fontsize=FONT["legend"], color=DARK_GREY)
    colorbar = fig.colorbar(mesh, ax=ac, fraction=0.040, pad=0.02, aspect=18)
    colorbar.set_label("p50 (ms)", fontsize=FONT["legend"])
    colorbar.ax.tick_params(labelsize=FONT["tick"])

    for f, color, marker in zip(fields, CATEGORICAL[:4], ("o", "s", "^", "D"), strict=True):
        cells = [r for r in trace if r["fields"] == f]
        ad.scatter([r["baseline_p50_ms"] for r in cells],
                   [r["current_p50_ms"] for r in cells],
                   s=22, color=color, marker=marker,
                   label=f"{f} field" + ("s" if f != 1 else ""),
                   edgecolors="white", linewidth=0.3)
    ad.plot([3, 10000], [3, 10000], linestyle=":", color=GREY, linewidth=1.0)
    ad.set_xscale("log")
    ad.set_yscale("log")
    ad.set_xlim(3, 10000)
    ad.set_ylim(3, 10000)
    ad.set_xticks([10, 100, 1000, 10000], ["10", "100", "1,000", "10,000"], fontsize=FONT["tick"])
    ad.set_yticks([10, 100, 1000, 10000], ["10", "100", "1,000", "10,000"], fontsize=FONT["tick"])
    ad.set_xlabel("Historical p50 (ms)", fontsize=FONT["label"])
    ad.set_ylabel("Optimized p50 (ms)", fontsize=FONT["label"])
    ad.set_title("d  All 36 trace cells", loc="left", fontweight="bold",
                 fontsize=FONT["title"])
    ad.legend(loc="upper left", ncol=2, handletextpad=0.3, columnspacing=0.6,
              fontsize=FONT["legend"])
    ad.text(0.99, 0.06, "dotted: equal latency", transform=ad.transAxes,
            ha="right", fontsize=FONT["legend"], color=DARK_GREY)
    fig.text(0.5, 0.015,
             "Frozen grid: 2,000 admission pairs; 7,200 observations per trace execution; "
             "every frozen cell is shown.",
             ha="center", va="bottom", fontsize=FONT["note"], color=DARK_GREY)
    return _export(
        fig, stem,
        title="Equivalent admission and optimized reverse trace",
        description=(
            "All ten persistence-equivalent admission cells and all 36 optimized trace cells, "
            "with paired admission differences and a historical trace comparison. No new "
            "experiment was run."
        ),
    )


def build_behavior_authority(stats_path: Path, stem: Path) -> dict[str, object]:
    data = json.loads(stats_path.read_text(encoding="utf-8"))
    rows = {row["model_config_id"]: row for row in data["agent_behavior"]}
    configs = ["D1", "G1", "G2"]
    colors = {"D1": CATEGORICAL[3], "G1": CATEGORICAL[0], "G2": CATEGORICAL[4]}
    markers = {"D1": "s", "G1": "o", "G2": "^"}

    fig = plt.figure(figsize=(CANVAS_INCHES, 3.3))
    grid = fig.add_gridspec(
        1, 2, width_ratios=[1.45, 1.0],
        left=0.155, right=0.985, top=0.80, bottom=0.30, wspace=0.22,
    )
    ax_task = fig.add_subplot(grid[0, 0])
    ax_authority = fig.add_subplot(grid[0, 1])

    metrics = [
        ("Benign task\ncompletion", "benign_completion_strict", "benign_completion_endpoint"),
        ("Stale\nrecovery", "recovery_strict", "recovery_endpoint"),
    ]
    y_base = np.arange(len(metrics))[::-1] * 1.0
    offsets = {"D1": -0.24, "G1": 0.0, "G2": 0.24}
    for model_id in configs:
        row = rows[model_id]
        color, marker = colors[model_id], markers[model_id]
        for y, (_, strict_field, endpoint_field) in zip(y_base, metrics, strict=True):
            strict_count, strict_den = bf._parse_fraction(row[strict_field])
            endpoint_count, endpoint_den = bf._parse_fraction(row[endpoint_field])
            y_value = y + offsets[model_id]
            x_strict = 100 * strict_count / strict_den
            x_endpoint = 100 * endpoint_count / endpoint_den
            ax_task.plot([x_strict, x_endpoint], [y_value, y_value],
                         color=color, linewidth=1.5, zorder=2)
            ax_task.scatter([x_strict], [y_value], facecolor="white", edgecolor=color,
                            marker=marker, s=34, linewidth=1.2, zorder=3)
            ax_task.scatter([x_endpoint], [y_value], color=color, marker=marker,
                            s=34, edgecolor="white", linewidth=0.4, zorder=4,
                            label=model_id if y == y_base[0] else None)
            if y == y_base[0]:
                ax_task.annotate(
                    model_id, (52.0, y_value), ha="left", va="center",
                    fontsize=FONT["annot"], color=color, fontweight="bold",
                )
            ax_task.annotate(
                f"{strict_count}/{strict_den}", (x_strict, y_value),
                xytext=(-5, 0), textcoords="offset points", ha="right", va="center",
                fontsize=FONT["annot"], color=color,
            )
            ax_task.annotate(
                f"{endpoint_count}/{endpoint_den}", (x_endpoint, y_value),
                xytext=(5, 0), textcoords="offset points", ha="left", va="center",
                fontsize=FONT["annot"], color=color, fontweight="bold",
            )
    ax_task.set_yticks(y_base, [label for label, _, _ in metrics], fontsize=FONT["label"])
    ax_task.set_ylim(-0.55, len(metrics) - 0.35)
    ax_task.set_xlim(50, 116)
    ax_task.set_xticks([60, 70, 80, 90, 100])
    ax_task.tick_params(axis="both", labelsize=FONT["tick"])
    ax_task.set_xlabel("Observed rate (%)", fontsize=FONT["label"])
    ax_task.set_title("a  Task endpoints", loc="left", fontweight="bold",
                      fontsize=FONT["title"])
    for guide in (60, 70, 80, 90, 100):
        ax_task.axvline(guide, color="#E5E5E5", linewidth=0.45, zorder=0)


    ax_authority.set_axis_off()
    ax_authority.set_title("b  Host operations", loc="left", fontweight="bold",
                           fontsize=FONT["title"])
    for bottom, heading, detail, value, color, fill in (
        (0.52, "Invalid-tuple admission calls", "A2--A9: admission invoked",
         data["host_operations"]["fixed_invalid_tuple_admission_calls"],
         CATEGORICAL[0], LIGHT_BLUE),
        (0.02, "Unavailable capability", "A1/A10: no admission call",
         data["host_operations"]["capability_unavailable_checks"],
         CATEGORICAL[2], LIGHT_GREEN),
    ):
        ax_authority.add_patch(bf.FancyBboxPatch((0.01, bottom), 0.98, 0.43,
            boxstyle="round,pad=0.008", transform=ax_authority.transAxes,
            facecolor=fill, edgecolor="none"))
        ax_authority.text(0.06, bottom + 0.35, heading, transform=ax_authority.transAxes,
            fontsize=FONT["annot"], fontweight="bold", color=color)
        ax_authority.text(0.06, bottom + 0.185, value, transform=ax_authority.transAxes,
            fontsize=17, fontweight="bold", color=color)
        ax_authority.text(0.06, bottom + 0.10, "unauthorized mutations / checks",
            transform=ax_authority.transAxes, fontsize=FONT["legend"], color=BLACK)
        ax_authority.text(0.06, bottom + 0.035, detail, transform=ax_authority.transAxes,
            fontsize=FONT["legend"], color=DARK_GREY)

    fig.text(
        0.50, 0.105,
        "hollow = strict trajectory; filled = endpoint. Strict 320/335; endpoint 331/335.",
        ha="center", va="bottom", fontsize=FONT["note"], color=DARK_GREY,
    )
    fig.text(
        0.50, 0.035,
        "Recovery strict 75/82, endpoint 82/82. Runtime failures: D1 76/420; G1 4/420; G2 13/420.",
        ha="center", va="bottom", fontsize=FONT["note"], color=DARK_GREY,
    )
    return _export(
        fig, stem,
        title="Task endpoints and authority invariance",
        description=(
            "Panel a contrasts the deposited strict tool-call-trajectory verdict with the "
            "endpoint-completion sensitivity verdict for benign completion and stale-state "
            "recovery in three qualified configurations. Panel b separately shows 720 fixed "
            "invalid-tuple admission calls and 179 capability-unavailable checks, each with zero "
            "unauthorized mutations. Ninety-three runtime failures are reported separately."
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stats", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_root.resolve()
    audit = {
        "cost-characterization": build_cost_characterization(output / "cost-characterization"),
        "behavior-vs-authority": build_behavior_authority(
            args.stats.resolve(), output / "behavior-vs-authority"
        ),
    }
    (output / "figure-font-audit-revised.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
