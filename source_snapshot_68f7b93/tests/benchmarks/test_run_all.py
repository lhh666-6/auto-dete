import json
from pathlib import Path

from benchmarks.run_all import run_all


def test_master_run_creates_hashed_manifest(tmp_path: Path) -> None:
    config = {
        "benchmark_id": "master-smoke",
        "seeds": [1],
        "digits": ["3"],
        "fonts": ["FONT_HERSHEY_SIMPLEX"],
        "conditions": [{"name": "clean", "severities": [0.0]}],
        "thresholds": [0.0, 0.02],
        "selected_threshold": 0.02,
        "training_seeds": [101, 102],
        "run_tesseract": False,
        "bootstrap_replicates": 10,
        "bootstrap_seed": 9,
        "form_calibration_seeds": [11],
        "form_evaluation_seeds": [21],
        "form_templates": [
            {
                "template_id": "TEMPLATE-A",
                "template_version": "1",
                "font": "FONT_HERSHEY_SIMPLEX",
            }
        ],
        "form_conditions": [{"name": "clean", "severity": 0.0}],
        "form_digit_threshold": 0.0,
        "fault_trials_per_family": 1,
        "fault_stress_seed": 73,
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    output = tmp_path / "artifacts"

    run_all(config_path, output, resilience_repetitions=4, resilience_warmups=1)

    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["benchmark_id"] == "master-smoke"
    assert manifest["artifacts"]
    assert all(len(item["sha256"]) == 64 for item in manifest["artifacts"])
    assert "manifest.json" not in {item["path"] for item in manifest["artifacts"]}
    artifact_paths = {item["path"] for item in manifest["artifacts"]}
    assert {
        "form_raw.json",
        "form_summary.json",
        "trust_ablation.json",
        "trust_stress.json",
    }.issubset(artifact_paths)
