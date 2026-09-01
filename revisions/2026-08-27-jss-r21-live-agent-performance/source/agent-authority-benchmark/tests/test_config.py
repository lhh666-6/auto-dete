from importlib import import_module
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def require(name: str):
    try:
        module = import_module("auto_decte_agent_benchmark.config")
    except ModuleNotFoundError:
        module = None
    assert module is not None, "config module is missing"
    assert hasattr(module, name), f"config is missing {name}"
    return getattr(module, name)


def test_checked_in_pilot_configuration_is_four_by_fourteen_by_two_by_one() -> None:
    load = require("load_phase_configuration")

    config = load(ROOT / "config", "pilot")

    assert len(config.models) == 4
    assert [model.model_config_id for model in config.models] == ["G1", "G2", "D1", "D2"]
    assert config.prompt_variant_ids == ("V1", "V2")
    assert config.repetitions == 1
    assert config.planned_execution_count == 112


def test_checked_in_d2b_configuration_is_one_by_fourteen_by_two_by_one() -> None:
    load = require("load_phase_configuration")

    config = load(ROOT / "config-d2b", "pilot")

    assert [model.model_config_id for model in config.models] == ["D2b"]
    assert config.models[0].requested_model == "deepseek-v4-pro"
    assert config.models[0].output_token_cap == 8192
    assert config.prompt_variant_ids == ("V1", "V2")
    assert config.repetitions == 1
    assert config.planned_execution_count == 28
    retry = json.loads((ROOT / "config-d2b/retry-policy.json").read_text(encoding="utf-8"))
    assert retry["max_transport_retry"] == 0
    assert (ROOT / "config-d2b/resource-policy.json").read_bytes() == (
        ROOT / "config/resource-policy.json"
    ).read_bytes()


def test_configuration_rejects_duplicate_model_ids(tmp_path) -> None:
    load = require("load_phase_configuration")
    (tmp_path / "pilot.models.json").write_text(
        json.dumps(
            {
                "models": [
                    {
                        "model_config_id": "G1",
                        "provider": "openai",
                        "requested_model": "a",
                        "endpoint_origin": "codex",
                        "api_dialect": "codex-jsonl",
                    },
                    {
                        "model_config_id": "G1",
                        "provider": "deepseek",
                        "requested_model": "b",
                        "endpoint_origin": "https://ds",
                        "api_dialect": "anthropic",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "pilot.matrix.json").write_text(
        json.dumps({"prompt_variant_ids": ["V1", "V2"], "repetitions": 1, "base_seed": 1}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate model_config_id"):
        load(tmp_path, "pilot")


def test_configuration_loads_d2b_output_token_cap(tmp_path: Path) -> None:
    load = require("load_phase_configuration")
    (tmp_path / "pilot.models.json").write_text(
        json.dumps(
            {
                "models": [
                    {
                        "model_config_id": "D2b",
                        "provider": "deepseek",
                        "requested_model": "deepseek-v4-pro",
                        "endpoint_origin": "https://api.deepseek.com",
                        "api_dialect": "anthropic-compatible",
                        "output_token_cap": 8192,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "pilot.matrix.json").write_bytes(
        (ROOT / "config/pilot.matrix.json").read_bytes()
    )

    config = load(tmp_path, "pilot")

    assert config.planned_execution_count == 28
    assert config.models[0].model_config_id == "D2b"
    assert config.models[0].output_token_cap == 8192
