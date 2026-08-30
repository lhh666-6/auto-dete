import json
from pathlib import Path

import pytest

from auto_decte_agent_benchmark.freeze import (
    build_final_configuration,
    verify_frozen_manifest,
    write_frozen_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


def qualification():
    return {
        "schema_version": "agent-authority-model-qualification.v2",
        "models": [
            {"model_config_id": "G1", "provider": "openai", "qualification_pass": True},
            {"model_config_id": "G2", "provider": "openai", "qualification_pass": False},
            {"model_config_id": "D1", "provider": "deepseek", "qualification_pass": True},
            {"model_config_id": "D2", "provider": "deepseek", "qualification_pass": True},
        ],
    }


def gate(status="PASS_FALLBACK"):
    return {
        "schema_version": "agent-authority-final-resource-gate.v2",
        "status": status,
        "scientific_outcomes_read": False,
        "qualified_model_config_ids": ["D1", "D2", "G1"],
        "selected_repetitions": 5,
        "planned_executions": 630,
    }


def test_final_configuration_filters_honestly_and_keeps_balanced_matrix(tmp_path: Path) -> None:
    output = tmp_path / "final-config"
    receipt = build_final_configuration(
        pilot_config_root=ROOT / "config",
        qualification=qualification(),
        resource_gate=gate(),
        output_root=output,
    )

    models = json.loads((output / "final.models.json").read_text(encoding="utf-8"))
    matrix = json.loads((output / "final.matrix.json").read_text(encoding="utf-8"))
    assert [model["model_config_id"] for model in models["models"]] == ["G1", "D1", "D2"]
    assert matrix["prompt_variant_ids"] == ["V1", "V2", "V3"]
    assert matrix["repetitions"] == 5
    assert matrix["planned_executions"] == 630
    assert (output / "retry-policy.json").read_bytes() == (
        ROOT / "config/retry-policy.json"
    ).read_bytes()
    assert (output / "resource-policy.json").read_bytes() == (
        ROOT / "config/resource-policy.json"
    ).read_bytes()
    assert receipt["scientific_outcomes_read"] is False
    assert receipt["config_files_sha256"]


def test_final_configuration_rejects_nonpassing_or_contaminated_gate(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="resource gate"):
        build_final_configuration(
            pilot_config_root=ROOT / "config",
            qualification=qualification(),
            resource_gate=gate("BLOCK"),
            output_root=tmp_path / "blocked",
        )
    contaminated = gate()
    contaminated["scientific_outcomes_read"] = True
    with pytest.raises(ValueError, match="scientific outcomes"):
        build_final_configuration(
            pilot_config_root=ROOT / "config",
            qualification=qualification(),
            resource_gate=contaminated,
            output_root=tmp_path / "contaminated",
        )


def test_final_configuration_refuses_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "existing"
    output.mkdir()
    with pytest.raises(FileExistsError):
        build_final_configuration(
            pilot_config_root=ROOT / "config",
            qualification=qualification(),
            resource_gate=gate(),
            output_root=output,
        )


def test_frozen_manifest_is_non_self_referential_and_detects_tamper(tmp_path: Path) -> None:
    root = tmp_path / "freeze"
    (root / "source").mkdir(parents=True)
    (root / "source/module.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / "config").mkdir()
    (root / "config/final.matrix.json").write_text("{}\n", encoding="utf-8")

    frozen = write_frozen_manifest(
        root,
        runtime_metadata={"python": "3.11", "scientific_outcomes_read": False},
    )

    assert frozen["schema_version"] == "agent-authority-frozen-source.v2"
    assert "FROZEN.json" not in {item["path"] for item in frozen["files"]}
    assert verify_frozen_manifest(root) == []
    (root / "source/module.py").write_text("VALUE = 2\n", encoding="utf-8")
    assert verify_frozen_manifest(root) == ["HASH_OR_SIZE:source/module.py"]


def test_frozen_manifest_rejects_scientific_outcome_metadata(tmp_path: Path) -> None:
    root = tmp_path / "freeze"
    root.mkdir()
    with pytest.raises(ValueError, match="scientific outcome"):
        write_frozen_manifest(
            root,
            runtime_metadata={"benign_task_completion": 1.0},
        )
