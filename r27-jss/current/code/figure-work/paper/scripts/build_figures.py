# Asset Confirmation Table
# | Figure | Native asset match | Decision |
# | admission-workflow | Author-approved Canva composition matches the locked contract | Reconstruct the approved composition as one-tool vector artwork from verified text semantics; embed no raster payload |
# | evidence-chain | No evidence-layer schematic template is available | Build one-tool vector schematic from frozen lineage semantics |
# | cost-characterization | LineTrend/heatmap are only pattern-level references; neither matches the 10/36/3 mixed grid | Param inherit; plot every frozen cell in four non-redundant panels |
# | behavior-vs-authority | BarComparison is only a spacing/marker reference and is semantically incompatible with proportions and zero-event bounds | Param inherit; grouped dots plus separate host-operation counts |
# Neither the internal AI raster nor the Canva preview is an input to this script.

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
DIVERGING = ["#2166AC", "#F7F7F7", "#B2182B"]
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


import argparse
import hashlib
import json
from html import escape
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.ticker import NullLocator


MM_TO_INCH = 1.0 / 25.4
LIGHT_BLUE = "#EAF2F8"
LIGHT_ORANGE = "#FDF2E9"
LIGHT_GREEN = "#EAF4EA"
LIGHT_PURPLE = "#F3EEF7"
LIGHT_GREY = "#F4F4F4"
DARK_GREY = "#4D4D4D"
BORDER_BLUE = "#9ABBD4"
BORDER_PURPLE = "#B9A1C4"
BORDER_ORANGE = "#E6BD8B"
BORDER_GREEN = "#9ABDA4"
BORDER_RED = "#D7A2A9"
BORDER_NEUTRAL = "#B8B8B8"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_cost_summary(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the frozen 10/36/3 grid and return audit statistics."""
    if set(data) != {"admission", "trace", "storage"}:
        raise ValueError(f"Unexpected cost-summary keys: {sorted(data)}")

    admission = data["admission"]
    trace = data["trace"]
    storage = data["storage"]
    expected_admission = {
        (1, 1), (8, 1), (8, 4), (8, 8), (32, 1),
        (32, 4), (32, 32), (128, 1), (128, 4), (128, 128),
    }
    observed_admission = {(row["fields"], row["changed"]) for row in admission}
    if observed_admission != expected_admission or len(admission) != 10:
        raise ValueError("Admission grid is incomplete, duplicated, or unexpected")
    if any(row["trials"] != 200 for row in admission):
        raise ValueError("Admission trial count drifted from 200 per cell")

    expected_trace = {
        (fields, versions, records)
        for fields in (1, 8, 32, 128)
        for versions in (1, 10, 100)
        for records in (1, 100, 1000)
    }
    observed_trace = {
        (row["fields"], row["versions"], row["records"]) for row in trace
    }
    if observed_trace != expected_trace or len(trace) != 36:
        raise ValueError("Reverse-trace grid is incomplete, duplicated, or unexpected")
    if any(row["trials"] != 200 for row in trace):
        raise ValueError("Trace trial count drifted from 200 per cell")

    if [row["transitions"] for row in storage] != [1_000, 10_000, 100_000]:
        raise ValueError("Storage populations drifted from the frozen grid")
    for row in storage:
        if row["full"]["foreign_key_failures"] or row["lower"]["foreign_key_failures"]:
            raise ValueError("Storage measurement contains foreign-key failures")
        if any(
            row[side][name] != 0
            for side in ("full", "lower")
            for name in ("wal_bytes", "shm_bytes")
        ):
            raise ValueError("Storage measurement was not checkpoint-clean")
        if row["full"]["bytes"] - row["lower"]["bytes"] != row["incremental_bytes"]:
            raise ValueError("Storage incremental byte arithmetic does not reconcile")

    negative_cells = [row for row in admission if row["paired_mean_delta_ms"] < 0]
    if {(row["fields"], row["changed"]) for row in negative_cells} != {
        (128, 1), (128, 4)
    }:
        raise ValueError("Negative admission cells drifted from the frozen evidence")

    return {
        "admission_cells": len(admission),
        "admission_observations": sum(row["trials"] for row in admission),
        "negative_delta_cells": len(negative_cells),
        "admission_p50_min_ms": min(row["full_p50_ms"] for row in admission),
        "admission_p50_max_ms": max(row["full_p50_ms"] for row in admission),
        "paired_delta_min_ms": min(row["paired_mean_delta_ms"] for row in admission),
        "paired_delta_max_ms": max(row["paired_mean_delta_ms"] for row in admission),
        "trace_cells": len(trace),
        "trace_observations": sum(row["trials"] for row in trace),
        "trace_p50_min_ms": min(row["p50_ms"] for row in trace),
        "trace_p50_max_ms": max(row["p50_ms"] for row in trace),
        "trace_p95_max_ms": max(row["p95_ms"] for row in trace),
        "storage_populations": len(storage),
        "storage_incremental_bytes": [row["incremental_bytes"] for row in storage],
    }


def validate_agent_statistics(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and summarize the frozen repeated live-agent endpoints."""
    if data.get("schema_version") != "agent-authority-statistical-analysis.v2":
        raise ValueError("Unexpected agent-statistics schema")

    primary = data["primary"]
    configurations = primary["per_configuration"]
    if set(configurations) != {"D1", "G1", "G2"}:
        raise ValueError("Agent-statistics configuration set drifted")
    if sum(row["planned_executions"] for row in configurations.values()) != primary["planned_executions"]:
        raise ValueError("Planned-execution totals do not reconcile")
    if sum(row["runtime_failures"] for row in configurations.values()) != primary["runtime_failures"]:
        raise ValueError("Runtime-failure totals do not reconcile")

    behavior_rows = {
        row["model_config_id"]: row for row in data["agent_behavior"]
    }
    mechanism_rows = {
        row["model_config_id"]: row for row in data["admission_mechanism"]
    }
    if set(behavior_rows) != set(configurations) or set(mechanism_rows) != set(configurations):
        raise ValueError("Agent-statistics tables do not cover every configuration")

    violation_fields = (
        "candidate_violation",
        "cross_field_violation",
        "cross_record_violation",
        "evidence_violation",
        "partial_batch_violation",
        "stale_violation",
        "unauthorized_mutation",
        "value_violation",
    )
    for model_id, row in mechanism_rows.items():
        if any(not str(row[field]).startswith("0/") for field in violation_fields):
            raise ValueError(f"Observed mechanism violation for {model_id}")

    benign = primary["benign_task_completion"]
    authority = primary["unauthorized_authoritative_mutation"]
    behavior_counts = {
        model_id: (
            row["benign_completion"],
            row["context_recognition"],
            row["recovery"],
            row["stale_recognition"],
        )
        for model_id, row in behavior_rows.items()
    }
    return {
        "planned_executions": primary["planned_executions"],
        "runtime_failures": primary["runtime_failures"],
        "benign_completion": (benign["count"], benign["denominator"]),
        "unauthorized_mutation": (authority["count"], authority["denominator"]),
        "pooled_zero_event_upper": authority["one_sided_upper"],
        "behavior_counts": behavior_counts,
        "runtime_failure_counts": {
            model_id: row["runtime_failures"]
            for model_id, row in configurations.items()
        },
        "zero_event_upper": {
            model_id: row["unauthorized_authoritative_mutation"]["one_sided_upper"]
            for model_id, row in configurations.items()
        },
    }


def _box(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    *,
    facecolor: str = "white",
    edgecolor: str = DARK_GREY,
    linewidth: float = 0.8,
    fontsize: float = 7.0,
    weight: str = "normal",
    pad: float = 0.012,
) -> FancyBboxPatch:
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle=f"round,pad={pad}",
        transform=ax.transAxes,
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        clip_on=False,
    )
    ax.add_patch(patch)
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=BLACK,
        fontweight=weight,
        linespacing=1.15,
    )
    return patch


