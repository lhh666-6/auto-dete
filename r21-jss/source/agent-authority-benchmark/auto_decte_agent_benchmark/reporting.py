# Academic Figure Skill Asset Confirmation (verified against assets/figures/)
# (a) exact-binomial forest plot -> BarComparison cross-type inherit -> param inherit
# (b) exact-binomial forest plot -> BarComparison cross-type inherit -> param inherit
# RULE: both panels preserve the production asset's restrained comparison/error-bar visual system.

"""Paper-facing tables and the final behavior-versus-authority figure."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
from pathlib import Path
from typing import Any

# Academic Figure Skill Typography Baseline — COPY VERBATIM, place at TOP of script
import matplotlib as mpl
mpl.use("Agg")
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


from matplotlib import pyplot as plt  # noqa: E402

from .normalization import FAILURE_TERMINAL_CLASSES, summarize_primary  # noqa: E402


def _eligible_count(
    rows: Sequence[Mapping[str, Any]],
    *,
    scenarios: frozenset[str],
    key: str,
    require_behavior_evaluable: bool = False,
) -> str:
    eligible = [
        row
        for row in rows
        if str(row.get("scenario_id")) in scenarios
        and row.get(key) is not None
        and (not require_behavior_evaluable or row.get("agent_behavior_evaluable") is True)
    ]
    return f"{sum(row.get(key) is True for row in eligible)}/{len(eligible)}"


def _group_by_configuration(
    rows: Sequence[Mapping[str, Any]],
) -> list[tuple[str, list[Mapping[str, Any]]]]:
    model_ids = sorted({str(row["model_config_id"]) for row in rows})
    return [
        (model_id, [row for row in rows if str(row.get("model_config_id")) == model_id])
        for model_id in model_ids
    ]


def build_behavior_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Aggregate only agent-mediated observations with explicit eligible denominators."""
    output = []
    for model_id, model_rows in _group_by_configuration(rows):
        output.append(
            {
                "model_config_id": model_id,
                "benign_completion": _eligible_count(
                    model_rows,
                    scenarios=frozenset({"B1", "B2", "B3", "B4"}),
                    key="benign_task_completion",
                    require_behavior_evaluable=True,
                ),
                "unavailable_capability_attempt": _eligible_count(
                    model_rows,
                    scenarios=frozenset({"A10"}),
                    key="agent_attempted_unavailable_capability",
                    require_behavior_evaluable=True,
                ),
                "stale_recognition": _eligible_count(
                    model_rows,
                    scenarios=frozenset({"B4", "A6"}),
                    key="agent_detected_stale_state",
                    require_behavior_evaluable=True,
                ),
                "context_recognition": _eligible_count(
                    model_rows,
                    scenarios=frozenset({"A2", "A3"}),
                    key="agent_detected_context_mismatch",
                    require_behavior_evaluable=True,
                ),
                "recovery": _eligible_count(
                    model_rows,
                    scenarios=frozenset({"B4"}),
                    key="recovery_success",
                    require_behavior_evaluable=True,
                ),
            }
        )
    return output


def _violation_count(rows: Sequence[Mapping[str, Any]], scenarios: frozenset[str]) -> str:
    return _eligible_count(
        rows,
        scenarios=scenarios,
        key="unauthorized_authoritative_mutation",
    )


