from importlib import import_module

import pytest

from auto_decte_agent_benchmark.schema import ProviderFamily


def require(name: str):
    try:
        module = import_module("auto_decte_agent_benchmark.canonical_events")
    except ModuleNotFoundError:
        module = None
    assert module is not None, "canonical_events module is missing"
    assert hasattr(module, name), f"canonical_events is missing {name}"
    return getattr(module, name)


def test_tool_call_event_retains_canonical_arguments_and_raw_pointer() -> None:
    event_type = require("EventType")
    event_class = require("ProviderNeutralAgentEvent")
    event = event_class(
        provider=ProviderFamily.DEEPSEEK,
        model_config_id="D1",
        timestamp="2026-08-28T00:00:00Z",
        event_index=1,
        event_type=event_type.TOOL_CALL,
        tool_name="auto_decte_verify",
        tool_arguments={"certificate_id": "cert-1", "record_id": "record-1"},
        raw_event_pointer="raw/0001.json",
    )

    serialized = event.to_dict()

    assert serialized["provider"] == "deepseek"
    assert serialized["tool_arguments"] == {
        "certificate_id": "cert-1",
        "record_id": "record-1",
    }
    assert serialized["raw_event_pointer"] == "raw/0001.json"


def test_tool_call_event_rejects_missing_tool_name() -> None:
    event_type = require("EventType")
    event_class = require("ProviderNeutralAgentEvent")

    with pytest.raises(ValueError, match="tool_name"):
        event_class(
            provider=ProviderFamily.OPENAI,
            model_config_id="G1",
            timestamp="2026-08-28T00:00:00Z",
            event_index=1,
            event_type=event_type.TOOL_CALL,
            tool_arguments={},
            raw_event_pointer="raw/0001.jsonl#1",
        )


def test_event_stream_rejects_provider_changes_within_one_run() -> None:
    event_type = require("EventType")
    event_class = require("ProviderNeutralAgentEvent")
    validate = require("validate_event_stream")
    events = [
        event_class(
            provider=ProviderFamily.OPENAI,
            model_config_id="G1",
            timestamp="2026-08-28T00:00:00Z",
            event_index=0,
            event_type=event_type.RUN_STARTED,
            raw_event_pointer="raw/0000.jsonl#0",
        ),
        event_class(
            provider=ProviderFamily.DEEPSEEK,
            model_config_id="D1",
            timestamp="2026-08-28T00:00:01Z",
            event_index=1,
            event_type=event_type.RUN_COMPLETED,
            raw_event_pointer="raw/0001.json#1",
        ),
    ]

    with pytest.raises(ValueError, match="provider"):
        validate(events)
