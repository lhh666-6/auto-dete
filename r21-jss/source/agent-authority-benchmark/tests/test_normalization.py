import pytest

from auto_decte_agent_benchmark.ledger import build_run_plan
from auto_decte_agent_benchmark.normalization import normalize_complete_plan, summarize_primary
from auto_decte_agent_benchmark.schema import (
    BenchmarkPhase,
    ModelConfiguration,
    ProviderFamily,
)
from auto_decte_agent_benchmark.scenarios import scenario_registry


def plan():
    model = ModelConfiguration("G1", ProviderFamily.OPENAI, "gpt-a", "codex", "jsonl")
    return build_run_plan(
        benchmark_version="v2",
        phase=BenchmarkPhase.PILOT,
        models=(model,),
        scenarios=scenario_registry()[:2],
        prompt_variant_ids=("V1",),
        repetitions=1,
        base_seed=7,
    )


def record(run, **values):
    return {
        "schema_version": "agent-authority-run.v2",
        "run_id": run.coordinate.run_id,
        "phase": "pilot",
        "terminal_class": "PASS_UTILITY_SAFE",
        "agent_behavior_evaluable": True,
        "benign_task_completion": True,
        "authority_evaluable": False,
        "unauthorized_authoritative_mutation": None,
        "error_class": None,
        **values,
    }


def test_normalizer_emits_one_row_per_plan_and_retains_runtime_failure() -> None:
    planned = plan()
    records = [
        record(planned[0]),
        record(
            planned[1],
            terminal_class="MODEL_API_FAILURE",
            agent_behavior_evaluable=False,
            benign_task_completion=None,
            error_class="TIMEOUT",
        ),
    ]

    rows = normalize_complete_plan(planned, records, expected_phase=BenchmarkPhase.PILOT)
    summary = summarize_primary(rows)

    assert len(rows) == 2
    assert summary["planned_executions"] == 2
    assert summary["runtime_failures"] == 1
    assert summary["benign_task_completion"]["count"] == 1
    assert summary["benign_task_completion"]["denominator"] == 1
    assert summary["benign_task_completion"]["proportion"] == 1.0
    assert summary["benign_task_completion"]["two_sided_lower"] == pytest.approx(0.025)
    assert summary["benign_task_completion"]["two_sided_upper"] == 1.0
    assert summary["unauthorized_authoritative_mutation"] == {
        "count": 0,
        "denominator": 0,
        "proportion": None,
        "confidence": 0.95,
        "two_sided_lower": None,
        "two_sided_upper": None,
        "one_sided_upper": None,
    }


def test_primary_summary_reports_zero_event_exact_upper_bound() -> None:
    summary = summarize_primary(
        [
            {
                "terminal_class": "PASS_UTILITY_SAFE",
                "benign_task_completion": None,
                "unauthorized_authoritative_mutation": False,
            }
            for _ in range(900)
        ]
    )

    endpoint = summary["unauthorized_authoritative_mutation"]
    assert endpoint["count"] == 0
    assert endpoint["denominator"] == 900
    assert endpoint["one_sided_upper"] == pytest.approx(0.003323, rel=1e-3)


def test_primary_summary_stratifies_both_endpoints_by_configuration() -> None:
    rows = [
        {
            "model_config_id": "G1",
            "terminal_class": "PASS_UTILITY_SAFE",
            "benign_task_completion": True,
            "unauthorized_authoritative_mutation": False,
        },
        {
            "model_config_id": "G1",
            "terminal_class": "PASS_SAFE_BUT_UTILITY_FAILED",
            "benign_task_completion": False,
            "unauthorized_authoritative_mutation": False,
        },
        {
            "model_config_id": "D1",
            "terminal_class": "MODEL_API_FAILURE",
            "benign_task_completion": None,
            "unauthorized_authoritative_mutation": None,
        },
    ]

    summary = summarize_primary(rows)

    assert summary["per_configuration"]["G1"]["benign_task_completion"]["count"] == 1
    assert summary["per_configuration"]["G1"]["benign_task_completion"]["denominator"] == 2
    assert summary["per_configuration"]["G1"]["unauthorized_authoritative_mutation"][
        "denominator"
    ] == 2
    assert summary["per_configuration"]["D1"]["runtime_failures"] == 1


def test_normalizer_rejects_missing_duplicate_extra_or_cross_phase_records() -> None:
    planned = plan()
    complete = [record(run) for run in planned]

    for records in (
        complete[:1],
        [complete[0], complete[0]],
        [*complete, {**complete[0], "run_id": "EXTRA"}],
        [{**complete[0], "phase": "final"}, complete[1]],
    ):
        try:
            normalize_complete_plan(planned, records, expected_phase=BenchmarkPhase.PILOT)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid run collection must be rejected")
