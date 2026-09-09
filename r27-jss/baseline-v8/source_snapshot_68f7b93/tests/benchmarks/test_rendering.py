import json
from pathlib import Path

import numpy as np
import pytest
from matplotlib.figure import Figure

import benchmarks.render_paper_artifacts as rendering
from benchmarks.render_paper_artifacts import render_artifacts


def test_rendering_produces_vector_figures_and_booktabs(tmp_path: Path) -> None:
    input_dir = tmp_path / "inputs"
    output_dir = tmp_path / "paper"
    input_dir.mkdir()
    recognition = [{
        "selected_threshold": 0.02,
        "selected_metrics": {
            "total": 4, "accepted": 3, "coverage": 0.75,
            "accepted_accuracy": 1.0, "selective_risk": 0.0,
            "erroneous_auto_pass_rate": 0.0, "routing_rate": 0.25
        },
        "accepted_accuracy_ci95": {"estimate": 1.0, "lower": 1.0, "upper": 1.0},
        "threshold_sweep": [
            {"threshold": 0.0, "coverage": 1.0, "selective_risk": 0.25},
            {"threshold": 0.02, "coverage": 0.75, "selective_risk": 0.0}
        ],
        "robustness": [
            {"perturbation": "clean", "severity": 0.0, "coverage": 1.0, "accepted_accuracy": 1.0},
            {"perturbation": "noise", "severity": 0.5, "coverage": 0.5, "accepted_accuracy": 1.0}
        ],
        "baselines": [
            {"model": "auto-decte", "accuracy": 0.75, "coverage": 1.0, "cases": 4}
        ],
        "selective_models": [
            {
                "model": "auto-decte",
                "selected_threshold": 0.02,
                "selected_metrics": {
                    "coverage": 0.75, "accepted_accuracy": 1.0,
                    "selective_risk": 0.0, "routing_rate": 0.25
                },
            },
            {
                "model": "hog-linear-svm",
                "selected_threshold": 0.0,
                "selected_metrics": {
                    "coverage": 1.0, "accepted_accuracy": 0.99,
                    "selective_risk": 0.01, "routing_rate": 0.0
                },
            },
        ],
    }]
    trust = [{"fault": "wrong_recognition", "fact_unchanged": True, "audit_complete": True}]
    resilience = [
        {
            "checks": {
                "ai_disabled": True,
                "duplicate_rejected": True,
                "stale_rejected": True,
                "reverse_trace": True,
            },
            "latency": {"warm_ms": [1.0, 1.2, 0.9], "cold_ms": [2.0, 2.2, 1.8]},
        }
    ]
    (input_dir / "recognition_summary.json").write_text(json.dumps(recognition), encoding="utf-8")
    (input_dir / "trust_faults.json").write_text(json.dumps(trust), encoding="utf-8")
    (input_dir / "resilience.json").write_text(json.dumps(resilience), encoding="utf-8")
    (input_dir / "form_summary.json").write_text(
        json.dumps(
            [{
                "base_evaluation_forms": 2,
                "evaluation_condition_rows": 4,
                "ablations": [
                    {
                        "variant": "full_pipeline", "template_identification_rate": 1.0,
                        "alignment_success_rate": 1.0, "digit_fields": 40,
                        "digit_coverage": 0.8, "digit_accuracy": 0.75, "omr_fields": 40,
                        "omr_coverage": 1.0, "omr_accuracy": 0.95,
                        "complete_form_success_rate": 0.5,
                    },
                    {
                        "variant": "without_qr", "template_identification_rate": 0.0,
                        "alignment_success_rate": 1.0, "digit_fields": 40,
                        "digit_coverage": 0.8, "digit_accuracy": 0.75, "omr_fields": 40,
                        "omr_coverage": 1.0, "omr_accuracy": 0.95,
                        "complete_form_success_rate": 0.0,
                    },
                    {
                        "variant": "without_aruco", "template_identification_rate": 1.0,
                        "alignment_success_rate": 0.0, "digit_fields": 40,
                        "digit_coverage": 0.5, "digit_accuracy": 0.4, "omr_fields": 40,
                        "omr_coverage": 0.7, "omr_accuracy": 0.6,
                        "complete_form_success_rate": 0.0,
                    },
                ],
            }]
        ),
        encoding="utf-8",
    )
    (input_dir / "trust_stress.json").write_text(
        json.dumps([
            {"family": "wrong_recognition", "contained": True},
            {"family": "wrong_llm_suggestion", "contained": True},
        ]),
        encoding="utf-8",
    )

    render_artifacts(input_dir, output_dir)

    expected = [
        "coverage_risk.pdf", "coverage_risk.svg", "robustness.pdf", "robustness.svg",
        "trust_faults.pdf", "trust_faults.svg", "latency.pdf", "latency.svg",
        "selective_metrics.tex", "baseline_comparison.tex", "robustness.tex",
        "model_selective_comparison.pdf", "model_selective_comparison.svg",
        "whole_form_ablation.pdf", "whole_form_ablation.svg",
        "selective_model_comparison.tex", "whole_form_metrics.tex", "fault_stress.tex"
    ]
    assert all((output_dir / name).stat().st_size > 0 for name in expected)
    table = (output_dir / "selective_metrics.tex").read_text(encoding="utf-8")
    assert all(command in table for command in ("\\toprule", "\\midrule", "\\bottomrule"))
    assert "|" not in table


def test_robustness_figure_plots_coverage_not_conditional_accuracy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, Figure] = {}

    def capture(fig: Figure, output: Path, stem: str) -> None:
        captured["figure"] = fig

    monkeypatch.setattr(rendering, "_save", capture)
    summary = {
        "robustness": [
            {
                "perturbation": "noise",
                "severity": 0.25,
                "coverage": 0.75,
                "accepted_accuracy": 1.0,
            },
            {
                "perturbation": "noise",
                "severity": 1.0,
                "coverage": 0.25,
                "accepted_accuracy": 1.0,
            },
        ]
    }

    rendering._robustness(summary, tmp_path)

    figure = captured["figure"]
    axis = figure.axes[0]
    assert axis.get_ylabel() == "Coverage (%)"
    assert np.asarray(axis.lines[0].get_ydata(), dtype=float).tolist() == [75.0, 25.0]
    assert axis.get_ylim() == (0.0, 80.0)