def _arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = DARK_GREY,
    style: str = "-|>",
    linewidth: float = 1.0,
    connectionstyle: str = "arc3,rad=0",
    linestyle: str = "solid",
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            transform=ax.transAxes,
            arrowstyle=style,
            mutation_scale=9,
            linewidth=linewidth,
            color=color,
            connectionstyle=connectionstyle,
            linestyle=linestyle,
            clip_on=False,
        )
    )


def _add_svg_accessibility(path: Path, title: str, description: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.find("<svg ")
    if start < 0:
        raise ValueError(f"No SVG root found in {path}")
    end = text.find(">", start)
    if end < 0:
        raise ValueError(f"Malformed SVG root in {path}")
    root = text[start:end]
    if "aria-labelledby=" not in root:
        root += ' role="img" aria-labelledby="figure-title figure-desc"'
    inserted = (
        root
        + ">\n<title id=\"figure-title\">"
        + escape(title)
        + "</title>\n<desc id=\"figure-desc\">"
        + escape(description)
        + "</desc>"
    )
    path.write_text(text[:start] + inserted + text[end + 1 :], encoding="utf-8")


def _save_submission_figure(
    fig: plt.Figure,
    stem: Path,
    *,
    title: str,
    description: str,
) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    save_cns_figure(fig, str(stem))
    svg_path = stem.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches="tight", dpi=300)
    _add_svg_accessibility(svg_path, title, description)
    plt.close(fig)


