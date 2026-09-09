import json
from pathlib import Path

import pytest

from auto_decte_agent_benchmark.manifest import build_manifest, verify_manifest


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


def _complete_final(tmp_path: Path) -> Path:
    root = tmp_path / "final"
    scenario_ids = ["B1", "B2", "B3", "B4"] + [f"A{index}" for index in range(1, 11)]
    _write_json(
        root / "frozen-config/final.matrix.json",
        {
            "schema_version": "agent-authority-matrix.v2",
            "phase": "final",
            "scenario_ids": scenario_ids,
            "prompt_variant_ids": ["V1", "V2", "V3"],
            "repetitions": 5,
            "planned_executions": 420,
            "citable": True,
        },
    )
    _write_json(
        root / "frozen-config/final.models.json",
        {
            "schema_version": "agent-authority-model-config.v2",
            "qualification_status": "qualified",
            "models": [
                {"model_config_id": "G1", "provider": "openai"},
                {"model_config_id": "D1", "provider": "deepseek"},
            ],
        },
    )
    rows = [
        {
            "run_id": f"{model_id}-{scenario_id}-{variant_id}-{repetition}",
            "phase": "final",
            "model_config_id": model_id,
            "scenario_id": scenario_id,
            "prompt_variant_id": variant_id,
            "repetition": repetition,
        }
        for model_id in ("G1", "D1")
        for scenario_id in scenario_ids
        for variant_id in ("V1", "V2", "V3")
        for repetition in range(1, 6)
    ]
    _write_json(root / "normalized/runs.json", rows)
    _write(root / "normalized/runs.csv", b"run_id,phase\nrun-1,final\nrun-2,final\n")
    _write_json(
        root / "normalized/summary.json",
        {"schema_version": "agent-authority-summary.v2", "planned_executions": 420},
    )
    reporting = root / "normalized/paper-reporting"
    _write_json(
        reporting / "statistical_analysis.json",
        {"schema_version": "agent-authority-statistical-analysis.v2"},
    )
    _write(reporting / "agent_behavior_table.tex", b"behavior table\n")
    _write(reporting / "admission_mechanism_table.tex", b"mechanism table\n")
    _write(reporting / "behavior_vs_authority.svg", b"<svg/>\n")
    _write(reporting / "behavior_vs_authority.pdf", b"%PDF-fixture\n")
    _write(reporting / "behavior_vs_authority.png", b"PNG-fixture\n")
    _write(reporting / "FIGURE_QA.md", b"# PASS\n")
    _write(root / "FINAL_REPORT.md", b"# complete locked Final\n")
    manifest_path = root / "manifest.json"
    _write_json(manifest_path, build_manifest(root, manifest_path=manifest_path))
    return root


def test_stage_manuscript_bundle_requires_and_copies_complete_final(tmp_path: Path) -> None:
    from auto_decte_agent_benchmark.manuscript_stage import stage_manuscript_bundle

    final_root = _complete_final(tmp_path)
    output = tmp_path / "manuscript-input"

    status = stage_manuscript_bundle(final_root=final_root, output_root=output)

    assert status["status"] == "READY_FOR_MANUSCRIPT_INTEGRATION"
    assert status["planned_executions"] == 420
    assert status["qualified_model_config_ids"] == ["G1", "D1"]
    assert status["prompt_variant_ids"] == ["V1", "V2", "V3"]
    assert (output / "normalized/agent_authority_benchmark_runs.json").is_file()
    assert (output / "normalized/agent_authority_benchmark_runs.csv").is_file()
    assert (output / "normalized/agent_authority_benchmark_summary.json").is_file()
    assert (output / "tables/agent_behavior_table.tex").is_file()
    assert (output / "tables/admission_mechanism_table.tex").is_file()
    assert (output / "figures/behavior_vs_authority.svg").is_file()
    assert (output / "figures/behavior_vs_authority.pdf").is_file()
    assert (output / "figures/behavior_vs_authority.png").is_file()
    assert (output / "statistical_analysis.json").is_file()
    assert (output / "MANUSCRIPT_INPUT_STATUS.json").is_file()
    assert verify_manifest(output, output / "manifest.json") == []


@pytest.mark.parametrize("failure", ["tamper", "pilot-phase", "incomplete"])
def test_stage_manuscript_bundle_rejects_nonfinal_or_unverified_input(
    tmp_path: Path, failure: str
) -> None:
    from auto_decte_agent_benchmark.manuscript_stage import stage_manuscript_bundle

    final_root = _complete_final(tmp_path)
    if failure == "tamper":
        (final_root / "FINAL_REPORT.md").write_bytes(b"changed\n")
    elif failure == "pilot-phase":
        rows_path = final_root / "normalized/runs.json"
        rows = json.loads(rows_path.read_text(encoding="utf-8"))
        rows[0]["phase"] = "pilot"
        _write_json(rows_path, rows)
        _write_json(
            final_root / "manifest.json",
            build_manifest(final_root, manifest_path=final_root / "manifest.json"),
        )
    else:
        (final_root / "normalized/paper-reporting/agent_behavior_table.tex").unlink()
        _write_json(
            final_root / "manifest.json",
            build_manifest(final_root, manifest_path=final_root / "manifest.json"),
        )
    output = tmp_path / "manuscript-input"

    with pytest.raises((FileNotFoundError, ValueError), match="Final|manifest|missing"):
        stage_manuscript_bundle(final_root=final_root, output_root=output)

    assert not output.exists()


def test_stage_manuscript_bundle_refuses_overwrite(tmp_path: Path) -> None:
    from auto_decte_agent_benchmark.manuscript_stage import stage_manuscript_bundle

    final_root = _complete_final(tmp_path)
    output = tmp_path / "manuscript-input"
    output.mkdir()

    with pytest.raises(FileExistsError):
        stage_manuscript_bundle(final_root=final_root, output_root=output)
