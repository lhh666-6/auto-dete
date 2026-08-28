from importlib import import_module
from pathlib import Path


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
