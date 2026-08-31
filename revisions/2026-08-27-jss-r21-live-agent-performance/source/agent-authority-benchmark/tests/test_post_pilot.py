from hashlib import sha256
import json
from pathlib import Path

import pytest

from auto_decte_agent_benchmark.manifest import build_manifest


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _pilot_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    pilot = tmp_path / "pilot"
    config = tmp_path / "config"
    credit = tmp_path / "provider-credit.json"
    models = [
        ("G1", "openai"),
        ("G2", "openai"),
        ("D1", "deepseek"),
        ("D2", "deepseek"),
    ]
    qualification_rows = []
    normalized_rows = []
    for model_id, provider in models:
        qualification_rows.append(
            {
                "model_config_id": model_id,
                "provider": provider,
                "qualification_pass": True,
                "runtime_failure_rate": 0.0,
                "mean_latency_ms": 100_000.0,
            }
        )
        normalized_rows.extend(
            {
                "phase": "pilot",
                "run_id": f"{model_id}-{index}",
                "model_config_id": model_id,
            }
            for index in range(28)
        )
    _write_json(
        pilot / "pilot-model-qualification.json",
        {
            "schema_version": "agent-authority-model-qualification.v2",
            "models": qualification_rows,
        },
    )
    _write_json(pilot / "normalized/runs.json", normalized_rows)
    _write_json(
        pilot / "normalized/summary.json",
        {"schema_version": "agent-authority-summary.v2", "planned_executions": 112},
    )
    (pilot / "PILOT_REPORT.md").write_text("# complete Pilot\n", encoding="utf-8")
    manifest_path = pilot / "manifest.json"
    _write_json(manifest_path, build_manifest(pilot, manifest_path=manifest_path))

    _write_json(
        config / "resource-policy.json",
        {
            "schema_version": "agent-authority-resource-policy.v2",
            "frozen_before_final_outcomes": True,
            "scientific_outcomes_permitted": False,
            "scenario_count": 14,
            "final_prompt_variant_count": 3,
            "default_repetitions": 10,
            "fallback_repetitions": 5,
            "max_expected_wall_time_hours": 72,
            "max_runtime_failure_rate": 0.05,
            "require_provider_credit_sufficient": True,
            "required_provider_families": ["openai", "deepseek"],
            "decision_order": ["default", "balanced_fallback", "block"],
        },
    )
    _write_json(
        credit,
        {
            "schema_version": "agent-authority-provider-credit.v2",
            "model_configurations": {model_id: True for model_id, _provider in models},
        },
    )
    return pilot, config, credit


def test_complete_pilot_writes_hash_bound_resource_gate(tmp_path: Path) -> None:
    from auto_decte_agent_benchmark.post_pilot import write_resource_gate

    pilot, config, credit = _pilot_fixture(tmp_path)
    output = tmp_path / "FINAL_RESOURCE_GATE.json"

    result = write_resource_gate(
        pilot_root=pilot,
        pilot_config_root=config,
        provider_credit_path=credit,
        output_path=output,
    )

    written = json.loads(output.read_text(encoding="utf-8"))
    assert result == written
    assert written["status"] == "PASS"
    assert written["selected_repetitions"] == 10
    assert written["planned_executions"] == 1680
    assert written["scientific_outcomes_read"] is False
    assert written["input_sha256"] == {
        "pilot_manifest": _digest(pilot / "manifest.json"),
        "pilot_qualification": _digest(pilot / "pilot-model-qualification.json"),
        "provider_credit": _digest(credit),
        "resource_policy": _digest(config / "resource-policy.json"),
    }


def test_resource_gate_blocks_false_credit_without_creating_final_authority(tmp_path: Path) -> None:
    from auto_decte_agent_benchmark.post_pilot import write_resource_gate

    pilot, config, credit = _pilot_fixture(tmp_path)
    attestation = json.loads(credit.read_text(encoding="utf-8"))
    attestation["model_configurations"]["G2"] = False
    _write_json(credit, attestation)

    result = write_resource_gate(
        pilot_root=pilot,
        pilot_config_root=config,
        provider_credit_path=credit,
        output_path=tmp_path / "FINAL_RESOURCE_GATE.json",
    )

    assert result["status"] == "BLOCK"
    assert result["selected_repetitions"] is None
    assert result["planned_executions"] == 0
    assert result["reasons"] == ["PROVIDER_CREDIT_NOT_CONFIRMED"]


