from importlib import import_module
import json

from auto_decte_agent_benchmark.schema import ModelConfiguration, ProviderFamily


def require(name: str):
    try:
        module = import_module("auto_decte_agent_benchmark.deepseek_adapter")
    except ModuleNotFoundError:
        module = None
    assert module is not None, "deepseek_adapter module is missing"
    assert hasattr(module, name), f"deepseek_adapter is missing {name}"
    return getattr(module, name)


def config() -> ModelConfiguration:
    return ModelConfiguration(
        model_config_id="D1",
        provider=ProviderFamily.DEEPSEEK,
        requested_model="deepseek-v4-pro",
        endpoint_origin="https://api.deepseek.com",
        api_dialect="anthropic-compatible",
    )


def test_non_streaming_anthropic_response_normalizes_tool_message_and_usage() -> None:
    adapter_class = require("DeepSeekAdapter")
    response = {
        "id": "msg-1",
        "type": "message",
        "model": "deepseek-v4-pro",
        "content": [
            {"type": "text", "text": "I will verify it."},
            {
                "type": "tool_use",
                "id": "toolu-1",
                "name": "auto_decte_verify",
                "input": {"certificate_id": "C1"},
            },
        ],
        "usage": {"input_tokens": 20, "output_tokens": 7},
    }

    events = adapter_class(config()).normalize_response(response, raw_pointer="raw/ds.json")

    assert [event.event_type.value for event in events] == [
        "RUN_STARTED",
        "ASSISTANT_MESSAGE",
        "TOOL_CALL",
        "MODEL_USAGE",
        "RUN_COMPLETED",
    ]
    assert events[2].tool_name == "auto_decte_verify"
    assert events[2].tool_arguments == {"certificate_id": "C1"}


def test_streamed_partial_tool_json_normalizes_to_same_arguments() -> None:
    adapter_class = require("DeepSeekAdapter")
    records = [
        {"type": "message_start", "message": {"usage": {"input_tokens": 20}}},
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {
                "type": "tool_use",
                "id": "toolu-1",
                "name": "auto_decte_verify",
                "input": {},
            },
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "input_json_delta", "partial_json": '{"certificate_id":'},
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "input_json_delta", "partial_json": '"C1"}'},
        },
        {"type": "content_block_stop", "index": 0},
        {"type": "message_delta", "usage": {"output_tokens": 7}},
        {"type": "message_stop"},
    ]
    raw_sse = "\n".join(f"data: {json.dumps(record)}" for record in records)

    events = adapter_class(config()).normalize_stream(raw_sse, raw_pointer="raw/ds.sse")
    tool_call = next(event for event in events if event.event_type.value == "TOOL_CALL")

    assert tool_call.tool_name == "auto_decte_verify"
    assert tool_call.tool_arguments == {"certificate_id": "C1"}


def test_tool_result_is_retained_as_provider_neutral_event() -> None:
    adapter_class = require("DeepSeekAdapter")
    adapter = adapter_class(config())

    event = adapter.tool_result_event(
        tool_name="auto_decte_verify",
        result={"verified": True},
        event_index=3,
        raw_pointer="raw/tool-result.json",
    )

    assert event.event_type.value == "TOOL_RESULT"
    assert event.tool_name == "auto_decte_verify"
    assert event.tool_result == {"verified": True}