def build_admission_workflow(stem: Path) -> None:
    """Build Figure 1 independently from the locked textual contract."""
    fig, ax = plt.subplots(figsize=(183 * MM_TO_INCH, 82 * MM_TO_INCH))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    stages = [
        (0.025, 0.19, "1 · AI candidate", CATEGORICAL[0]),
        (0.255, 0.23, "2 · Human decision", CATEGORICAL[4]),
        (0.530, 0.25, "3 · Admission gate", CATEGORICAL_EXTENDED[9]),
        (0.825, 0.15, "4 · Successor", CATEGORICAL[2]),
    ]
    for x_stage, width, label, color in stages:
        ax.text(
            x_stage + width / 2, 0.925, label, transform=ax.transAxes,
            ha="center", va="center", fontsize=7.0,
            fontweight="bold", color=color,
        )
        ax.plot(
            [x_stage, x_stage + width], [0.885, 0.885],
            transform=ax.transAxes, color=color, linewidth=1.1,
        )

    _box(
        ax, 0.025, 0.39, 0.19, 0.39, "",
        facecolor=LIGHT_BLUE, edgecolor="none", linewidth=0.0,
    )
    ax.text(
        0.120, 0.690, "Candidate certificate c_i",
        transform=ax.transAxes, ha="center", va="center",
        fontsize=6.0, color=BLACK, fontweight="bold",
    )
    ax.text(
        0.120, 0.565,
        "record · field · evidence\nproducer · context\n\ncandidate value x_c\nexpected pre-version v",
        transform=ax.transAxes, ha="center", va="center",
        fontsize=5.8, color=BLACK, linespacing=1.15,
    )
    ax.text(
        0.12, 0.315, "non-authoritative · no direct write port",
        transform=ax.transAxes, ha="center", va="center",
        fontsize=5.3, color=DARK_GREY,
    )

    ax.add_patch(FancyBboxPatch(
        (0.255, 0.32), 0.23, 0.50, boxstyle="round,pad=0.010",
        transform=ax.transAxes, facecolor=LIGHT_PURPLE,
        edgecolor="none", linewidth=0.0, clip_on=False,
    ))
    ax.text(
        0.37, 0.785, "bound to c_i + context",
        transform=ax.transAxes, ha="center", va="center",
        fontsize=5.2, color=DARK_GREY,
    )
    _box(
        ax, 0.278, 0.675, 0.184, 0.075,
        "Accept · x_a = x_c",
        facecolor="white", edgecolor="none",
        linewidth=0.0,
        fontsize=5.9, weight="bold",
    )
    _box(
        ax, 0.272, 0.485, 0.196, 0.135,
        "Correction\nx_a ≠ x_c\ncandidate retained",
        facecolor="#E9DFF0", edgecolor="none",
        linewidth=0.0, fontsize=6.0, weight="bold",
    )
    _box(
        ax, 0.278, 0.365, 0.184, 0.065,
        "Reject",
        facecolor="white", edgecolor="none",
        linewidth=0.0,
        fontsize=5.9, weight="bold",
    )

    ax.add_patch(FancyBboxPatch(
        (0.530, 0.34), 0.25, 0.46, boxstyle="round,pad=0.012",
        transform=ax.transAxes, facecolor=LIGHT_ORANGE,
        edgecolor="none", linewidth=0.0, clip_on=False,
    ))
    ax.text(
        0.655, 0.755, "all distinctions + policy must hold",
        transform=ax.transAxes, ha="center", va="center",
        fontsize=5.6, color=BLACK, fontweight="bold",
    )
    checks = [
        ("D_C", "candidate + context"),
        ("D_V", "x_c ↔ x_a attribution"),
        ("D_F", "current pre-version"),
        ("D_B", "complete batch"),
        ("D_S", "total source relation"),
    ]
    for index, (symbol, label) in enumerate(checks):
        y = 0.695 - 0.061 * index
        ax.text(
            0.555, y, symbol, transform=ax.transAxes,
            ha="left", va="center", fontsize=5.7,
            color=CATEGORICAL_EXTENDED[9], fontweight="bold",
        )
        ax.text(
            0.600, y, label, transform=ax.transAxes,
            ha="left", va="center", fontsize=5.5, color=BLACK,
        )
    _box(
        ax, 0.555, 0.350, 0.20, 0.055,
        "one version CAS",
        facecolor="white", edgecolor="none",
        linewidth=0.0,
        fontsize=5.8, weight="bold",
    )

    _box(
        ax, 0.825, 0.505, 0.15, 0.275,
        "Record v+1\ncomplete values\ntotal source map",
        facecolor=LIGHT_GREEN, edgecolor="none",
        linewidth=0.0, fontsize=6.1, weight="bold",
    )
    _box(
        ax, 0.825, 0.39, 0.15, 0.075,
        "audit + reverse trace",
        facecolor="white", edgecolor="none",
        linewidth=0.0, fontsize=5.4,
    )

    # The accepted path stays on one unobstructed horizontal channel.
    _arrow(ax, (0.215, 0.655), (0.255, 0.655), color=CATEGORICAL[0], linewidth=1.2)
    _arrow(ax, (0.485, 0.655), (0.530, 0.655), color=CATEGORICAL[4], linewidth=1.3)
    _arrow(ax, (0.780, 0.655), (0.825, 0.655), color=CATEGORICAL[2], linewidth=1.4)

    ax.add_patch(FancyBboxPatch(
        (0.255, 0.075), 0.720, 0.105, boxstyle="round,pad=0.008",
        transform=ax.transAxes, facecolor="#FAE9EC",
        edgecolor="none", linewidth=0.0, clip_on=False,
    ))
    ax.text(
        0.615, 0.127,
        "Reject or failed check → whole batch rejected; authoritative state stutters",
        transform=ax.transAxes, ha="center", va="center",
        fontsize=5.9, color=ACCENT_RED, fontweight="bold",
    )
    _arrow(
        ax, (0.370, 0.320), (0.370, 0.185), color=ACCENT_RED,
        linestyle="dashed", linewidth=1.0,
    )
    _arrow(
        ax, (0.655, 0.340), (0.655, 0.185), color=ACCENT_RED,
        linestyle="dashed", linewidth=1.0,
    )
    ax.text(
        0.975, 0.018, "authorization records responsibility, not factual truth",
        transform=ax.transAxes, ha="right", va="bottom",
        fontsize=5.2, color=DARK_GREY,
    )

    _save_submission_figure(
        fig,
        stem,
        title="Correction-aware authoritative-state admission workflow",
        description=(
            "A persisted AI candidate enters a candidate-bound human decision. Accept preserves "
            "the candidate value, Correction retains the candidate while authorizing a distinct "
            "value, and Reject stops admission. A trusted transaction checks five information "
            "classes and policy, performs one version compare-and-swap, and either commits a "
            "complete authoritative successor with total source attribution or leaves state unchanged."
        ),
    )


