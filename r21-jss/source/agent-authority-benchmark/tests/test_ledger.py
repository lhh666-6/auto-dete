from importlib import import_module

import pytest

from auto_decte_agent_benchmark.schema import (
    BenchmarkPhase,
    ModelConfiguration,
    ProviderFamily,
)
from auto_decte_agent_benchmark.scenarios import scenario_registry


def require(name: str):
    try:
        module = import_module("auto_decte_agent_benchmark.ledger")
    except ModuleNotFoundError:
        module = None
    assert module is not None, "ledger module is missing"
    assert hasattr(module, name), f"ledger is missing {name}"
    return getattr(module, name)


def models() -> tuple[ModelConfiguration, ...]:
    return (
        ModelConfiguration("G1", ProviderFamily.OPENAI, "gpt-a", "codex", "codex-jsonl"),
        ModelConfiguration("G2", ProviderFamily.OPENAI, "gpt-b", "codex", "codex-jsonl"),
        ModelConfiguration("D1", ProviderFamily.DEEPSEEK, "ds-a", "https://ds", "anthropic"),
        ModelConfiguration("D2", ProviderFamily.DEEPSEEK, "ds-b", "https://ds", "anthropic"),
    )


def test_pilot_plan_contains_112_unique_locked_runs() -> None:
    build = require("build_run_plan")
    plan = build(
        benchmark_version="v2",
        phase=BenchmarkPhase.PILOT,
        models=models(),
        scenarios=scenario_registry(),
        prompt_variant_ids=("V1", "V2"),
        repetitions=1,
        base_seed=20260828,
    )

    assert len(plan) == 112
    assert len({run.coordinate.run_id for run in plan}) == 112


def test_default_final_plan_contains_1680_unique_locked_runs() -> None:
    build = require("build_run_plan")
    plan = build(
        benchmark_version="v2",
        phase=BenchmarkPhase.FINAL,
        models=models(),
        scenarios=scenario_registry(),
        prompt_variant_ids=("V1", "V2", "V3"),
        repetitions=10,
        base_seed=20260828,
    )

    assert len(plan) == 1680
    assert len({run.coordinate.run_id for run in plan}) == 1680


def test_plan_writer_refuses_to_overwrite_existing_ledger(tmp_path) -> None:
    write = require("write_run_plan")
    target = tmp_path / "planned-runs.jsonl"
    target.write_text("historical\n", encoding="utf-8")

    with pytest.raises(FileExistsError):
        write(target, ())

    assert target.read_text(encoding="utf-8") == "historical\n"


def test_resume_selects_only_missing_run_ids() -> None:
    build = require("build_run_plan")
    missing = require("missing_planned_runs")
    plan = build(
        benchmark_version="v2",
        phase=BenchmarkPhase.PILOT,
        models=models()[:1],
        scenarios=scenario_registry()[:2],
        prompt_variant_ids=("V1",),
        repetitions=1,
        base_seed=9,
    )

    remaining = missing(plan, {plan[0].coordinate.run_id})

    assert remaining == plan[1:]


def test_prompt_variants_share_case_seed_but_keep_unique_run_ids() -> None:
    build = require("build_run_plan")
    plan = build(
        benchmark_version="v2",
        phase=BenchmarkPhase.PILOT,
        models=models()[:1],
        scenarios=scenario_registry()[:1],
        prompt_variant_ids=("V1", "V2"),
        repetitions=1,
        base_seed=20260828,
    )

    assert len(plan) == 2
    assert plan[0].coordinate.case_seed == plan[1].coordinate.case_seed
    assert plan[0].coordinate.run_id != plan[1].coordinate.run_id
