"""Codex/OpenAI JSONL normalization."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
import subprocess
from time import monotonic
from typing import Any, Callable, Sequence

from .canonical_events import EventType, ProviderNeutralAgentEvent, validate_event_stream
from .schema import ModelConfiguration, ProviderFamily, UNAVAILABLE


DISABLED_CODEX_FEATURES = (
    "shell_tool",
    "view_image",
    "browser_use",
    "in_app_browser",
    "computer_use",
    "image_generation",
    "apps",
    "skill_search",
    "tool_suggest",
)


@dataclass(frozen=True, slots=True)
class CodexInvocationResult:
    raw_payload: str
    stderr: str
    returncode: int
    latency_ms: int
    transport_error: str | None
    events: tuple[ProviderNeutralAgentEvent, ...]


def _toml_literal(value: str | Path) -> str:
    rendered = str(value).replace("\\", "/")
    if "'" in rendered:
        raise ValueError("Codex configuration values may not contain a single quote")
    return f"'{rendered}'"


class OpenAICodexAdapter:
    def __init__(self, configuration: ModelConfiguration) -> None:
        if configuration.provider is not ProviderFamily.OPENAI:
            raise ValueError("OpenAICodexAdapter requires an OpenAI configuration")
        self.configuration = configuration

    def build_command(
        self,
        *,
        codex: Path,
        workspace: Path,
        server_python: Path,
        server_source: Path,
        server_args: Sequence[str],
        prompt: str,
    ) -> list[str]:
        reasoning = self.configuration.reasoning_config
        if reasoning == UNAVAILABLE:
            reasoning = "low"
        arguments = ",".join(_toml_literal(value) for value in server_args)
        command = [
            str(codex),
            "-a",
            "never",
        ]
        for feature in DISABLED_CODEX_FEATURES:
            command.extend(("--disable", feature))
        command.extend(
            [
            "exec",
            "--ephemeral",
            "--json",
            "--ignore-user-config",
            "--ignore-rules",
            "--skip-git-repo-check",
            "-m",
            self.configuration.requested_model,
            "-c",
            f"model_reasoning_effort='{reasoning}'",
            "-c",
            f"mcp_servers.auto_decte.command={_toml_literal(server_python)}",
            "-c",
            f"mcp_servers.auto_decte.args=[{arguments}]",
            "-c",
            (
                "mcp_servers.auto_decte.env={"
                f"PYTHONPATH={_toml_literal(server_source)},"
                "PYTHONDONTWRITEBYTECODE='1'}"
            ),
            "-c",
            "mcp_servers.auto_decte.enabled_tools=['auto_decte_propose','auto_decte_verify']",
            "-c",
            "mcp_servers.auto_decte.default_tools_approval_mode='approve'",
            "-s",
            "read-only",
            "-C",
            str(workspace),
            prompt,
            ]
        )
        return command

    def invoke(
        self,
        *,
        codex: Path,
        workspace: Path,
        server_python: Path,
        server_source: Path,
        server_args: Sequence[str],
        prompt: str,
        timeout_seconds: float,
        command_runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ) -> CodexInvocationResult:
        resolved_workspace = workspace.resolve()
        command = self.build_command(
            codex=codex,
            workspace=resolved_workspace,
            server_python=server_python,
            server_source=server_source,
            server_args=server_args,
            prompt=prompt,
        )
        started = monotonic()
        environment = os.environ.copy()
        environment.pop("CODEX_THREAD_ID", None)
        environment.pop("CODEX_SESSION_ID", None)
        try:
            completed = command_runner(
                command,
                cwd=resolved_workspace,
                env=environment,
                stdin=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
            raw_payload = completed.stdout or ""
            stderr = completed.stderr or ""
            returncode = completed.returncode
            transport_error = None if returncode == 0 else f"CODEX_RETURN_CODE_{returncode}"
        except subprocess.TimeoutExpired as error:
            raw_payload = error.stdout if isinstance(error.stdout, str) else ""
            stderr = error.stderr if isinstance(error.stderr, str) else ""
            returncode = -1
            transport_error = "CODEX_TIMEOUT"
            raw_payload += json.dumps({"type": "error", "message": transport_error}) + "\n"
        latency_ms = round((monotonic() - started) * 1000)
        return CodexInvocationResult(
            raw_payload=raw_payload,
            stderr=stderr,
            returncode=returncode,
            latency_ms=latency_ms,
            transport_error=transport_error,
            events=self.normalize(raw_payload, raw_pointer="raw/openai.jsonl"),
        )

    def normalize(
        self,
        raw_jsonl: str,
        *,
        raw_pointer: str,
    ) -> tuple[ProviderNeutralAgentEvent, ...]:
        pending: list[dict[str, Any]] = [
            {"event_type": EventType.RUN_STARTED, "raw_event_pointer": f"{raw_pointer}#start"}
        ]
        for line_number, raw_line in enumerate(raw_jsonl.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            pointer = f"{raw_pointer}#{line_number}"
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                pending.append(
                    {
                        "event_type": EventType.TRANSPORT_ERROR,
                        "message_text": "NON_JSON_EVENT",
                        "raw_event_pointer": pointer,
                    }
                )
                continue
            event_type = event.get("type")
            if event_type == "item.completed":
                self._normalize_item(event.get("item"), pointer, pending)
            elif event_type == "turn.completed":
                pending.append(
                    {
                        "event_type": EventType.MODEL_USAGE,
                        "usage": event.get("usage", {}),
                        "raw_event_pointer": pointer,
                    }
                )
            elif event_type == "error":
                pending.append(
                    {
                        "event_type": EventType.TRANSPORT_ERROR,
                        "message_text": str(event.get("message", "unknown transport error")),
                        "raw_event_pointer": pointer,
                    }
                )
        pending.append(
            {"event_type": EventType.RUN_COMPLETED, "raw_event_pointer": f"{raw_pointer}#end"}
        )
        events = tuple(
            ProviderNeutralAgentEvent(
                provider=self.configuration.provider,
                model_config_id=self.configuration.model_config_id,
                timestamp="unavailable",
                event_index=index,
                **values,
            )
            for index, values in enumerate(pending)
        )
        validate_event_stream(events)
        return events

    @staticmethod
    def _normalize_item(
        raw_item: object,
        pointer: str,
        pending: list[dict[str, Any]],
    ) -> None:
        item = raw_item if isinstance(raw_item, dict) else {}
        if item.get("type") == "mcp_tool_call":
            tool_name = str(item.get("tool", ""))
            arguments = item.get("arguments")
            pending.append(
                {
                    "event_type": EventType.TOOL_CALL,
                    "tool_name": tool_name,
                    "tool_arguments": arguments if isinstance(arguments, dict) else {},
                    "raw_event_pointer": pointer,
                }
            )
            pending.append(
                {
                    "event_type": EventType.TOOL_RESULT,
                    "tool_name": tool_name,
                    "tool_result": item.get("result", item.get("error")),
                    "raw_event_pointer": pointer,
                }
            )
        elif item.get("type") == "agent_message":
            pending.append(
                {
                    "event_type": EventType.ASSISTANT_MESSAGE,
                    "message_text": str(item.get("text", "")),
                    "raw_event_pointer": pointer,
                }
            )
