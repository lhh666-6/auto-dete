from importlib import import_module
import json
from pathlib import Path
import subprocess

from auto_decte_agent_benchmark.schema import ModelConfiguration, ProviderFamily


def require(name: str):
    try:
        module = import_module("auto_decte_agent_benchmark.openai_adapter")
    except ModuleNotFoundError:
        module = None
    assert module is not None, "openai_adapter module is missing"
    assert hasattr(module, name), f"openai_adapter is missing {name}"
    return getattr(module, name)


def config() -> ModelConfiguration:
    return ModelConfiguration(
        model_config_id="G1",
        provider=ProviderFamily.OPENAI,
        requested_model="requested-gpt-alias",
        endpoint_origin="codex-cli",
        api_dialect="codex-jsonl",
    )


def test_codex_jsonl_normalizes_tool_call_message_and_usage() -> None:
    adapter_class = require("OpenAICodexAdapter")
    raw = "\n".join(
        json.dumps(event)
        for event in (
            {"type": "thread.started", "thread_id": "thread-1"},
            {
                "type": "item.completed",
                "item": {
                    "type": "mcp_tool_call",
                    "tool": "auto_decte_propose",
                    "arguments": {"value": 8},
                    "result": {"certificate_id": "C1"},
                    "status": "completed",
                },
            },
            {"type": "item.completed", "item": {"type": "agent_message", "text": "done"}},
            {"type": "turn.completed", "usage": {"input_tokens": 12, "output_tokens": 4}},
        )
    )

    events = adapter_class(config()).normalize(raw, raw_pointer="raw/openai.jsonl")

    assert [event.event_type.value for event in events] == [
        "RUN_STARTED",
        "TOOL_CALL",
        "TOOL_RESULT",
        "ASSISTANT_MESSAGE",
        "MODEL_USAGE",
        "RUN_COMPLETED",
    ]
    assert events[1].tool_name == "auto_decte_propose"
    assert events[1].tool_arguments == {"value": 8}
    assert events[2].tool_result == {"certificate_id": "C1"}
    assert events[4].usage == {"input_tokens": 12, "output_tokens": 4}
    assert [event.event_index for event in events] == list(range(len(events)))


def test_codex_error_event_normalizes_as_transport_error() -> None:
    adapter_class = require("OpenAICodexAdapter")
    raw = json.dumps({"type": "error", "message": "rate limited"})

    events = adapter_class(config()).normalize(raw, raw_pointer="raw/error.jsonl")

    assert any(event.event_type.value == "TRANSPORT_ERROR" for event in events)
    assert any(event.message_text == "rate limited" for event in events)


def test_codex_command_exposes_only_two_tools_and_frozen_reasoning() -> None:
    adapter = require("OpenAICodexAdapter")(config())

    command = adapter.build_command(
        codex=Path("C:/tools/codex.exe"),
        workspace=Path("C:/workspace"),
        server_python=Path("C:/python/python.exe"),
        server_source=Path("C:/benchmark/source"),
        server_args=("--run-root", "C:/runs/R1"),
        prompt="bounded prompt",
    )
    joined = " ".join(command)

    assert "gpt-5.6" not in joined
    assert "requested-gpt-alias" in command
    assert "model_reasoning_effort='low'" in command
    assert "enabled_tools=['auto_decte_propose','auto_decte_verify']" in joined
    assert "default_tools_approval_mode='approve'" in joined
    assert "-s read-only" in joined


def test_codex_invoke_retains_raw_output_stderr_and_latency(tmp_path) -> None:
    adapter = require("OpenAICodexAdapter")(config())
    observed: dict[str, object] = {}

    def fake_run(command, **kwargs):
        observed["command"] = command
        observed["kwargs"] = kwargs
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({"type": "turn.completed", "usage": {"input_tokens": 3}}),
            stderr="provider diagnostic",
        )

    result = adapter.invoke(
        codex=Path("C:/tools/codex.exe"),
        workspace=tmp_path,
        server_python=Path("C:/python/python.exe"),
        server_source=Path("C:/benchmark/source"),
        server_args=("--run-root", str(tmp_path / "run")),
        prompt="bounded prompt",
        timeout_seconds=12.0,
        command_runner=fake_run,
    )

    assert result.returncode == 0
    assert result.raw_payload
    assert result.stderr == "provider diagnostic"
    assert result.latency_ms >= 0
    assert result.transport_error is None
    assert any(event.event_type.value == "MODEL_USAGE" for event in result.events)
    assert observed["kwargs"]["timeout"] == 12.0