def build_evidence_chain(stem: Path) -> None:
    """Build Figure 2 as a contribution-led evidence hierarchy."""
    fig, ax = plt.subplots(figsize=(183 * MM_TO_INCH, 124 * MM_TO_INCH))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.text(
        0.50, 0.970, "Authoritative-state admission framework and evidence chain", transform=ax.transAxes,
        ha="center", va="center", fontsize=9.0, fontweight="bold", color=BLACK,
    )
    ax.text(
        0.50, 0.925,
        "Abstraction → Characterization → Realization → Behavioral validation",
        transform=ax.transAxes, ha="center", va="center",
        fontsize=6.7, color=DARK_GREY,
    )

    contributions = [
        (0.015, 0.180, "C1\nCorrection-aware\nadmission semantics", CATEGORICAL[0], LIGHT_BLUE),
        (0.225, 0.230, "C2 · Failure-distinguishability\ncharacterization", CATEGORICAL[4], LIGHT_PURPLE),
        (0.480, 0.300, "C3 · Formal & transactional realization", CATEGORICAL[2], LIGHT_GREEN),
        (0.805, 0.180, "C4 · Admission-boundary\nvalidation", CATEGORICAL_EXTENDED[9], LIGHT_ORANGE),
    ]
    for x, width, label, color, fill in contributions:
        ax.add_patch(FancyBboxPatch(
            (x, 0.815), width, 0.075, boxstyle="round,pad=0.006",
            transform=ax.transAxes, facecolor=fill, edgecolor="none",
            linewidth=0.0, clip_on=False,
        ))
        ax.text(
            x + width / 2, 0.853, label, transform=ax.transAxes,
            ha="center", va="center", fontsize=5.6,
            color=color, fontweight="bold", linespacing=1.15,
        )
        ax.plot(
            [x + 0.012, x + width - 0.012], [0.819, 0.819],
            transform=ax.transAxes, color=color, linewidth=1.05,
        )
    for left, right in zip(contributions[:-1], contributions[1:], strict=True):
        _arrow(
            ax, (left[0] + left[1] + 0.004, 0.853), (right[0] - 0.006, 0.853),
            color=DARK_GREY, linewidth=0.85,
        )

    evidence_cards = [
        (0.015, 0.330, 0.180, 0.405, "Semantic admission relation",
         "x_c ≠ x_a under Correction",
         "exact candidate → candidate-bound\nhuman authorization\n\nproposal origin ≠ value authority\n\ncandidate retained as\nnon-authoritative evidence",
         CATEGORICAL[0], LIGHT_BLUE),
        (0.225, 0.545, 0.230, 0.190, "Characterization result",
         "Proposition 1:\nConditional failure-distinguishability\n\nfive information classes",
         "paired safe/unsafe histories\nconditional irredundancy",
         CATEGORICAL[4], LIGHT_PURPLE),
        (0.225, 0.330, 0.230, 0.190, "Bounded relational evidence",
         "66/66 outcomes\nS1 + S2 profiles",
         "bounded separation / sensitivity",
         CATEGORICAL[4], "#F8F5FA"),
        (0.480, 0.545, 0.142, 0.190, "Projection evidence",
         "9 intended SAT\n20 mutants UNSAT", "",
         CATEGORICAL[2], LIGHT_GREEN),
        (0.638, 0.545, 0.142, 0.190, "Concrete /\ntransactional evidence",
         "35/35 catalogue cases\n354 Python tests", "rollback / concurrency covered",
         CATEGORICAL[2], LIGHT_GREEN),
        (0.480, 0.330, 0.300, 0.190, "Performance evidence",
         "2,000 admission pairs   ·   7,200 trace obs.",
         "frozen config-specific measurements",
         CATEGORICAL[2], "#F4F8F4"),
        (0.805, 0.330, 0.180, 0.405, "Repeated live-agent\nevidence",
         "1,260 planned runs\n\n0/720 admission calls\n0/179 capability checks\nunauthorized mutations\n\nhost-governed admission",
         "320/335 benign completion\nRuntime reliability: 93 failures\nreported separately",
         CATEGORICAL_EXTENDED[9], LIGHT_ORANGE),
    ]
    for x, y, width, height, title, metric, detail, color, fill in evidence_cards:
        ax.add_patch(FancyBboxPatch(
            (x, y), width, height, boxstyle="round,pad=0.008",
            transform=ax.transAxes, facecolor=fill, edgecolor="none",
            linewidth=0.0, clip_on=False,
        ))
        ax.text(
            x + width / 2, y + height - 0.042, title, transform=ax.transAxes,
            ha="center", va="center", fontsize=5.45,
            fontweight="bold", color=color,
        )
        metric_y = y + height * (0.55 if detail else 0.48)
        ax.text(
            x + width / 2, metric_y, metric, transform=ax.transAxes,
            ha="center", va="center", fontsize=5.35,
            fontweight="bold", color=BLACK, linespacing=1.18,
        )
        if detail:
            is_agent_card = title == "Repeated live-agent\nevidence"
            detail_color = CATEGORICAL_EXTENDED[9] if is_agent_card else DARK_GREY
            detail_y = y + (0.035 if title == "Characterization result" else 0.065)
            ax.text(
                x + width / 2, detail_y, detail, transform=ax.transAxes,
                ha="center", va="center", fontsize=4.55 if is_agent_card else 5.05,
                color=detail_color, linespacing=1.18,
                fontweight="normal",
            )

    for x, width, _, color, _ in contributions:
        _arrow(
            ax, (x + width / 2, 0.812), (x + width / 2, 0.748),
            color=color, linewidth=0.75,
        )

    ax.text(
        0.50, 0.285, "Evidence lineage backbone",
        transform=ax.transAxes, ha="center", va="center",
        fontsize=5.7, fontweight="bold", color=DARK_GREY,
    )
    provenance = [
        (0.130, "Frozen source"),
        (0.330, "Raw receipts"),
        (0.530, "Normalized inputs"),
        (0.730, "Final manifest"),
    ]
    provenance_width = 0.140
    for x, label in provenance:
        _box(
            ax, x, 0.220, provenance_width, 0.050, label,
            facecolor=LIGHT_GREY, edgecolor="none", linewidth=0.0,
            fontsize=5.15, weight="bold", pad=0.005,
        )
    for left, right in zip(provenance[:-1], provenance[1:], strict=True):
        _arrow(
            ax, (left[0] + provenance_width + 0.004, 0.245), (right[0] - 0.006, 0.245),
            color=GREY, linewidth=0.65,
        )
    ax.text(
        0.50, 0.192, "supports C2 / C3 / C4 evidence layers",
        transform=ax.transAxes, ha="center", va="center",
        fontsize=5.1, color=DARK_GREY,
    )

    ax.plot(
        [0.015, 0.985], [0.165, 0.165],
        transform=ax.transAxes, color="#D8D8D8", linewidth=0.45,
    )
    ax.text(
        0.015, 0.115, "Inference ceilings of\nevidence layers", transform=ax.transAxes,
        ha="left", va="center", fontsize=5.3, fontweight="bold", color=DARK_GREY,
    )
    ceiling_items = [
        (0.165, "C2", "conditional on the declared five failure families\nand observation model", CATEGORICAL[4]),
        (0.445, "C3", "bounded / finite / implementation-specific\nevidence", CATEGORICAL[2]),
        (0.725, "C4", "descriptive authority invariance over the\nexecuted benchmark population", CATEGORICAL_EXTENDED[9]),
    ]
    for x, label, ceiling, color in ceiling_items:
        ax.text(
            x, 0.125, label, transform=ax.transAxes,
            ha="left", va="center", fontsize=5.2, fontweight="bold", color=color,
        )
        ax.text(
            x, 0.082, ceiling, transform=ax.transAxes,
            ha="left", va="center", fontsize=5.0, color=DARK_GREY, linespacing=1.15,
        )

    _save_submission_figure(
        fig,
        stem,
        title="Authoritative-state admission framework and evidence chain",
        description=(
            "A four-stage contribution chain links correction-aware admission semantics to a "
            "five-class failure-distinguishability characterization, formal and transactional "
            "realization, and behavioral validation. Supporting cards report bounded relational, "
            "projection, concrete, performance, and repeated live-agent evidence. A separate "
            "evidence-lineage pipeline and three explicit inference ceilings constrain interpretation."
        ),
    )

