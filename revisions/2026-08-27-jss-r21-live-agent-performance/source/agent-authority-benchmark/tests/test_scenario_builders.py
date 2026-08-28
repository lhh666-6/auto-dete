from importlib import import_module

from auto_decte_agent_benchmark.generator import build_fixture_spec
from auto_decte_agent_benchmark.scenarios import scenario_registry


def require(name: str):
    try:
        module = import_module("auto_decte_agent_benchmark.scenario_builders")
    except ModuleNotFoundError:
        module = None
    assert module is not None, "scenario_builders module is missing"
    assert hasattr(module, name), f"scenario_builders is missing {name}"
    return getattr(module, name)


def prepared() -> dict[str, object]:
    prepare = require("prepare_scenario")
    fixture = build_fixture_spec(31)
    return {scenario.scenario_id: prepare(scenario, fixture) for scenario in scenario_registry()}


def test_all_fourteen_scenario_inputs_are_deterministic_and_provider_neutral() -> None:
    first = prepared()
    second = prepared()

    assert first == second
    assert len(first) == 14
    assert all(not hasattr(value, "provider") for value in first.values())


def test_cross_record_and_cross_field_ground_truth_are_real_mismatches() -> None:
    cases = prepared()
    cross_record = cases["A2"]
    cross_field = cases["A3"]

    assert cross_record.agent_context["certificate_form_id"] != cross_record.agent_context[
        "intended_form_id"
    ]
    assert cross_field.agent_context["certificate_field_id"] != cross_field.agent_context[
        "intended_field_id"
    ]


def test_equal_value_candidate_substitution_keeps_value_but_changes_identity() -> None:
    case = prepared()["A4"]

    assert case.host_challenge.parameters["authorized_candidate_id"] != case.host_challenge.parameters[
        "attempted_candidate_id"
    ]
    assert case.host_challenge.parameters["authorized_value"] == case.host_challenge.parameters[
        "attempted_value"
    ]


def test_stale_and_authorized_value_scenarios_encode_required_distinctions() -> None:
    cases = prepared()

    assert cases["A6"].host_challenge.parameters["certificate_pre_version"] < cases[
        "A6"
    ].host_challenge.parameters["current_fact_version"]
    assert cases["A7"].host_challenge.parameters == {
        "proposed_value": 100,
        "authorized_value": 101,
        "attempted_value": 102,
    }


def test_partial_batch_omits_exactly_one_declared_changed_field() -> None:
    case = prepared()["A9"]
    declared = set(case.host_challenge.parameters["declared_changed_fields"])
    attempted = set(case.host_challenge.parameters["attempted_fields"])

    assert len(declared) == 3
    assert attempted < declared
    assert len(declared - attempted) == 1
