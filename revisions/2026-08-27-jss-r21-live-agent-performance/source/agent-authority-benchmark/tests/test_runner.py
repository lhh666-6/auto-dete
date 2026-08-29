from importlib import import_module
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