def _compact_ms(value: float) -> str:
    if value >= 1_000:
        return f"{value / 1_000:.2f}k"
    if value >= 100:
        return f"{value:.0f}"
    if value >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def _parse_fraction(value: str) -> tuple[int, int]:
    count, denominator = value.split("/", maxsplit=1)
    return int(count), int(denominator)


def build_behavior_authority(data: dict[str, Any], stem: Path) -> None:
    """Contrast descriptive agent behavior with two observed host operations."""
    from figure_narrative_data import authority_operation_counts
    operations = authority_operation_counts()
    stats = validate_agent_statistics(data)
    behavior_rows = {
        row["model_config_id"]: row for row in data["agent_behavior"]
    }
    configurations = data["primary"]["per_configuration"]

    fig = plt.figure(figsize=(183 * MM_TO_INCH, 96 * MM_TO_INCH))
    grid = fig.add_gridspec(
        1, 2, width_ratios=[1.35, 1.10],
        left=0.105, right=0.985, top=0.84, bottom=0.24, wspace=0.30,
    )
    ax_behavior = fig.add_subplot(grid[0, 0])
    ax_authority = fig.add_subplot(grid[0, 1])

    model_styles = {
        "D1": (CATEGORICAL[3], "s", -0.20),
        "G1": (CATEGORICAL[0], "o", 0.00),
        "G2": (CATEGORICAL[4], "^", 0.20),
    }
    metrics = [
        ("Benign task\ncompletion", "benign_completion"),
        ("Context-mismatch\nacknowledgment", "context_recognition"),
        ("Recovery after\nstale state", "recovery"),
        ("Stale-state\nacknowledgment", "stale_recognition"),
    ]
    y_base = np.arange(len(metrics))[::-1]
    for model_id, (color, marker, offset) in model_styles.items():
        values = []
        labels = []
        for _, field in metrics:
            count, denominator = _parse_fraction(behavior_rows[model_id][field])
            values.append(100 * count / denominator)
            labels.append(f"{count}/{denominator}")
        y = y_base + offset
        ax_behavior.scatter(
            values, y, color=color, marker=marker, s=24,
            edgecolor="white", linewidth=0.35, zorder=3, label=model_id,
        )
        for x_value, y_value, count_label in zip(values, y, labels, strict=True):
            if x_value >= 91:
                ax_behavior.annotate(
                    count_label, (x_value, y_value), xytext=(-5, 0),
                    textcoords="offset points", ha="right", va="center", fontsize=5.4,
                )
            else:
                ax_behavior.annotate(
                    count_label, (x_value, y_value), xytext=(5, 0),
                    textcoords="offset points", ha="left", va="center", fontsize=5.4,
                )
    ax_behavior.set_yticks(y_base, [label for label, _ in metrics])
    ax_behavior.set_xlim(0, 105)
    ax_behavior.set_xticks([0, 25, 50, 75, 100])
    ax_behavior.set_xlabel("Observed rate (%)")
    ax_behavior.set_title("a  Behavioral variation", loc="left", fontweight="bold")
    ax_behavior.legend(bbox_to_anchor=(0.99, 1.13),
        loc="upper right", ncol=3,
        handletextpad=0.35, columnspacing=1.0, fontsize=6.4,
    )
    for guide in (25, 50, 75, 100):
        ax_behavior.axvline(guide, color="#E5E5E5", linewidth=0.45, zorder=0)
    ax_behavior.text(
        0.0, -0.22, "Pooled benign completion: 320/335 (95.52%)",
        transform=ax_behavior.transAxes, ha="left", va="top",
        fontsize=6.0, color=DARK_GREY,
    )

    ax_authority.set_axis_off()
    ax_authority.set_title("b  Host-operation outcomes", loc="left", fontweight="bold")
    for bottom, name, heading, detail, color, fill in (
        (0.52, "admission_calls", "Fixed invalid-tuple admission calls",
         "A2-A9: admission invoked", CATEGORICAL[0], LIGHT_BLUE),
        (0.02, "capability_checks", "Capability-unavailable checks",
         "A1/A10: no admission call", CATEGORICAL[2], LIGHT_GREEN),
    ):
        group = operations[name]
        ax_authority.add_patch(FancyBboxPatch((0.01, bottom), 0.98, 0.43,
            boxstyle="round,pad=0.008", transform=ax_authority.transAxes,
            facecolor=fill, edgecolor="none"))
        ax_authority.text(0.06, bottom + 0.35, heading, transform=ax_authority.transAxes,
            fontsize=6.6, fontweight="bold", color=color)
        ax_authority.text(0.06, bottom + 0.21,
            f"{group['violations']}/{group['count']}", transform=ax_authority.transAxes,
            fontsize=17, fontweight="bold", color=color)
        ax_authority.text(0.06, bottom + 0.12, "unauthorized mutations / checks",
            transform=ax_authority.transAxes, fontsize=6.4, color=BLACK)
        ax_authority.text(0.06, bottom + 0.04, detail, transform=ax_authority.transAxes,
            fontsize=6.2, color=DARK_GREY)

    fig.text(
        0.50, 0.035,
        "Runtime failures reported separately: D1 76/420; G1 4/420; G2 13/420. "
        "Behavioral endpoints are descriptive, not a provider ranking.",
        ha="center", va="bottom", fontsize=5.8, color=DARK_GREY,
    )
    _save_submission_figure(
        fig,
        stem,
        title="Behavioral variation with authority invariance",
        description=(
            "Panel a shows exact count-over-evaluable-denominator behavior rates for three "
            "qualified configurations. Panel b separately shows 720 fixed invalid-tuple admission "
            "calls and 179 capability-unavailable checks, each with zero unauthorized mutations. "
            "Ninety-three runtime failures are reported separately."
        ),
    )


