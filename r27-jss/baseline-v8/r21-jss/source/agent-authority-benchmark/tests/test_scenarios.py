from importlib import import_module


def require(name: str):
    try:
        module = import_module("auto_decte_agent_benchmark.scenarios")
    except ModuleNotFoundError:
        module = None
    assert module is not None, "scenarios module is missing"
    assert hasattr(module, name), f"scenarios is missing {name}"
    return getattr(module, name)


def test_registry_contains_exactly_four_benign_and_ten_negative_scenarios() -> None:
    scenarios = require("scenario_registry")()

    assert [scenario.scenario_id for scenario in scenarios] == [
        "B1",
        "B2",
        "B3",
        "B4",
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A6",
        "A7",
        "A8",
        "A9",
        "A10",
    ]
    assert sum(scenario.benign_eligible for scenario in scenarios) == 4


def test_every_negative_scenario_declares_a_rejecting_mechanism_challenge() -> None:
    scenarios = require("scenario_registry")()
    negative = [scenario for scenario in scenarios if not scenario.benign_eligible]

    assert all(scenario.mechanism_challenge_type for scenario in negative)
    assert all(scenario.mechanism_expected_reject is True for scenario in negative)


def test_scenario_ground_truth_contains_no_provider_branch() -> None:
    scenarios = require("scenario_registry")()

    assert all(not hasattr(scenario, "provider") for scenario in scenarios)
    assert all(scenario.formal_properties for scenario in scenarios)
