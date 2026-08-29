from importlib import import_module
from io import BytesIO
import json
from urllib.error import HTTPError

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


def test_deepseek_request_uses_only_canonical_tools_and_frozen_parameters() -> None:
    adapter = require("DeepSeekAdapter")(config())

    request = adapter.build_request(prompt="bounded prompt")

    assert request["model"] == "deepseek-v4-pro"
    assert request["temperature"] == 0
    assert request["max_tokens"] == 4096
    assert [tool["name"] for tool in request["tools"]] == [
        "auto_decte_propose",
        "auto_decte_verify",
    ]


def test_deepseek_invoke_executes_tool_loop_and_retains_every_round() -> None:
    adapter = require("DeepSeekAdapter")(config())
    requests: list[dict] = []
    tool_calls: list[tuple[str, dict]] = []
    responses = iter(
        (
            {
                "id": "m1",
                "model": "deepseek-v4-pro",
                "stop_reason": "tool_use",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "toolu-1",
                        "name": "auto_decte_verify",
                        "input": {"certificate_id": "C1"},
                    }
                ],
                "usage": {"input_tokens": 10, "output_tokens": 3},
            },
            {
                "id": "m2",
                "model": "deepseek-v4-pro",
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": "verified"}],
                "usage": {"input_tokens": 14, "output_tokens": 2},
            },
        )
    )

    def fake_send(payload: dict, timeout_seconds: float) -> dict:
        requests.append(payload)
        assert timeout_seconds == 20.0
        return next(responses)

    def fake_tool(name: str, arguments: dict) -> dict:
        tool_calls.append((name, arguments))
        return {"verified": True, "certificate_id": arguments["certificate_id"]}

    result = adapter.invoke(
        prompt="bounded prompt",
        tool_executor=fake_tool,
        request_sender=fake_send,
        timeout_seconds=20.0,
    )

    assert result.transport_error is None
    assert result.returncode == 0
    assert len(result.raw_responses) == 2
    assert tool_calls == [("auto_decte_verify", {"certificate_id": "C1"})]
    assert requests[1]["messages"][-1]["role"] == "user"
    assert requests[1]["messages"][-1]["content"][0] == {
        "type": "tool_result",
        "tool_use_id": "toolu-1",
        "content": '{"certificate_id":"C1","verified":true}',
    }
    assert [event.event_type.value for event in result.events].count("TOOL_CALL") == 1
    assert [event.event_type.value for event in result.events].count("TOOL_RESULT") == 1


def test_deepseek_tool_loop_rejects_unknown_tool_without_executing_it() -> None:
    adapter = require("DeepSeekAdapter")(config())
    response = {
        "id": "m1",
        "stop_reason": "tool_use",
        "content": [
            {"type": "tool_use", "id": "x", "name": "confirm_fact", "input": {}}
        ],
    }

    result = adapter.invoke(
        prompt="bounded prompt",
        tool_executor=lambda _name, _arguments: (_ for _ in ()).throw(AssertionError()),
        request_sender=lambda _payload, _timeout: response,
        timeout_seconds=5.0,
    )

    assert result.returncode == 1
    assert result.transport_error is None
    assert any(event.event_type.value == "RUNTIME_ERROR" for event in result.events)


def test_max_tokens_with_only_thinking_is_retained_as_invalid_output() -> None:
    adapter = require("DeepSeekAdapter")(config())
    response = {
        "id": "m1",
        "stop_reason": "max_tokens",
        "content": [{"type": "thinking", "thinking": "internal reasoning"}],
        "usage": {"input_tokens": 20, "output_tokens": 4096},
    }

    result = adapter.invoke(
        prompt="bounded prompt",
        tool_executor=lambda _name, _arguments: (_ for _ in ()).throw(AssertionError()),
        request_sender=lambda _payload, _timeout: response,
        timeout_seconds=5.0,
    )

    assert result.returncode == 1
    runtime = [event for event in result.events if event.event_type.value == "RUNTIME_ERROR"]
    assert [event.message_text for event in runtime] == ["INVALID_OUTPUT_MAX_TOKENS"]


def test_http_client_posts_anthropic_request_without_exposing_key() -> None:
    client_class = require("DeepSeekHTTPClient")
    observed: dict[str, object] = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b'{"id":"m1","content":[]}'

    def fake_open(request, timeout):
        observed["url"] = request.full_url
        observed["headers"] = dict(request.header_items())
        observed["body"] = json.loads(request.data)
        observed["timeout"] = timeout
        return Response()

    client = client_class(
        base_url="https://api.deepseek.com/anthropic",
        api_key="SECRET-KEY",
        urlopen=fake_open,
    )
    response = client.send({"model": "deepseek-v4-pro"}, 9.0)

    assert response["id"] == "m1"
    assert observed["url"] == "https://api.deepseek.com/anthropic/v1/messages"
    assert observed["headers"]["X-api-key"] == "SECRET-KEY"
    assert observed["headers"]["Anthropic-version"] == "2023-06-01"
    assert observed["timeout"] == 9.0
    assert "SECRET-KEY" not in repr(client)


def test_http_client_classifies_rate_limit_without_leaking_response_body() -> None:
    client_class = require("DeepSeekHTTPClient")

    def rate_limited(_request, timeout):
        assert timeout == 9.0
        raise HTTPError(
            "https://api.deepseek.com/anthropic/v1/messages",
            429,
            "Too Many Requests",
            {},
            BytesIO(b'{"error":"account-secret"}'),
        )

    client = client_class(
        base_url="https://api.deepseek.com/anthropic",
        api_key="SECRET-KEY",
        urlopen=rate_limited,
    )

    try:
        client.send({"model": "deepseek-v4-pro"}, 9.0)
    except RuntimeError as error:
        assert str(error) == "DEEPSEEK_HTTP_429"
        assert "SECRET-KEY" not in str(error)
        assert "account-secret" not in str(error)
    else:
        raise AssertionError("rate limit must be classified as an error")
