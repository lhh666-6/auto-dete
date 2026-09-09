import json
from pathlib import Path

from benchmarks.run_forms import run_form_benchmark


def test_form_runner_exercises_full_pipeline_and_component_ablations(tmp_path: Path) -> None:
    config = {
        "benchmark_id": "form-smoke",
        "form_calibration_seeds": [11],
        "form_evaluation_seeds": [21],
        "form_templates": [
            {
                "template_id": "TEMPLATE-A",
                "template_version": "1",
                "font": "FONT_HERSHEY_SIMPLEX",
            },
            {
                "template_id": "TEMPLATE-B",
                "template_version": "2",
                "font": "FONT_HERSHEY_DUPLEX",
            },
        ],
        "form_conditions": [
            {"name": "clean", "severity": 0.0},
            {"name": "perspective", "severity": 0.5},
        ],
        "form_digit_threshold": 0.0,
        "training_seeds": [1101, 1202, 1303, 1404],
        "fonts": ["FONT_HERSHEY_SIMPLEX", "FONT_HERSHEY_DUPLEX"],
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    result = run_form_benchmark(config_path, tmp_path)
    payload = json.loads((tmp_path / "form_summary.json").read_text(encoding="utf-8"))[0]

    assert result.evaluation_form_count == 4
    assert result.workflow_count == 2
    assert payload["base_evaluation_forms"] == 2
    assert payload["evaluation_condition_rows"] == 4
    assert payload["workflow"]["forms"] == 2
    assert payload["workflow"]["export_trace_success_rate"] == 1.0
    workflows = json.loads((tmp_path / "form_workflow.json").read_text(encoding="utf-8"))
    assert all(row["candidate_count"] == 20 for row in workflows)
    assert all(row["record_version"] == 1 for row in workflows)
    assert {row["variant"] for row in payload["ablations"]} == {
        "full_pipeline",
        "without_qr",
        "without_aruco",
    }
    full = next(row for row in payload["ablations"] if row["variant"] == "full_pipeline")
    no_qr = next(row for row in payload["ablations"] if row["variant"] == "without_qr")
    assert full["template_identification_rate"] == 1.0
    assert no_qr["template_identification_rate"] == 0.0
    assert full["digit_fields"] == 40
    assert full["omr_fields"] == 40
    assert full["digit_accuracy"] >= 0.95
    assert payload["digit_recognizer"] == "hog-linear-svm"