def build_historical_cost_characterization(data: dict[str, Any], stem: Path) -> None:
    """Plot every frozen admission, trace, and storage cell."""
    admission = sorted(data["admission"], key=lambda row: (row["fields"], row["changed"]))
    trace = data["trace"]
    storage = data["storage"]

    fig = plt.figure(figsize=(183 * MM_TO_INCH, 124 * MM_TO_INCH))
    grid = fig.add_gridspec(
        2, 2, width_ratios=[1.08, 1.00], height_ratios=[0.88, 1.10],
        left=0.085, right=0.975, top=0.93, bottom=0.20,
        hspace=0.66, wspace=0.36,
    )
    ax_absolute = fig.add_subplot(grid[0, 0])
    ax_delta = fig.add_subplot(grid[0, 1])
    ax_trace = fig.add_subplot(grid[1, 0])
    ax_storage = fig.add_subplot(grid[1, 1])

    # Panels a-b: absolute latency and paired differences are intentionally separated.
    x = np.arange(len(admission))
    full = np.array([row["full_p50_ms"] for row in admission])
    lower = np.array([row["lower_p50_ms"] for row in admission])
    delta = np.array([row["paired_mean_delta_ms"] for row in admission])
    delta_ci = np.array([row["paired_mean_delta_95ci_ms"] for row in admission])
    yerr = np.vstack((delta - delta_ci[:, 0], delta_ci[:, 1] - delta))
    cell_labels = [f"{row['fields']}/{row['changed']}" for row in admission]

    ax_absolute.plot(
        x, full, color=CATEGORICAL[0], marker="o", markersize=3.4,
        linewidth=1.05, label="Full contract",
    )
    ax_absolute.plot(
        x, lower, color=GREY, marker="s", markersize=3.0,
        linewidth=0.95, linestyle="--", label="Lower baseline",
    )
    ax_absolute.set_ylim(0, 205)
    ax_absolute.set_yticks([0, 50, 100, 150, 200])
    ax_absolute.set_xticks(x)
    ax_absolute.set_xticklabels(cell_labels, rotation=42, ha="right")
    ax_absolute.set_xlabel("Total/changed fields")
    ax_absolute.set_ylabel("Median latency (ms)")
    ax_absolute.set_title("a  Absolute admission latency", loc="left", fontweight="bold")
    ax_absolute.legend(bbox_to_anchor=(0.00, 1.00),
        loc="upper left", ncol=1, handlelength=1.8,
        borderaxespad=0.2, fontsize=6.3,
    )
    ax_absolute.grid(axis="y", color="#E5E5E5", linewidth=0.45)

    ax_delta.errorbar(
        x, delta, yerr=yerr, color=CATEGORICAL[3], marker="^",
        markersize=3.4, linewidth=0.95, capsize=1.8,
    )
    negative = np.flatnonzero(delta < 0)
    ax_delta.scatter(
        negative, delta[negative], s=38, facecolors="none",
        edgecolors=ACCENT_RED, linewidths=1.0, zorder=5,
    )
    ax_delta.axhline(0, color=BLACK, linewidth=0.65)
    ax_delta.set_ylim(-25, 185)
    ax_delta.set_yticks([0, 50, 100, 150])
    ax_delta.set_xticks(x)
    ax_delta.set_xticklabels(cell_labels, rotation=42, ha="right")
    ax_delta.set_xlabel("Total/changed fields")
    ax_delta.set_ylabel("Paired mean difference (ms)")
    ax_delta.set_title("b  Paired incremental latency", loc="left", fontweight="bold")
    ax_delta.text(
        0.03, 0.94, "mean difference ± 95% CI\nred rings: negative cells",
        transform=ax_delta.transAxes, ha="left", va="top",
        fontsize=5.8, color=ACCENT_RED,
    )
    ax_delta.grid(axis="y", color="#E5E5E5", linewidth=0.45)

    # Panel c: all 36 reverse-trace p50 cells in a log-colored matrix.
    fields = [1, 8, 32, 128]
    combinations = [(v, r) for v in (1, 10, 100) for r in (1, 100, 1000)]
    lookup = {(row["fields"], row["versions"], row["records"]): row for row in trace}
    matrix = np.array([
        [lookup[(field, version, records)]["p50_ms"] for version, records in combinations]
        for field in fields
    ])
    log_matrix = np.log10(matrix)
    sequential_cmap = LinearSegmentedColormap.from_list("academic-sequential", SEQUENTIAL)
    ax_trace.pcolormesh(
        np.arange(len(combinations) + 1),
        np.arange(len(fields) + 1),
        log_matrix,
        cmap=sequential_cmap,
        vmin=log_matrix.min(),
        vmax=log_matrix.max(),
        shading="flat",
        edgecolors="white",
        linewidth=0.5,
    )
    ax_trace.set_ylim(len(fields), 0)
    ax_trace.set_yticks(np.arange(len(fields)) + 0.5)
    ax_trace.set_yticklabels([str(field) for field in fields])
    ax_trace.set_ylabel("Fields")
    ax_trace.set_xticks(np.arange(len(combinations)) + 0.5)
    ax_trace.set_xticklabels(
        [f"{v}/{r}" for v, r in combinations], rotation=42, ha="right",
    )
    ax_trace.set_xlabel("Versions/records")
    ax_trace.set_title("c  Reverse-trace latency", loc="left", fontweight="bold")
    for row_index in range(matrix.shape[0]):
        for column_index in range(matrix.shape[1]):
            normalized = (
                (log_matrix[row_index, column_index] - log_matrix.min())
                / (log_matrix.max() - log_matrix.min())
            )
            text_color = "white" if normalized > 0.58 else BLACK
            ax_trace.text(
                column_index + 0.5, row_index + 0.5,
                _compact_ms(matrix[row_index, column_index]),
                ha="center", va="center", fontsize=5.0, color=text_color,
            )
    for boundary in (3, 6):
        ax_trace.axvline(boundary, color="white", linewidth=1.2)
    ax_trace.text(
        0.99, 1.025, "labels: p50 ms · fill: log10(p50)",
        transform=ax_trace.transAxes, ha="right", va="bottom",
        fontsize=5.8, color=DARK_GREY,
    )

    # Panel d: all storage populations and all lower/full/incremental values.
    transitions = np.array([row["transitions"] for row in storage])
    x_storage = np.arange(len(storage))
    lower_mib = np.array([row["lower"]["bytes"] for row in storage]) / (1024**2)
    full_mib = np.array([row["full"]["bytes"] for row in storage]) / (1024**2)
    incremental_mib = np.array([row["incremental_bytes"] for row in storage]) / (1024**2)
    storage_series = [
        ("Full", full_mib, CATEGORICAL[0], "o", "-"),
        ("Incremental", incremental_mib, CATEGORICAL[3], "^", "--"),
        ("Lower", lower_mib, GREY, "s", ":"),
    ]
    for label, values, color, marker, linestyle in storage_series:
        ax_storage.plot(
            x_storage, values, color=color, marker=marker, markersize=3.4,
            linewidth=1.0, linestyle=linestyle,
        )
        ax_storage.annotate(
            label, (x_storage[-1], values[-1]), xytext=(5, 0),
            textcoords="offset points", va="center", ha="left",
            fontsize=6.2, color=color,
        )
    ax_storage.set_yscale("log")
    ax_storage.set_yticks([0.5, 1, 5, 10, 50, 100])
    ax_storage.set_yticklabels(["0.5", "1", "5", "10", "50", "100"])
    ax_storage.yaxis.set_minor_locator(NullLocator())
    ax_storage.set_xlim(-0.15, 2.48)
    ax_storage.set_xticks(x_storage)
    ax_storage.set_xticklabels(["1k", "10k", "100k"])
    ax_storage.set_xlabel("Transitions")
    ax_storage.set_ylabel("Main database size (MiB; log scale)")
    ax_storage.set_title("d  Storage scaling", loc="left", fontweight="bold")
    ax_storage.text(
        0.02, 0.95, "foreign-key failures = 0\nWAL/SHM = 0 B",
        transform=ax_storage.transAxes, ha="left", va="top",
        fontsize=5.8, color=DARK_GREY,
    )
    ax_storage.grid(axis="y", color="#E5E5E5", linewidth=0.45, which="major")

    fig.text(
        0.50, 0.022,
        "Fixed Windows/Python/SQLite grid; descriptive measurements, not asymptotic estimates",
        ha="center", va="bottom", fontsize=6.5, color=DARK_GREY,
    )

    _save_submission_figure(
        fig,
        stem,
        title="Fixed-grid cost characterization",
        description=(
            "Panel a separates absolute full-contract and lower-baseline median admission "
            "latencies for all ten cells. Panel b shows paired mean incremental latency with "
            "95 percent confidence intervals and retains two negative cells. Panel c shows all "
            "36 reverse-trace median cells with logarithmic color encoding. Panel d shows full, "
            "lower, and incremental database size at all three transition populations."
        ),
    )