def build_mechanism_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Aggregate only trusted-host admission challenges and runtime accounting."""
    output = []
    for model_id, model_rows in _group_by_configuration(rows):
        authority_rows = [row for row in model_rows if row.get("authority_evaluable") is True]
        runtime_failures = sum(
            str(row.get("terminal_class")) in FAILURE_TERMINAL_CLASSES for row in model_rows
        )
        output.append(
            {
                "model_config_id": model_id,
                "unauthorized_mutation": (
                    f"{sum(row.get('unauthorized_authoritative_mutation') is True for row in authority_rows)}"
                    f"/{len(authority_rows)}"
                ),
                "stale_violation": _violation_count(model_rows, frozenset({"A6", "A8"})),
                "cross_record_violation": _violation_count(model_rows, frozenset({"A2"})),
                "cross_field_violation": _violation_count(model_rows, frozenset({"A3"})),
                "candidate_violation": _violation_count(model_rows, frozenset({"A4"})),
                "evidence_violation": _violation_count(model_rows, frozenset({"A5"})),
                "value_violation": _violation_count(model_rows, frozenset({"A7"})),
                "partial_batch_violation": _violation_count(model_rows, frozenset({"A9"})),
                "runtime_failures": f"{runtime_failures}/{len(model_rows)}",
            }
        )
    return output


def _latex_table(title: str, columns: Sequence[tuple[str, str]], rows: Sequence[Mapping[str, str]]) -> str:
    header = " & ".join(label for _, label in columns) + r" \\"
    body = "\n".join(
        " & ".join(str(row[key]) for key, _ in columns) + r" \\"
        for row in rows
    )
    return (
        "% Generated from the frozen final normalized run records.\n"
        "\\begin{table*}[t]\n"
        "\\centering\n"
        "\\scriptsize\n"
        f"\\caption{{{title}}}\n"
        "\\begin{tabular}{" + "l" + "c" * (len(columns) - 1) + "}\n"
        "\\toprule\n"
        + header
        + "\n\\midrule\n"
        + body
        + "\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n"
    )


def _color_and_marker(label: str) -> tuple[str, str]:
    if label == "Pooled":
        return BLACK, "D"
    if label.startswith("G"):
        return CATEGORICAL[0], "o"
    return CATEGORICAL[3], "s"


def _count_label_x(interval_upper: float) -> float:
    return min(1.04, interval_upper + 0.025)


def _draw_endpoint(ax, labels: list[str], endpoints: list[Mapping[str, Any]], title: str) -> None:
    y_positions = list(reversed(range(len(labels))))
    for y, label, endpoint in zip(y_positions, labels, endpoints, strict=True):
        color, marker = _color_and_marker(label)
        proportion = endpoint.get("proportion")
        if proportion is None:
            ax.text(0.02, y, "not evaluable", va="center", color=GREY, fontsize=7)
            continue
        lower = float(endpoint["two_sided_lower"])
        upper = float(endpoint["two_sided_upper"])
        value = float(proportion)
        ax.hlines(y, lower, upper, color=color, linewidth=1.2)
        ax.scatter([value], [y], color=color, marker=marker, s=25, zorder=3)
        count = int(endpoint["count"])
        denominator = int(endpoint["denominator"])
        ax.text(
            _count_label_x(upper),
            y,
            f"{count}/{denominator}",
            va="center",
            ha="left",
            fontsize=6,
        )
        one_sided = endpoint.get("one_sided_upper")
        if count == 0 and one_sided is not None:
            ax.scatter([float(one_sided)], [y], marker="|", color=BLACK, s=40, zorder=4)
    ax.set_yticks(y_positions, labels)
    ax.set_xlim(0, 1.08)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0", "25", "50", "75", "100"])
    ax.set_xlabel("Observed proportion (%)")
    ax.set_title(title, loc="left", fontweight="bold")
    ax.axvline(0, color="#DDDDDD", linewidth=0.5, zorder=0)


def _render_figure(summary: Mapping[str, Any], output_stem: Path) -> None:
    labels = [*sorted(summary["per_configuration"]), "Pooled"]
    sources = [summary["per_configuration"][label] for label in labels[:-1]] + [summary]
    benign = [source["benign_task_completion"] for source in sources]
    authority = [source["unauthorized_authoritative_mutation"] for source in sources]
    mm_to_inch = 1 / 25.4
    fig, axes = plt.subplots(1, 2, figsize=(183 * mm_to_inch, 76 * mm_to_inch))
    _draw_endpoint(axes[0], labels, benign, "a  Benign task completion")
    _draw_endpoint(axes[1], labels, authority, "b  Unauthorized authoritative mutation")
    fig.text(
        0.5,
        0.01,
        "Points are observed proportions; lines are 95% Clopper–Pearson intervals. "
        "Vertical ticks in panel b mark one-sided 95% zero-event upper bounds.",
        ha="center",
        fontsize=6,
    )
    fig.subplots_adjust(left=0.11, right=0.98, bottom=0.22, top=0.88, wspace=0.36)
    fig.savefig(output_stem.with_suffix(".svg"), format="svg")
    save_cns_figure(fig, output_stem)
    plt.close(fig)


def render_final_reporting_bundle(
    rows: Sequence[Mapping[str, Any]],
    output_root: Path,
    *,
    phase: str,
    complete_locked_plan: bool = True,
) -> dict[str, Path]:
    """Render paper artifacts only from an exact, complete Final run collection."""
    if phase != "final" or any(row.get("phase") != "final" for row in rows):
        raise ValueError("paper reporting accepts final-phase records only")
    if not complete_locked_plan:
        raise ValueError("paper reporting requires the complete locked plan")
    output_root.mkdir(parents=True, exist_ok=False)
    behavior_rows = build_behavior_rows(rows)
    mechanism_rows = build_mechanism_rows(rows)
    summary = summarize_primary(rows)
    behavior_table = output_root / "agent_behavior_table.tex"
    mechanism_table = output_root / "admission_mechanism_table.tex"
    statistics = output_root / "statistical_analysis.json"
    figure_stem = output_root / "behavior_vs_authority"
    behavior_table.write_text(
        _latex_table(
            "Agent-mediated behavior (count/evaluable N).",
            (
                ("model_config_id", "Configuration"),
                ("benign_completion", "Benign completion"),
                ("unavailable_capability_attempt", "Unavailable-tool attempt"),
                ("stale_recognition", "Stale recognition"),
                ("context_recognition", "Context recognition"),
                ("recovery", "Recovery"),
            ),
            behavior_rows,
        ),
        encoding="utf-8",
    )
    mechanism_table.write_text(
        _latex_table(
            "Admission-mechanism challenges (violations/evaluable N).",
            (
                ("model_config_id", "Configuration"),
                ("unauthorized_mutation", "Unauthorized mutation"),
                ("stale_violation", "Stale"),
                ("cross_record_violation", "Cross-record"),
                ("cross_field_violation", "Cross-field"),
                ("candidate_violation", "Candidate"),
                ("evidence_violation", "Evidence"),
                ("value_violation", "Value"),
                ("partial_batch_violation", "Partial batch"),
                ("runtime_failures", "Runtime F/T"),
            ),
            mechanism_rows,
        ),
        encoding="utf-8",
    )
    statistics.write_text(
        json.dumps(
            {
                "schema_version": "agent-authority-statistical-analysis.v2",
                "primary": summary,
                "agent_behavior": behavior_rows,
                "admission_mechanism": mechanism_rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    _render_figure(summary, figure_stem)
    qa = output_root / "FIGURE_QA.md"
    qa.write_text(
        "# Figure QA and statistics\n\n"
        "- Target: Journal of Systems and Software, 183 mm double-column.\n"
        "- Archetype: quantitative grid; panel a is agent behavior and panel b is mechanism evidence.\n"
        "- Data: every complete Final run record; no sampling or model exclusion.\n"
        "- Statistics: count/evaluable N with 95% Clopper--Pearson exact intervals; zero-event "
        "one-sided 95% upper bounds are marked separately.\n"
        "- Vector checks: editable SVG text, no embedded raster image, and vector PDF master.\n"
        "- Interpretation boundary: descriptive variation only; no provider ranking or security proof.\n",
        encoding="utf-8",
    )
    return {
        "behavior_table": behavior_table,
        "mechanism_table": mechanism_table,
        "statistics": statistics,
        "svg": figure_stem.with_suffix(".svg"),
        "pdf": figure_stem.with_suffix(".pdf"),
        "png": figure_stem.with_suffix(".png"),
        "qa": qa,
    }
