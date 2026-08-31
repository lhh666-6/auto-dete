from importlib import import_module
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]


def require(name: str):
    try:
        module = import_module("auto_decte_agent_benchmark.runner")
    except ModuleNotFoundError:
        module = None
    assert module is not None, "runner module is missing"
    assert hasattr(module, name), f"runner is missing {name}"
    return getattr(module, name)


def test_pilot_dry_run_validates_complete_matrix_without_writing(tmp_path) -> None:
    dry_run = require("dry_run")
    output_root = tmp_path / "must-not-exist"

    summary = dry_run(config_root=ROOT / "config", phase="pilot", output_root=output_root)

    assert summary["planned_executions"] == 112
    assert summary["model_configurations"] == 4
    assert summary["provider_counts"] == {"openai": 2, "deepseek": 2}
    assert summary["scenarios"] == 14
    assert summary["prompt_variants"] == 2
    assert summary["repetitions"] == 1
    assert summary["rendered_prompts"] == 112
    assert summary["scenario_builder_validations"] == 112
    assert summary["semantic_equivalence_groups"] == 56
    assert summary["logical_tool_surface_equivalent"] is True
    assert len(summary["run_plan_sha256"]) == 64
    assert not output_root.exists()


def test_dry_run_reuses_the_same_case_seed_across_providers() -> None:
    build = require("build_phase_plan")

    plan = build(config_root=ROOT / "config", phase="pilot")
    aligned = [
        run
        for run in plan
        if run.coordinate.scenario_id == "B1"
        and run.coordinate.prompt_variant_id == "V1"
        and run.coordinate.repetition == 1
    ]

    assert len(aligned) == 4
    assert len({run.coordinate.case_seed for run in aligned}) == 1


def test_pilot_dry_run_selectors_narrow_without_changing_locked_config(tmp_path) -> None:
    dry_run = require("dry_run")

    summary = dry_run(
        config_root=ROOT / "config",
        phase="pilot",
        output_root=tmp_path / "must-not-exist",
        model_ids=("D1",),
        scenario_ids=("B1",),
        variant_ids=("V1",),
    )

    assert summary["planned_executions"] == 1
    assert summary["model_configurations"] == 1
    assert summary["provider_counts"] == {"deepseek": 1}
    assert summary["scenarios"] == 1
    assert summary["prompt_variants"] == 1


def test_required_cli_accepts_phase_selectors_resume_and_locked_config() -> None:
    parser = require("_parser")()

    args = parser.parse_args(
        [
            "--pilot",
            "--config",
            str(ROOT / "config"),
            "--output",
            "pilot-output",
            "--model",
            "D1",
            "--scenario",
            "B1",
            "--variant",
            "V1",
            "--repetitions",
            "1",
            "--seed",
            "20260828",
            "--resume",
            "--max-new-invocations",
            "1",
            "--launch-lock",
            "pilot2-lock.json",
            "--frozen-root",
            "final-freeze",
            "--dry-run",
        ]
    )

    assert args.pilot is True
    assert args.final is False
    assert args.config == ROOT / "config"
    assert args.output == Path("pilot-output")
    assert args.model == ["D1"]
    assert args.scenario == ["B1"]
    assert args.variant == ["V1"]
    assert args.repetitions == 1
    assert args.seed == 20260828
    assert args.resume is True
    assert args.max_new_invocations == 1
    assert args.launch_lock == Path("pilot2-lock.json")
    assert args.frozen_root == Path("final-freeze")
    assert args.dry_run is True

    with pytest.raises(SystemExit):
        parser.parse_args(["--pilot", "--final", "--config", str(ROOT / "config")])


def test_cli_dispatches_live_execution_with_exact_locked_values(tmp_path) -> None:
    parser = require("_parser")()
    dispatch = require("_dispatch")
    output = tmp_path / "pilot"
    args = parser.parse_args(
        [
            "--pilot",
            "--config",
            str(ROOT / "config"),
            "--output",
            str(output),
            "--model",
            "D1",
            "--scenario",
            "B1",
            "--variant",
            "V1",
            "--repetitions",
            "1",
            "--seed",
            "20260828",
            "--max-new-invocations",
            "1",
        ]
    )
    captured = {}

    def fake_live_runner(**values):
        captured.update(values)
        return {"planned_executions": 1}

    result = dispatch(
        args,
        revision_root=ROOT.parents[1],
        implementation_python=Path(sys.executable),
        live_runner=fake_live_runner,
    )

    assert result == {"planned_executions": 1}
    assert captured["config_root"] == ROOT / "config"
    assert captured["output_root"] == output
    assert captured["phase"] == "pilot"
    assert captured["model_ids"] == ("D1",)
    assert captured["scenario_ids"] == ("B1",)
    assert captured["variant_ids"] == ("V1",)
    assert captured["resume"] is False
    assert captured["max_new_invocations"] == 1


