"""Convert provider-specific live invocations into one execution envelope."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from .execution import InvocationEnvelope


class ModelBridge(Protocol):
    def model(self, operation: str, **values: object) -> dict[str, Any]: ...


def invoke_deepseek(
    *,
    adapter: Any,
    request_sender: Callable[[dict[str, Any], float], Mapping[str, Any]],
    bridge: ModelBridge,
    prompt: str,
    timeout_seconds: float,
) -> InvocationEnvelope:
    operation_by_tool = {
        "auto_decte_propose": "propose",
        "auto_decte_verify": "verify",
    }

    def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name not in operation_by_tool:
            raise ValueError(f"unknown model tool: {name}")
        return bridge.model(operation_by_tool[name], **arguments)

    result = adapter.invoke(
        prompt=prompt,
        tool_executor=execute_tool,
        request_sender=request_sender,
        timeout_seconds=timeout_seconds,
    )
    raw = json.dumps(
        list(result.raw_responses),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return InvocationEnvelope(
        events=tuple(result.events),
        raw_payloads={"deepseek-rounds.json": raw + "\n"},
        stderr="",
        returncode=result.returncode,
        latency_ms=result.latency_ms,
        transport_error=result.transport_error,
    )


def invoke_openai_codex(
    *,
    adapter: Any,
    codex: Path,
    workspace: Path,
    server_python: Path,
    server_source: Path,
    implementation_root: Path,
    implementation_python: Path,
    data_root: Path,
    prompt: str,
    timeout_seconds: float,
) -> InvocationEnvelope:
    result = adapter.invoke(
        codex=codex,
        workspace=workspace.resolve(),
        server_python=server_python.resolve(),
        server_source=server_source.resolve(),
        server_args=(
            "-m",
            "auto_decte_agent_benchmark.mcp_server",
            "--data-root",
            str(data_root.resolve()),
            "--implementation-root",
            str(implementation_root.resolve()),
            "--python",
            str(implementation_python.resolve()),
        ),
        prompt=prompt,
        timeout_seconds=timeout_seconds,
    )
    return InvocationEnvelope(
        events=tuple(result.events),
        raw_payloads={"openai.jsonl": result.raw_payload},
        stderr=result.stderr,
        returncode=result.returncode,
        latency_ms=result.latency_ms,
        transport_error=result.transport_error,
    )
