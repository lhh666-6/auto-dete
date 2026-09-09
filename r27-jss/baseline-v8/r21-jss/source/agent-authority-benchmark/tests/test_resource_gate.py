import json
from pathlib import Path

import pytest

from auto_decte_agent_benchmark.resource_gate import decide_resource_gate, load_resource_policy


ROOT = Path(__file__).resolve().parents[1]


def qualifications():
    return {
        "models": [
            {"model_config_id": "G1", "provider": "openai", "qualification_pass": True},
            {"model_config_id": "G2", "provider": "openai", "qualification_pass": True},
            {"model_config_id": "D1", "provider": "deepseek", "qualification_pass": True},
            {"model_config_id": "D2", "provider": "deepseek", "qualification_pass": True},
        ]
    }


def resources(mean_seconds: float):
    return {
        model: {
            "mean_total_latency_seconds": mean_seconds,
            "runtime_failure_rate": 0.0,
            "provider_credit_sufficient": True,
        }
        for model in ("G1", "G2", "D1", "D2")
    }


def test_resource_policy_is_frozen_before_pilot_outcomes() -> None:
    policy = load_resource_policy(ROOT / "config/resource-policy.json")

    assert policy["default_repetitions"] == 10
    assert policy["fallback_repetitions"] == 5
    assert policy["max_expected_wall_time_hours"] == 72
    assert policy["scientific_outcomes_permitted"] is False


def test_resource_gate_selects_default_or_balanced_fallback_from_resources_only() -> None:
    policy = load_resource_policy(ROOT / "config/resource-policy.json")

    default = decide_resource_gate(qualifications(), resources(100), policy)
    fallback = decide_resource_gate(qualifications(), resources(250), policy)

    assert default["status"] == "PASS"
    assert default["selected_repetitions"] == 10
    assert default["planned_executions"] == 1680
    assert fallback["status"] == "PASS_FALLBACK"
    assert fallback["selected_repetitions"] == 5
    assert fallback["planned_executions"] == 840
    assert fallback["scientific_outcomes_read"] is False


def test_resource_gate_blocks_missing_provider_credit_or_excess_wall_time() -> None:
    policy = load_resource_policy(ROOT / "config/resource-policy.json")
    missing_family = qualifications()
    missing_family["models"] = missing_family["models"][:2]
    insufficient = resources(100)
    insufficient["D2"]["provider_credit_sufficient"] = False

    assert decide_resource_gate(missing_family, resources(100), policy)["status"] == "BLOCK"
    assert decide_resource_gate(qualifications(), insufficient, policy)["status"] == "BLOCK"
    assert decide_resource_gate(qualifications(), resources(400), policy)["status"] == "BLOCK"


def test_resource_gate_rejects_scientific_outcome_fields() -> None:
    policy = load_resource_policy(ROOT / "config/resource-policy.json")
    contaminated = resources(100)
    contaminated["G1"]["benign_task_completion"] = 1.0

    with pytest.raises(ValueError, match="scientific outcome"):
        decide_resource_gate(qualifications(), contaminated, policy)


def test_policy_file_is_valid_json() -> None:
    json.loads((ROOT / "config/resource-policy.json").read_text(encoding="utf-8"))
