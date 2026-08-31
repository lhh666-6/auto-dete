import json
from pathlib import Path

import pytest

from auto_decte_agent_benchmark.freeze import (
    build_final_configuration,
    stage_final_freeze,
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


def _write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def final_freeze_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    benchmark = tmp_path / "benchmark"
    implementation = tmp_path / "implementation"
    final_config = tmp_path / "final-config"
    _write(benchmark / "auto_decte_agent_benchmark/runner.py", "VALUE = 1\n")
    _write(benchmark / "auto_decte_agent_benchmark/__pycache__/runner.pyc", "cache\n")
    _write(benchmark / "pyproject.toml", "[project]\nname='benchmark'\n")
    _write(benchmark / "uv.lock", "version = 1\n")
    _write(benchmark / "README_REPRODUCE.md", "# reproduce\n")
    _write(benchmark / "config/pilot.models.json", "{}\n")
    _write(benchmark / ".venv/secret.txt", "secret\n")
    _write(benchmark / "evidence/pilot/run.json", "{}\n")
    _write(implementation / "app/service.py", "VALUE = 2\n")
    _write(implementation / "app/__pycache__/service.pyc", "cache\n")
    _write(implementation / "pyproject.toml", "[project]\nname='implementation'\n")
    _write(implementation / "uv.lock", "version = 1\n")
    _write(implementation / ".env", "TOKEN=secret\n")
    for name in (
        "final.models.json",
        "final.matrix.json",
        "retry-policy.json",
        "resource-policy.json",
        "PILOT_MODEL_QUALIFICATION.json",
        "FINAL_RESOURCE_GATE.json",
        "FINAL_CONFIG_RECEIPT.json",
    ):
        _write(final_config / name, "{}\n")
    return benchmark, implementation, final_config


def test_stage_final_freeze_copies_only_runtime_allowlist(tmp_path: Path) -> None:
    benchmark, implementation, final_config = final_freeze_fixture(tmp_path)
    output = tmp_path / "freeze"

    result = stage_final_freeze(
        benchmark_root=benchmark,
        implementation_root=implementation,
        final_config_root=final_config,
        output_root=output,
        runtime_metadata={"python": "3.11", "scientific_outcomes_read": False},
    )

    assert result["schema_version"] == "agent-authority-frozen-source.v2"
    assert (output / "source/agent-authority-benchmark/auto_decte_agent_benchmark/runner.py").is_file()
    assert (output / "source/agent-authority-benchmark/config/final.models.json").is_file()
    assert (output / "source/agent-authority-benchmark/config/FINAL_RESOURCE_GATE.json").is_file()
    assert (
        output / "source/agent-authority-benchmark/config/PILOT_MODEL_QUALIFICATION.json"
    ).is_file()
    assert (output / "source/agent-authority-benchmark/config/FINAL_CONFIG_RECEIPT.json").is_file()
    assert (output / "source/implementation/app/service.py").is_file()
    assert not (output / "source/agent-authority-benchmark/config/pilot.models.json").exists()
    assert not (output / "source/agent-authority-benchmark/.venv").exists()
    assert not (output / "source/agent-authority-benchmark/evidence").exists()
    assert not (output / "source/implementation/.env").exists()
    assert not tuple(output.rglob("__pycache__"))
    assert verify_frozen_manifest(output) == []


def test_stage_final_freeze_refuses_existing_output(tmp_path: Path) -> None:
    benchmark, implementation, final_config = final_freeze_fixture(tmp_path)
    output = tmp_path / "freeze"
    output.mkdir()

    with pytest.raises(FileExistsError):
        stage_final_freeze(
            benchmark_root=benchmark,
            implementation_root=implementation,
            final_config_root=final_config,
            output_root=output,
            runtime_metadata={"python": "3.11"},
        )


def test_stage_final_freeze_preserves_failed_attempt(tmp_path: Path) -> None:
    benchmark, implementation, final_config = final_freeze_fixture(tmp_path)
    (implementation / "uv.lock").unlink()
    output = tmp_path / "freeze"

    with pytest.raises(FileNotFoundError):
        stage_final_freeze(
            benchmark_root=benchmark,
            implementation_root=implementation,
            final_config_root=final_config,
            output_root=output,
            runtime_metadata={"python": "3.11"},
        )

    assert (output / "FREEZE_FAILED.txt").is_file()
    assert not (output / "FROZEN.json").exists()