def test_live_dispatch_enforces_launch_lock_before_calling_runner(tmp_path) -> None:
    parser = require("_parser")()
    dispatch = require("_dispatch")
    lock = tmp_path / "PILOT2_LAUNCH_LOCK.json"
    lock.write_text("{}\n", encoding="utf-8")
    output = tmp_path / "pilot"
    args = parser.parse_args(
        [
            "--pilot",
            "--config",
            str(ROOT / "config"),
            "--output",
            str(output),
            "--max-new-invocations",
            "1",
            "--launch-lock",
            str(lock),
        ]
    )
    calls = []

    def reject_lock(*_args, **_kwargs):
        calls.append("lock")
        raise ValueError("synthetic launch-lock mismatch")

    def forbidden_live_runner(**_values):
        calls.append("live")
        pytest.fail("live runner must not run after launch-lock failure")

    with pytest.raises(ValueError, match="synthetic launch-lock mismatch"):
        dispatch(
            args,
            revision_root=ROOT.parents[1],
            implementation_python=Path(sys.executable),
            live_runner=forbidden_live_runner,
            launch_lock_verifier=reject_lock,
        )

    assert calls == ["lock"]


def _final_config(tmp_path: Path) -> Path:
    from auto_decte_agent_benchmark.freeze import build_final_configuration

    qualification = {
        "schema_version": "agent-authority-model-qualification.v2",
        "models": [
            {
                "model_config_id": model_id,
                "provider": provider,
                "qualification_pass": True,
            }
            for model_id, provider in (
                ("G1", "openai"),
                ("G2", "openai"),
                ("D1", "deepseek"),
                ("D2", "deepseek"),
            )
        ],
    }
    gate = {
        "schema_version": "agent-authority-final-resource-gate.v2",
        "status": "PASS",
        "scientific_outcomes_read": False,
        "qualified_model_config_ids": ["D1", "D2", "G1", "G2"],
        "selected_repetitions": 10,
        "planned_executions": 1680,
    }
    output = tmp_path / "final-config"
    build_final_configuration(
        pilot_config_root=ROOT / "config",
        qualification=qualification,
        resource_gate=gate,
        output_root=output,
    )
    return output


def _final_args(tmp_path: Path, *, frozen_root: Path | None = None):
    parser = require("_parser")()
    values = [
        "--final",
        "--config",
        str(_final_config(tmp_path)),
        "--output",
        str(tmp_path / "final-output"),
    ]
    if frozen_root is not None:
        values.extend(["--frozen-root", str(frozen_root)])
    return parser.parse_args(values)


def test_live_final_requires_frozen_root_before_calling_runner(tmp_path: Path) -> None:
    dispatch = require("_dispatch")
    calls = []

    with pytest.raises(ValueError, match="frozen-root"):
        dispatch(
            _final_args(tmp_path),
            revision_root=tmp_path / "freeze",
            implementation_python=Path(sys.executable),
            live_runner=lambda **_values: calls.append("live"),
        )

    assert calls == []


def test_live_final_rejects_tampered_freeze_before_calling_runner(tmp_path: Path) -> None:
    from auto_decte_agent_benchmark.freeze import write_frozen_manifest

    dispatch = require("_dispatch")
    freeze = tmp_path / "freeze"
    (freeze / "source").mkdir(parents=True)
    (freeze / "source/module.py").write_text("VALUE = 1\n", encoding="utf-8")
    write_frozen_manifest(freeze, runtime_metadata={"python": "3.11"})
    (freeze / "source/module.py").write_text("VALUE = 2\n", encoding="utf-8")
    calls = []

    with pytest.raises(ValueError, match="frozen manifest"):
        dispatch(
            _final_args(tmp_path, frozen_root=freeze),
            revision_root=freeze,
            implementation_python=Path(sys.executable),
            live_runner=lambda **_values: calls.append("live"),
        )

    assert calls == []


def test_live_final_verifies_freeze_before_and_after_dispatch(tmp_path: Path) -> None:
    from auto_decte_agent_benchmark.freeze import write_frozen_manifest

    dispatch = require("_dispatch")
    freeze = tmp_path / "freeze"
    (freeze / "source").mkdir(parents=True)
    source = freeze / "source/module.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    write_frozen_manifest(freeze, runtime_metadata={"python": "3.11"})
    calls = []

    def mutating_live_runner(**_values):
        calls.append("live")
        source.write_text("VALUE = 2\n", encoding="utf-8")
        return {"planned_executions": 1680}

    with pytest.raises(ValueError, match="frozen manifest"):
        dispatch(
            _final_args(tmp_path, frozen_root=freeze),
            revision_root=freeze,
            implementation_python=Path(sys.executable),
            live_runner=mutating_live_runner,
        )

    assert calls == ["live"]


def test_frozen_manifest_rejects_wrong_schema(tmp_path: Path) -> None:
    from auto_decte_agent_benchmark.freeze import verify_frozen_manifest
    from auto_decte_agent_benchmark.manifest import build_manifest

    freeze = tmp_path / "freeze"
    freeze.mkdir()
    (freeze / "source.py").write_text("VALUE = 1\n", encoding="utf-8")
    manifest_path = freeze / "FROZEN.json"
    manifest = build_manifest(freeze, manifest_path=manifest_path)
    manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

    assert verify_frozen_manifest(freeze) == ["SCHEMA:FROZEN.json"]
