from pathlib import Path
from types import SimpleNamespace

from auto_decte_agent_benchmark.provider_runtime import (
    invoke_deepseek,
    invoke_openai_codex,
)


class StubBridge:
    def __init__(self) -> None:
        self.calls = []

    def model(self, operation: str, **values):
        self.calls.append((operation, values))
        return {"certificate_id": "C1"}


def test_deepseek_runtime_maps_only_canonical_tool_names_to_bridge_operations() -> None:
    bridge = StubBridge()

    class Adapter:
        def invoke(self, **kwargs):
            result = kwargs["tool_executor"](
                "auto_decte_propose", {"form_id": "F1", "value": 8}
            )
            assert result == {"certificate_id": "C1"}
            assert kwargs["request_sender"]({"model": "ds"}, 3.0) == {"content": []}
            return SimpleNamespace(
                events=(),
                raw_responses=({"id": "m1"},),
                returncode=0,
                latency_ms=4,
                transport_error=None,
            )

    envelope = invoke_deepseek(
        adapter=Adapter(),
        request_sender=lambda payload, timeout: {"content": []},
        bridge=bridge,
        prompt="prompt",
        timeout_seconds=3.0,
    )

    assert bridge.calls == [("propose", {"form_id": "F1", "value": 8})]
    assert '"id":"m1"' in envelope.raw_payloads["deepseek-rounds.json"]


def test_openai_runtime_preserves_jsonl_and_stderr(tmp_path) -> None:
    class Adapter:
        def invoke(self, **kwargs):
            assert kwargs["prompt"] == "prompt"
            return SimpleNamespace(
                events=(),
                raw_payload='{"type":"turn.completed"}\n',
                stderr="diagnostic",
                returncode=0,
                latency_ms=3,
                transport_error=None,
            )

    envelope = invoke_openai_codex(
        adapter=Adapter(),
        codex=Path("C:/codex.exe"),
        workspace=tmp_path,
        server_python=Path("C:/python.exe"),
        server_source=tmp_path,
        implementation_root=tmp_path,
        implementation_python=Path("C:/implementation-python.exe"),
        data_root=tmp_path / "data",
        prompt="prompt",
        timeout_seconds=3.0,
    )

    assert envelope.raw_payloads == {"openai.jsonl": '{"type":"turn.completed"}\n'}
    assert envelope.stderr == "diagnostic"