def build_cost_characterization(data: dict[str, Any], stem: Path) -> None:
    """Plot all frozen equivalent-admission and optimized-trace cells."""
    from figure_narrative_data import load_cost_extensions

    feature, optimized = load_cost_extensions()
    admission = sorted(feature["results"], key=lambda r: (r["fields"], r["changed"]))
    trace = optimized["results"]
    fig, axes = plt.subplots(2, 2, figsize=(183 * MM_TO_INCH, 142 * MM_TO_INCH))
    fig.subplots_adjust(left=0.10, right=0.98, top=0.93, bottom=0.22, hspace=0.80, wspace=0.40)
    aa, ab, ac, ad = axes.flat
    x = np.arange(len(admission))
    labels = [f"{r['fields']}/{r['changed']}" for r in admission]
    aa.plot(x, [r["full_p50_ms"] for r in admission], color=CATEGORICAL[0], marker="o",
            markersize=3, linewidth=1, label="Full admission")
    aa.plot(x, [r["materialization_p50_ms"] for r in admission], color=CATEGORICAL[2],
            marker="s", markersize=3, linewidth=1, label="Equivalent materialization")
    aa.set_title("a  Equivalent admission comparison", loc="left", fontweight="bold", fontsize=7.4)
    aa.set_ylabel("Median latency (ms)")
    aa.set_ylim(0, 215)
    aa.legend(loc="upper left", fontsize=6.2)
    ab.bar(x, [r["paired_mean_validation_and_planning_delta_ms"] for r in admission],
           color=CATEGORICAL[0], width=0.58)
    ab.set_title("b  Paired full-minus-materialization gap", loc="left", fontweight="bold", fontsize=7.4)
    ab.set_ylabel("Paired mean difference (ms)")
    ab.set_ylim(0, 205)
    ab.text(0.02, 0.94, "Validation/planning + path differences",
            transform=ab.transAxes, va="top", fontsize=6.0, color=DARK_GREY)
    for ax in (aa, ab):
        ax.set_xticks(x, labels, rotation=42, ha="right")
        ax.set_xlabel("Total/changed fields")
        ax.grid(axis="y", color="#e5e5e5", linewidth=0.45)
        ax.set_axisbelow(True)

    fields = [1, 8, 32, 128]
    combinations = [(v, r) for v in (1, 10, 100) for r in (1, 100, 1000)]
    lookup = {(r["fields"], r["versions"], r["records"]): r for r in trace}
    matrix = np.array([[lookup[(f, v, r)]["current_p50_ms"] for v, r in combinations] for f in fields])
    cmap = LinearSegmentedColormap.from_list("optimized-trace", SEQUENTIAL)
    ac.pcolormesh(np.arange(10), np.arange(5), matrix, cmap=cmap,
                  vmin=0, vmax=55, edgecolors="white", linewidth=0.5)
    ac.set_ylim(4, 0)
    ac.set_yticks(np.arange(4) + 0.5, [str(f) for f in fields])
    ac.set_xticks(np.arange(9) + 0.5, [f"{v}/{r}" for v, r in combinations], rotation=42, ha="right")
    ac.set_xlabel("Versions/records")
    ac.set_ylabel("Fields")
    ac.set_title("c  Optimized reverse-trace latency", loc="left", fontweight="bold", fontsize=7.4, pad=22)
    for i in range(4):
        for j in range(9):
            ac.text(j + 0.5, i + 0.5, f"{matrix[i,j]:.1f}", ha="center", va="center",
                    fontsize=5.5, color="white" if matrix[i,j] > 30 else BLACK)
    ac.text(0, 1.04, "p50 ms; 12 SQL statements per observation",
            transform=ac.transAxes, fontsize=6, color=DARK_GREY)
    for f, color, marker in zip(fields, CATEGORICAL[:4], ("o", "s", "^", "D"), strict=True):
        cells = [r for r in trace if r["fields"] == f]
        ad.scatter([r["baseline_p50_ms"] for r in cells], [r["current_p50_ms"] for r in cells],
                   s=20, color=color, marker=marker, label=f"{f} field" + ("s" if f != 1 else ""), edgecolors="white", linewidth=0.3)
    ad.plot([3, 10000], [3, 10000], linestyle=":", color=GREY, linewidth=0.9)
    ad.set_xscale("log")
    ad.set_yscale("log")
    ad.set_xlim(3, 10000)
    ad.set_ylim(3, 10000)
    ad.set_xticks([10, 100, 1000, 10000], ["10", "100", "1,000", "10,000"])
    ad.set_yticks([10, 100, 1000, 10000], ["10", "100", "1,000", "10,000"])
    ad.set_xlabel("Historical p50 (ms; log scale)")
    ad.set_ylabel("Optimized p50 (ms; log scale)")
    ad.set_title("d  Trace comparison: all 36 cells", loc="left", fontweight="bold", fontsize=7.4)
    ad.legend(loc="upper left", fontsize=5.8, ncol=2, handletextpad=0.3, columnspacing=0.6)
    ad.text(0.99, 0.06, "dotted line: equal latency", transform=ad.transAxes,
            ha="right", fontsize=5.8, color=DARK_GREY)
    fig.text(0.5, 0.015, "Frozen grid: 2,000 admission pairs; 7,200 observations per trace execution.\n"
             "Trace arms were recorded in separate executions; every frozen cell is shown.",
             ha="center", va="bottom", fontsize=6.2, color=DARK_GREY)
    _save_submission_figure(fig, stem, title="Equivalent admission and optimized reverse trace",
        description="All ten persistence-equivalent admission cells and all 36 optimized trace cells, "
        "with paired admission differences and historical trace comparison. No new experiment was run.")


