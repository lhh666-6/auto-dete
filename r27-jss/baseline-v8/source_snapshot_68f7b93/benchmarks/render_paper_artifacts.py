import argparse
import json
import math
from pathlib import Path
from typing import Any, cast

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TEAL = "#16796F"
CHARCOAL = "#243746"
AMBER = "#C06B19"
PALE_TEAL = "#E1F2EF"
PALE_AMBER = "#FFF0DC"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.edgecolor": CHARCOAL,
        "axes.labelcolor": CHARCOAL,
        "text.color": CHARCOAL,
        "xtick.color": CHARCOAL,
        "ytick.color": CHARCOAL,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    }
)


def _load_first(path: Path) -> dict[str, Any]:
    payload = cast(list[dict[str, Any]], json.loads(path.read_text(encoding="utf-8")))
    if not payload:
        raise ValueError(f"empty artifact: {path}")
    return payload[0]


def _save(fig: Any, output: Path, stem: str) -> None:
    fig.tight_layout()
    for extension in ("pdf", "svg"):
        fig.savefig(output / f"{stem}.{extension}", bbox_inches="tight")
    plt.close(fig)


def _coverage_risk(summary: dict[str, Any], output: Path) -> None:
    sweep = cast(list[dict[str, Any]], summary["threshold_sweep"])
    fig, axis = plt.subplots(figsize=(4.8, 3.1))
    axis.plot(
        [100 * float(row["coverage"]) for row in sweep],
        [100 * float(row["selective_risk"]) for row in sweep],
        color=TEAL,
        marker="o",
        markersize=3,
        linewidth=1.8,
    )
    axis.set_xlabel("Coverage (%)")
    axis.set_ylabel("Selective risk (%)")
    axis.grid(alpha=0.22)
    _save(fig, output, "coverage_risk")


def _robustness(summary: dict[str, Any], output: Path) -> None:
    rows = cast(list[dict[str, Any]], summary["robustness"])
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(str(row["perturbation"]), []).append(row)
    fig, axis = plt.subplots(figsize=(6.2, 3.5))
    markers = ["o", "s", "^", "D", "v", "P", "X", "*"]
    for index, (name, group) in enumerate(sorted(groups.items())):
        ordered = sorted(group, key=lambda row: float(row["severity"]))
        axis.plot(
            [float(row["severity"]) for row in ordered],
            [100 * float(row["coverage"]) for row in ordered],
            label=name.replace("_", " "),
            marker=markers[index % len(markers)],
            linewidth=1.5,
            color=TEAL if index % 2 == 0 else AMBER,
            linestyle="-" if index < 4 else "--",
        )
    axis.set_xlabel("Perturbation severity")
    axis.set_ylabel("Coverage (%)")
    max_coverage = max(100 * float(row["coverage"]) for row in rows)
    upper = min(100.0, max(20.0, 20.0 * math.ceil(max_coverage / 20.0)))
    axis.set_ylim(0, upper)
    axis.grid(alpha=0.22)
    axis.legend(ncol=2, fontsize=7, frameon=False)
    _save(fig, output, "robustness")


def _trust(input_dir: Path, output: Path) -> None:
    rows = cast(
        list[dict[str, Any]],
        json.loads((input_dir / "trust_faults.json").read_text(encoding="utf-8")),
    )
    values = [int(bool(row["fact_unchanged"]) and bool(row["audit_complete"])) for row in rows]
    fig, axis = plt.subplots(figsize=(5.5, 3.2))
    axis.barh(
        range(len(rows)),
        values,
        color=[TEAL if value else AMBER for value in values],
    )
    axis.set_yticks(range(len(rows)), [str(row["fault"]).replace("_", " ") for row in rows])
    axis.set_xticks([0, 1], ["failed", "preserved"])
    axis.set_xlim(0, 1.05)
    axis.invert_yaxis()
    axis.grid(axis="x", alpha=0.22)
    _save(fig, output, "trust_faults")


def _latency(input_dir: Path, output: Path) -> None:
    resilience = _load_first(input_dir / "resilience.json")
    latency = cast(dict[str, list[float]], resilience["latency"])
    fig, axis = plt.subplots(figsize=(4.8, 3.1))
    plot = axis.boxplot(
        [latency["cold_ms"], latency["warm_ms"]],
        tick_labels=["Cold", "Warm"],
        patch_artist=True,
        widths=0.55,
    )
    for patch, color in zip(plot["boxes"], [PALE_AMBER, PALE_TEAL], strict=True):
        patch.set_facecolor(color)
        patch.set_edgecolor(CHARCOAL)
    axis.set_ylabel("Latency (ms)")
    axis.grid(axis="y", alpha=0.22)
    _save(fig, output, "latency")


