import json
from pathlib import Path

from benchmarks.run_recognition import run_recognition


def test_reduced_runner_has_exact_count_and_deterministic_predictions(tmp_path: Path) -> None:
    config = {
        "benchmark_id": "smoke",
        "seeds": [1],
        "digits": ["2", "7"],
        "fonts": ["FONT_HERSHEY_SIMPLEX"],
        "conditions": [
            {"name": "clean", "severities": [0.0]},
            {"name": "gaussian_noise", "severities": [0.5]},
        ],
        "thresholds": [0.0, 0.02],
        "selected_threshold": 0.02,
        "training_seeds": [101, 102],
        "run_tesseract": False,
        "bootstrap_replicates": 20,
        "bootstrap_seed": 9,
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    first = run_recognition(config_path, tmp_path / "first")
    run_recognition(config_path, tmp_path / "second")

    assert first.case_count == 4
    assert first.raw_row_count == 12
    first_rows = json.loads((tmp_path / "first" / "recognition_raw.json").read_text())
    second_rows = json.loads((tmp_path / "second" / "recognition_raw.json").read_text())
    for row in [*first_rows, *second_rows]:
        row.pop("latency_ms")
    assert first_rows == second_rows
    assert (tmp_path / "first" / "recognition_summary.json").read_bytes() == (
        tmp_path / "second" / "recognition_summary.json"
    ).read_bytes()


def test_hog_svm_uses_the_same_calibration_frozen_selective_protocol(tmp_path: Path) -> None:
    config = {
        "benchmark_id": "selective-hog-smoke",
        "seeds": [1, 2],
        "calibration_seeds": [1],
        "evaluation_seeds": [2],
        "digits": ["2", "7"],
        "fonts": ["FONT_HERSHEY_SIMPLEX"],
        "conditions": [
            {"name": "clean", "severities": [0.0]},
            {"name": "gaussian_noise", "severities": [0.5]},
        ],
        "thresholds": [0.0, 0.02, 0.1],
        "selection_risk_target": 0.0,
        "training_seeds": [101, 102],
        "run_tesseract": False,
        "bootstrap_replicates": 20,
        "bootstrap_seed": 9,
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    run_recognition(config_path, tmp_path)
    summary = json.loads((tmp_path / "recognition_summary.json").read_text())[0]
    by_model = {row["model"]: row for row in summary["selective_models"]}

    assert set(by_model) == {"auto-decte", "hog-linear-svm"}
    hog = by_model["hog-linear-svm"]
    assert hog["selection_method"] == "calibration-risk-target"
    assert hog["calibration_case_count"] == 4
    assert hog["evaluation_case_count"] == 4
    assert hog["selected_threshold"] in config["thresholds"]
    assert hog["base_unit_count"] == 2
    assert set(hog["cluster_bootstrap_ci95"]) == {
        "coverage",
        "accepted_accuracy",
        "selective_risk",
    }