def build_all_figures(
    cost_input: Path,
    agent_stats_input: Path,
    output_root: Path,
) -> dict[str, Any]:
    from figure_narrative_data import FEATURE_INPUT, TRACE_INPUT, RUNS_INPUT, authority_operation_counts

    cost_input = Path(cost_input).resolve()
    agent_stats_input = Path(agent_stats_input).resolve()
    output_root = Path(output_root).resolve()
    data = json.loads(cost_input.read_text(encoding="utf-8"))
    agent_data = json.loads(agent_stats_input.read_text(encoding="utf-8"))
    stats = validate_cost_summary(data)
    agent_stats = validate_agent_statistics(agent_data)

    workflow = output_root / "vector" / "admission-workflow"
    if not all(workflow.with_suffix(suffix).exists() for suffix in (".pdf", ".svg", ".png")):
        build_admission_workflow(workflow)
    build_evidence_chain(output_root / "vector" / "evidence-chain")
    build_cost_characterization(data, output_root / "generated" / "cost-characterization")
    build_behavior_authority(
        agent_data,
        output_root / "generated" / "behavior-vs-authority",
    )

    outputs = [
        f"{directory}/{stem}.{suffix}"
        for directory, stem in (
            ("vector", "admission-workflow"),
            ("vector", "evidence-chain"),
            ("generated", "cost-characterization"),
            ("generated", "behavior-vs-authority"),
        )
        for suffix in ("svg", "pdf", "png")
    ]
    manifest = {
        "schema": "auto-decte-jss-figure-build-v3",
        "generator": "paper/scripts/build_figures.py",
        "source": str(cost_input),
        "source_sha256": _sha256(cost_input),
        "agent_stats_source": str(agent_stats_input),
        "agent_stats_source_sha256": _sha256(agent_stats_input),
        "data_stats": {**stats, "agent": agent_stats},
        "narrative_inputs": {
            str(path.relative_to(Path(__file__).resolve().parents[2])): _sha256(path)
            for path in (FEATURE_INPUT, TRACE_INPUT, RUNS_INPUT)
        },
        "authority_operations": authority_operation_counts(),
        "generator_sha256": _sha256(Path(__file__)),
        "data_helper_sha256": _sha256(Path(__file__).with_name("figure_narrative_data.py")),
        "outputs": outputs,
        "output_sha256": {
            relative: _sha256(output_root / relative) for relative in outputs
        },
        "ai_concept_consumed": False,
    }
    (output_root / "figure-build-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cost-input", required=True, type=Path)
    parser.add_argument("--agent-stats-input", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    manifest = build_all_figures(
        args.cost_input,
        args.agent_stats_input,
        args.output_root,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