@pytest.mark.parametrize("failure", ["incomplete", "tampered", "roster"])
def test_resource_gate_rejects_invalid_pilot_before_writing(
    tmp_path: Path, failure: str
) -> None:
    from auto_decte_agent_benchmark.post_pilot import write_resource_gate

    pilot, config, credit = _pilot_fixture(tmp_path)
    if failure == "incomplete":
        (pilot / "manifest.json").unlink()
    elif failure == "tampered":
        with (pilot / "PILOT_REPORT.md").open("a", encoding="utf-8") as handle:
            handle.write("drift\n")
    else:
        qualification = json.loads(
            (pilot / "pilot-model-qualification.json").read_text(encoding="utf-8")
        )
        qualification["models"].pop()
        _write_json(pilot / "pilot-model-qualification.json", qualification)
        _write_json(
            pilot / "manifest.json",
            build_manifest(pilot, manifest_path=pilot / "manifest.json"),
        )
    output = tmp_path / "FINAL_RESOURCE_GATE.json"

    with pytest.raises((FileNotFoundError, ValueError), match="Pilot|manifest|roster"):
        write_resource_gate(
            pilot_root=pilot,
            pilot_config_root=config,
            provider_credit_path=credit,
            output_path=output,
        )

    assert not output.exists()


def test_resource_gate_refuses_overwrite(tmp_path: Path) -> None:
    from auto_decte_agent_benchmark.post_pilot import write_resource_gate

    pilot, config, credit = _pilot_fixture(tmp_path)
    output = tmp_path / "FINAL_RESOURCE_GATE.json"
    output.write_text("preserve\n", encoding="utf-8")

    with pytest.raises(FileExistsError):
        write_resource_gate(
            pilot_root=pilot,
            pilot_config_root=config,
            provider_credit_path=credit,
            output_path=output,
        )

    assert output.read_text(encoding="utf-8") == "preserve\n"


def test_post_pilot_cli_exposes_separate_non_networked_steps() -> None:
    from auto_decte_agent_benchmark.post_pilot import _parser

    parser = _parser()
    gate = parser.parse_args(
        [
            "gate",
            "--pilot-root",
            "pilot",
            "--pilot-config",
            "config",
            "--provider-credit",
            "credit.json",
            "--output",
            "gate.json",
        ]
    )
    final_config = parser.parse_args(
        [
            "final-config",
            "--pilot-config",
            "config",
            "--qualification",
            "qualification.json",
            "--resource-gate",
            "gate.json",
            "--output",
            "final-config",
        ]
    )
    freeze = parser.parse_args(
        [
            "freeze",
            "--benchmark-root",
            "benchmark",
            "--implementation-root",
            "implementation",
            "--final-config",
            "final-config",
            "--runtime-metadata",
            "runtime.json",
            "--output",
            "freeze",
        ]
    )
    verify = parser.parse_args(["verify-freeze", "--root", "freeze"])

    assert gate.command == "gate"
    assert final_config.command == "final-config"
    assert freeze.command == "freeze"
    assert verify.command == "verify-freeze"


def test_final_config_cli_binding_refuses_gate_from_other_qualification(tmp_path: Path) -> None:
    from auto_decte_agent_benchmark.post_pilot import write_final_config

    pilot, config, credit = _pilot_fixture(tmp_path)
    gate_path = tmp_path / "FINAL_RESOURCE_GATE.json"
    from auto_decte_agent_benchmark.post_pilot import write_resource_gate

    write_resource_gate(
        pilot_root=pilot,
        pilot_config_root=config,
        provider_credit_path=credit,
        output_path=gate_path,
    )
    qualification_path = pilot / "pilot-model-qualification.json"
    qualification = json.loads(qualification_path.read_text(encoding="utf-8"))
    qualification["models"][0]["qualification_pass"] = False
    _write_json(qualification_path, qualification)

    with pytest.raises(ValueError, match="qualification hash"):
        write_final_config(
            pilot_config_root=config,
            qualification_path=qualification_path,
            resource_gate_path=gate_path,
            output_root=tmp_path / "final-config",
        )

    assert not (tmp_path / "final-config").exists()