def _model_selective(summary: dict[str, Any], output: Path) -> None:
    rows = cast(list[dict[str, Any]], summary["selective_models"])
    labels = [str(row["model"]).replace("-linear-svm", " SVM") for row in rows]
    coverage = [
        100 * float(cast(dict[str, Any], row["selected_metrics"])["coverage"])
        for row in rows
    ]
    accuracy = [
        100 * float(cast(dict[str, Any], row["selected_metrics"])["accepted_accuracy"])
        for row in rows
    ]
    positions = list(range(len(rows)))
    fig, axis = plt.subplots(figsize=(5.4, 3.2))
    width = 0.34
    axis.bar(
        [value - width / 2 for value in positions],
        coverage,
        width,
        label="Coverage",
        color=TEAL,
    )
    axis.bar(
        [value + width / 2 for value in positions],
        accuracy,
        width,
        label="Accepted accuracy",
        color=AMBER,
    )
    axis.set_xticks(positions, labels)
    axis.set_ylabel("Rate (%)")
    axis.set_ylim(0, 105)
    axis.grid(axis="y", alpha=0.22)
    axis.legend(frameon=False)
    _save(fig, output, "model_selective_comparison")


def _whole_form(summary: dict[str, Any], output: Path) -> None:
    rows = cast(list[dict[str, Any]], summary["ablations"])
    labels = [str(row["variant"]).replace("_", " ") for row in rows]
    positions = list(range(len(rows)))
    metrics = (
        ("template_identification_rate", "QR/template", TEAL),
        ("alignment_success_rate", "Alignment", CHARCOAL),
        ("digit_accuracy", "Digit accuracy", AMBER),
        ("omr_accuracy", "OMR accuracy", "#6C8EAD"),
        ("complete_form_success_rate", "Complete form", "#8A5A8A"),
    )
    fig, axis = plt.subplots(figsize=(7.0, 3.5))
    width = 0.15
    center = (len(metrics) - 1) / 2
    for index, (key, label, color) in enumerate(metrics):
        axis.bar(
            [value + (index - center) * width for value in positions],
            [100 * float(row[key]) for row in rows],
            width,
            label=label,
            color=color,
        )
    axis.set_xticks(positions, labels)
    axis.set_ylabel("Rate (%)")
    axis.set_ylim(0, 105)
    axis.grid(axis="y", alpha=0.22)
    axis.legend(ncol=3, fontsize=7, frameon=False)
    _save(fig, output, "whole_form_ablation")


def _escape(value: object) -> str:
    return str(value).replace("_", r"\_")


