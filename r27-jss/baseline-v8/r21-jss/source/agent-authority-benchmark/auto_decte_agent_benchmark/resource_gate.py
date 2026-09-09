"""Pre-result capacity decision for the balanced Final benchmark matrix."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


FORBIDDEN_OUTCOME_FIELDS = frozenset(
    {
        "benign_task_completion",
        "unauthorized_authoritative_mutation",
        "utility_pass",
        "authority_safe",
        "agent_task_completed",
    }
)


def load_resource_policy(path: Path) -> dict[str, Any]:
    policy = json.loads(path.read_text(encoding="utf-8"))
    if policy.get("schema_version") != "agent-authority-resource-policy.v2":
        raise ValueError("unsupported resource policy schema")
    if policy.get("scientific_outcomes_permitted") is not False:
        raise ValueError("resource policy must prohibit scientific outcomes")
    if int(policy["fallback_repetitions"]) >= int(policy["default_repetitions"]):
        raise ValueError("fallback repetitions must be smaller than default repetitions")
    return policy


def _estimated_wall_time_hours(
    resources: Mapping[str, Mapping[str, Any]],
    *,
    repetitions: int,
    scenario_count: int,
    variant_count: int,
) -> float:
    seconds = sum(
        float(values["mean_total_latency_seconds"])
        * scenario_count
        * variant_count
        * repetitions
        for values in resources.values()
    )
    return seconds / 3600


def decide_resource_gate(
    qualification: Mapping[str, Any],
    resources: Mapping[str, Mapping[str, Any]],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    """Choose 10, balanced 5, or block without inspecting scientific outcomes."""
    for model_id, values in resources.items():
        contaminated = FORBIDDEN_OUTCOME_FIELDS.intersection(values)
        if contaminated:
            names = ", ".join(sorted(contaminated))
            raise ValueError(f"scientific outcome fields are prohibited in resource gate: {names}")

    qualified = [model for model in qualification.get("models", []) if model.get("qualification_pass") is True]
    qualified_ids = sorted(str(model["model_config_id"]) for model in qualified)
    providers = {str(model["provider"]) for model in qualified}
    required_providers = set(policy["required_provider_families"])
    reasons: list[str] = []
    if not required_providers.issubset(providers):
        reasons.append("MISSING_REQUIRED_PROVIDER_FAMILY")
    if set(resources) != set(qualified_ids):
        reasons.append("RESOURCE_ROWS_DO_NOT_MATCH_QUALIFIED_CONFIGURATIONS")
    if any(
        float(values["runtime_failure_rate"]) > float(policy["max_runtime_failure_rate"])
        for values in resources.values()
    ):
        reasons.append("RUNTIME_FAILURE_RATE_EXCEEDS_POLICY")
    if policy.get("require_provider_credit_sufficient") is True and any(
        values.get("provider_credit_sufficient") is not True for values in resources.values()
    ):
        reasons.append("PROVIDER_CREDIT_NOT_CONFIRMED")

    scenario_count = int(policy["scenario_count"])
    variant_count = int(policy["final_prompt_variant_count"])
    default_repetitions = int(policy["default_repetitions"])
    fallback_repetitions = int(policy["fallback_repetitions"])
    max_hours = float(policy["max_expected_wall_time_hours"])
    default_hours = _estimated_wall_time_hours(
        resources,
        repetitions=default_repetitions,
        scenario_count=scenario_count,
        variant_count=variant_count,
    )
    fallback_hours = _estimated_wall_time_hours(
        resources,
        repetitions=fallback_repetitions,
        scenario_count=scenario_count,
        variant_count=variant_count,
    )
    selected_repetitions: int | None = None
    status = "BLOCK"
    if not reasons and default_hours <= max_hours:
        selected_repetitions = default_repetitions
        status = "PASS"
    elif not reasons and fallback_hours <= max_hours:
        selected_repetitions = fallback_repetitions
        status = "PASS_FALLBACK"
    elif not reasons:
        reasons.append("BALANCED_FALLBACK_EXCEEDS_WALL_TIME_POLICY")
    planned_executions = (
        len(qualified_ids) * scenario_count * variant_count * selected_repetitions
        if selected_repetitions is not None
        else 0
    )
    return {
        "schema_version": "agent-authority-final-resource-gate.v2",
        "status": status,
        "scientific_outcomes_read": False,
        "qualified_model_config_ids": qualified_ids,
        "qualified_provider_families": sorted(providers),
        "selected_repetitions": selected_repetitions,
        "planned_executions": planned_executions,
        "estimated_default_wall_time_hours": default_hours,
        "estimated_fallback_wall_time_hours": fallback_hours,
        "reasons": reasons,
    }
