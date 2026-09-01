from importlib import import_module


schema = import_module("auto_decte_agent_benchmark.schema")


def require(name: str):
    assert hasattr(schema, name), f"schema is missing {name}"
    return getattr(schema, name)


def test_schema_module_is_importable() -> None:
    try:
        module = import_module("auto_decte_agent_benchmark.schema")
    except ModuleNotFoundError:
        module = None

    assert module is not None


def test_run_coordinate_id_is_deterministic() -> None:
    run_coordinate = require("RunCoordinate")
    phase = require("BenchmarkPhase")
    coordinate = run_coordinate(
        benchmark_version="v2",
        phase=phase.PILOT,
        model_config_id="G1",
        scenario_id="B1",
        prompt_variant_id="V1",
        repetition=1,
        case_seed=17,
    )

    assert coordinate.run_id == run_coordinate(**coordinate.identity_fields()).run_id


def test_run_coordinate_id_changes_when_repetition_changes() -> None:
    run_coordinate = require("RunCoordinate")
    phase = require("BenchmarkPhase")
    common = {
        "benchmark_version": "v2",
        "phase": phase.FINAL,
        "model_config_id": "D1",
        "scenario_id": "A6",
        "prompt_variant_id": "V3",
        "case_seed": 19,
    }

    assert run_coordinate(repetition=1, **common).run_id != run_coordinate(
        repetition=2, **common
    ).run_id


def test_model_configuration_preserves_unavailable_metadata() -> None:
    model_configuration = require("ModelConfiguration")
    provider = require("ProviderFamily")
    config = model_configuration(
        model_config_id="D1",
        provider=provider.DEEPSEEK,
        requested_model="deepseek-v4-pro",
        endpoint_origin="https://api.deepseek.com",
        api_dialect="anthropic-compatible",
    )

    serialized = config.to_dict()

    assert serialized["exposed_model_revision"] == "unavailable"
    assert serialized["temperature"] == "unavailable"
    assert serialized["seed"] == "unavailable"


def test_model_configuration_serializes_explicit_output_token_cap() -> None:
    model_configuration = require("ModelConfiguration")
    provider = require("ProviderFamily")
    config = model_configuration(
        model_config_id="D2b",
        provider=provider.DEEPSEEK,
        requested_model="deepseek-v4-pro",
        endpoint_origin="https://api.deepseek.com",
        api_dialect="anthropic-compatible",
        output_token_cap=8192,
    )

    assert config.to_dict()["output_token_cap"] == 8192