def _tables(summary: dict[str, Any], output: Path) -> None:
    metrics = cast(dict[str, Any], summary["selected_metrics"])
    interval = cast(
        dict[str, Any],
        summary.get("accepted_accuracy_wilson_ci95", summary["accepted_accuracy_ci95"]),
    )
    selected = (
        "\\begin{tabular}{lr}\n"
        "\\toprule\nMetric & Value \\\\\n"
        "\\midrule\n"
        f"Coverage & {100 * float(metrics['coverage']):.1f}\\% \\\\\n"
        f"Accepted accuracy & {100 * float(metrics['accepted_accuracy']):.1f}\\% \\\\\n"
        f"Selective risk & {100 * float(metrics['selective_risk']):.1f}\\% \\\\\n"
        f"Routing rate & {100 * float(metrics['routing_rate']):.1f}\\% \\\\\n"
        f"Accepted accuracy Wilson 95\\% CI & [{100 * float(interval['lower']):.1f}, "
        f"{100 * float(interval['upper']):.1f}]\\% \\\\\n"
        "\\bottomrule\n\\end{tabular}\n"
    )
    (output / "selective_metrics.tex").write_text(selected, encoding="utf-8")

    baseline_lines = [
        "\\begin{tabular}{lrrr}",
        "\\toprule",
        "Model & Accuracy (\\%) & Coverage (\\%) & Cases \\\\",
        "\\midrule",
    ]
    for row in cast(list[dict[str, Any]], summary["baselines"]):
        baseline_lines.append(
            f"{_escape(row['model'])} & {100 * float(row['accuracy']):.1f} & "
            f"{100 * float(row['coverage']):.1f} & {int(row['cases'])} \\\\"
        )
    baseline_lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    (output / "baseline_comparison.tex").write_text(
        "\n".join(baseline_lines), encoding="utf-8"
    )

    robustness_lines = [
        "\\begin{tabular}{lrrr}",
        "\\toprule",
        "Condition & Severity & Coverage (\\%) & Accepted accuracy (\\%) \\\\",
        "\\midrule",
    ]
    for row in cast(list[dict[str, Any]], summary["robustness"]):
        robustness_lines.append(
            f"{_escape(row['perturbation'])} & {float(row['severity']):.2f} & "
            f"{100 * float(row['coverage']):.1f} & "
            f"{100 * float(row['accepted_accuracy']):.1f} \\\\"
        )
    robustness_lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    (output / "robustness.tex").write_text("\n".join(robustness_lines), encoding="utf-8")

    model_lines = [
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Model & Cov. (\\%) & Acc. (\\%) & Risk (\\%) & Review (\\%) \\\\",
        "\\midrule",
    ]
    for row in cast(list[dict[str, Any]], summary.get("selective_models", [])):
        model_metrics = cast(dict[str, Any], row["selected_metrics"])
        label = {
            "auto-decte": "Template matcher",
            "hog-linear-svm": "HOG--SVM",
        }.get(str(row["model"]), _escape(row["model"]))
        model_lines.append(
            f"{label} & "
            f"{100 * float(model_metrics['coverage']):.1f} & "
            f"{100 * float(model_metrics['accepted_accuracy']):.2f} & "
            f"{100 * float(model_metrics['selective_risk']):.2f} & "
            f"{100 * float(model_metrics['routing_rate']):.1f} \\\\"
        )
    model_lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    (output / "selective_model_comparison.tex").write_text(
        "\n".join(model_lines), encoding="utf-8"
    )


def _whole_form_tables(input_dir: Path, output: Path) -> None:
    summary = _load_first(input_dir / "form_summary.json")
    lines = [
        "\\begin{tabular}{lrrrrr}",
        "\\toprule",
        "Variant & QR (\\%) & Align (\\%) & Digit (\\%) "
        "& OMR (\\%) & Complete (\\%) \\\\",
        "\\midrule",
    ]
    for row in cast(list[dict[str, Any]], summary["ablations"]):
        lines.append(
            f"{_escape(row['variant'])} & "
            f"{100 * float(row['template_identification_rate']):.1f} & "
            f"{100 * float(row['alignment_success_rate']):.1f} & "
            f"{100 * float(row['digit_accuracy']):.1f} & "
            f"{100 * float(row['omr_accuracy']):.1f} & "
            f"{100 * float(row['complete_form_success_rate']):.1f} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    (output / "whole_form_metrics.tex").write_text("\n".join(lines), encoding="utf-8")

    stress = cast(
        list[dict[str, Any]],
        json.loads((input_dir / "trust_stress.json").read_text(encoding="utf-8")),
    )
    families: dict[str, list[bool]] = {}
    for row in stress:
        families.setdefault(str(row["family"]), []).append(bool(row["contained"]))
    stress_lines = [
        "\\begin{tabular}{lrr}",
        "\\toprule",
        "Fault family & Contained & Trials \\\\",
        "\\midrule",
    ]
    for family, values in families.items():
        stress_lines.append(
            f"{_escape(family)} & {sum(values)} & {len(values)} \\\\"
        )
    stress_lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    (output / "fault_stress.tex").write_text(
        "\n".join(stress_lines), encoding="utf-8"
    )


def render_artifacts(input_dir: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    summary = _load_first(input_dir / "recognition_summary.json")
    _coverage_risk(summary, output)
    _robustness(summary, output)
    _trust(input_dir, output)
    _latency(input_dir, output)
    _tables(summary, output)
    if "selective_models" in summary:
        _model_selective(summary, output)
    if (input_dir / "form_summary.json").exists():
        form_summary = _load_first(input_dir / "form_summary.json")
        _whole_form(form_summary, output)
        _whole_form_tables(input_dir, output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render ESWA paper artifacts")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render_artifacts(args.input, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
