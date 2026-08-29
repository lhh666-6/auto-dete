"""Anthropic-compatible DeepSeek response normalization."""

from __future__ import annotations

import json
from dataclasses import dataclass
from time import monotonic
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen as default_urlopen

from .canonical_events import EventType, ProviderNeutralAgentEvent, validate_event_stream
from .schema import ModelConfiguration, ProviderFamily
from .tool_surface import canonical_tool_surface, deepseek_tool_schemas


@dataclass(frozen=True, slots=True)
class DeepSeekInvocationResult:
    raw_responses: tuple[Mapping[str, Any], ...]
    returncode: int
    latency_ms: int
    transport_error: str | None
    events: tuple[ProviderNeutralAgentEvent, ...]


class DeepSeekHTTPClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        urlopen: Callable[..., Any] = default_urlopen,
    ) -> None:
        if not api_key:
            raise ValueError("DeepSeek API key is required")
        self._endpoint = f"{base_url.rstrip('/')}/v1/messages"
        self._api_key = api_key
        self._urlopen = urlopen

    def __repr__(self) -> str:
        return f"DeepSeekHTTPClient(endpoint={self._endpoint!r}, api_key=<redacted>)"

    def send(self, payload: dict[str, Any], timeout_seconds: float) -> Mapping[str, Any]:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        request = Request(
            self._endpoint,
            data=body,
            method="POST",
            headers={
                "content-type": "application/json",
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        try:
            with self._urlopen(request, timeout=timeout_seconds) as response:
                raw = response.read()
        except HTTPError as error:
            raise RuntimeError(f"DEEPSEEK_HTTP_{error.code}") from None
        except (URLError, TimeoutError) as error:
            raise RuntimeError(f"DEEPSEEK_TRANSPORT_{type(error).__name__}") from None
        try:
            decoded = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RuntimeError("DEEPSEEK_MALFORMED_JSON") from None
        if not isinstance(decoded, Mapping):
            raise RuntimeError("DEEPSEEK_RESPONSE_NOT_OBJECT")
        return decoded


class DeepSeekAdapter:
    def __init__(self, configuration: ModelConfiguration) -> None:
        if configuration.provider is not ProviderFamily.DEEPSEEK:
            raise ValueError("DeepSeekAdapter requires a DeepSeek configuration")
        self.configuration = configuration

    def build_request(self, *, prompt: str) -> dict[str, Any]:
        return {
            "model": self.configuration.requested_model,
            "max_tokens": 4096,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
            "tools": deepseek_tool_schemas(canonical_tool_surface()),
        }

    def invoke(
        self,
        *,
        prompt: str,
        tool_executor: Callable[[str, dict[str, Any]], Any],
        request_sender: Callable[[dict[str, Any], float], Mapping[str, Any]],
        timeout_seconds: float,
        max_rounds: int = 8,
    ) -> DeepSeekInvocationResult:
        request = self.build_request(prompt=prompt)
        responses: list[Mapping[str, Any]] = []
        pending: list[dict[str, Any]] = [
            {"event_type": EventType.RUN_STARTED, "raw_event_pointer": "raw/deepseek.json#start"}
        ]
        allowed_tools = {tool["name"] for tool in canonical_tool_surface()["tools"]}
        started = monotonic()
        returncode = 0
        transport_error: str | None = None
        for round_index in range(max_rounds):
            try:
                response = request_sender(request, timeout_seconds)
            except Exception as error:  # provider clients expose heterogeneous transport errors
                transport_error = f"{type(error).__name__}: {error}"
                returncode = -1
                pending.append(
                    {
                        "event_type": EventType.TRANSPORT_ERROR,
                        "message_text": transport_error,
                        "raw_event_pointer": f"raw/deepseek.json#round[{round_index}]",
                    }
                )
                break
            responses.append(response)
            content = response.get("content", [])
            blocks = content if isinstance(content, list) else []
            tool_results: list[dict[str, Any]] = []
            saw_semantic_content = False
            for block_index, raw_block in enumerate(blocks):
                block = raw_block if isinstance(raw_block, Mapping) else {}
                pointer = f"raw/deepseek.json#round[{round_index}].content[{block_index}]"
                if block.get("type") == "text":
                    saw_semantic_content = True
                    pending.append(
                        {
                            "event_type": EventType.ASSISTANT_MESSAGE,
                            "message_text": str(block.get("text", "")),
                            "raw_event_pointer": pointer,
                        }
                    )
                elif block.get("type") == "tool_use":
                    saw_semantic_content = True
                    name = str(block.get("name", ""))
                    raw_arguments = block.get("input", {})
                    arguments = dict(raw_arguments) if isinstance(raw_arguments, Mapping) else {}
                    pending.append(
                        {
                            "event_type": EventType.TOOL_CALL,
                            "tool_name": name,
                            "tool_arguments": arguments,
                            "raw_event_pointer": pointer,
                        }
                    )
                    if name not in allowed_tools:
                        returncode = 1
                        pending.append(
                            {
                                "event_type": EventType.RUNTIME_ERROR,
                                "message_text": f"UNKNOWN_TOOL:{name}",
                                "raw_event_pointer": pointer,
                            }
                        )
                        break
                    result = tool_executor(name, arguments)
                    pending.append(
                        {
                            "event_type": EventType.TOOL_RESULT,
                            "tool_name": name,
                            "tool_result": result,
                            "raw_event_pointer": f"{pointer}.result",
                        }
                    )
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": str(block.get("id", "")),
                            "content": json.dumps(
                                result,
                                sort_keys=True,
                                separators=(",", ":"),
                            ),
                        }
                    )
            usage = response.get("usage", {})
            if isinstance(usage, Mapping) and usage:
                pending.append(
                    {
                        "event_type": EventType.MODEL_USAGE,
                        "usage": dict(usage),
                        "raw_event_pointer": f"raw/deepseek.json#round[{round_index}].usage",
                    }
                )
            if returncode != 0:
                break
            if response.get("stop_reason") == "max_tokens" and not saw_semantic_content:
                returncode = 1
                pending.append(
                    {
                        "event_type": EventType.RUNTIME_ERROR,
                        "message_text": "INVALID_OUTPUT_MAX_TOKENS",
                        "raw_event_pointer": f"raw/deepseek.json#round[{round_index}]",
                    }
                )
                break
            if not tool_results:
                break
            request["messages"] = [
                *request["messages"],
                {"role": "assistant", "content": blocks},
                {"role": "user", "content": tool_results},
            ]
        else:
            returncode = 1
            pending.append(
                {
                    "event_type": EventType.RUNTIME_ERROR,
                    "message_text": "MAX_TOOL_ROUNDS_EXCEEDED",
                    "raw_event_pointer": "raw/deepseek.json#end",
                }
            )
        pending.append(
            {"event_type": EventType.RUN_COMPLETED, "raw_event_pointer": "raw/deepseek.json#end"}
        )
        latency_ms = round((monotonic() - started) * 1000)
        return DeepSeekInvocationResult(
            raw_responses=tuple(responses),
            returncode=returncode,
            latency_ms=latency_ms,
            transport_error=transport_error,
            events=self._finalize(pending),
        )

    def _event(self, *, event_index: int, event_type: EventType, **values: Any):
        return ProviderNeutralAgentEvent(
            provider=self.configuration.provider,
            model_config_id=self.configuration.model_config_id,
            timestamp="unavailable",
            event_index=event_index,
            event_type=event_type,
            **values,
        )

    def normalize_response(
        self,
        response: Mapping[str, Any],
        *,
        raw_pointer: str,
    ) -> tuple[ProviderNeutralAgentEvent, ...]:
        pending: list[dict[str, Any]] = [
            {"event_type": EventType.RUN_STARTED, "raw_event_pointer": f"{raw_pointer}#start"}
        ]
        content = response.get("content", [])
        if isinstance(content, list):
            for block_index, raw_block in enumerate(content):
                block = raw_block if isinstance(raw_block, Mapping) else {}
                pointer = f"{raw_pointer}#content[{block_index}]"
                if block.get("type") == "text":
                    pending.append(
                        {
                            "event_type": EventType.ASSISTANT_MESSAGE,
                            "message_text": str(block.get("text", "")),
                            "raw_event_pointer": pointer,
                        }
                    )
                elif block.get("type") == "tool_use":
                    raw_input = block.get("input", {})
                    pending.append(
                        {
                            "event_type": EventType.TOOL_CALL,
                            "tool_name": str(block.get("name", "")),
                            "tool_arguments": dict(raw_input)
                            if isinstance(raw_input, Mapping)
                            else {},
                            "raw_event_pointer": pointer,
                        }
                    )
        usage = response.get("usage", {})
        if isinstance(usage, Mapping) and usage:
            pending.append(
                {
                    "event_type": EventType.MODEL_USAGE,
                    "usage": dict(usage),
                    "raw_event_pointer": f"{raw_pointer}#usage",
                }
            )
        pending.append(
            {"event_type": EventType.RUN_COMPLETED, "raw_event_pointer": f"{raw_pointer}#end"}
        )
        return self._finalize(pending)

    def normalize_stream(
        self,
        raw_sse: str,
        *,
        raw_pointer: str,
    ) -> tuple[ProviderNeutralAgentEvent, ...]:
        pending: list[dict[str, Any]] = [
            {"event_type": EventType.RUN_STARTED, "raw_event_pointer": f"{raw_pointer}#start"}
        ]
        blocks: dict[int, dict[str, Any]] = {}
        usage: dict[str, Any] = {}
        for line_number, raw_line in enumerate(raw_sse.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("event:"):
                continue
            payload = line[5:].strip() if line.startswith("data:") else line
            if payload == "[DONE]":
                continue
            pointer = f"{raw_pointer}#{line_number}"
            try:
                record = json.loads(payload)
            except json.JSONDecodeError:
                pending.append(
                    {
                        "event_type": EventType.TRANSPORT_ERROR,
                        "message_text": "NON_JSON_SSE_EVENT",
                        "raw_event_pointer": pointer,
                    }
                )
                continue
            record_type = record.get("type")
            if record_type == "message_start":
                message = record.get("message", {})
                initial_usage = message.get("usage", {}) if isinstance(message, Mapping) else {}
                if isinstance(initial_usage, Mapping):
                    usage.update(initial_usage)
            elif record_type == "content_block_start":
                index = int(record.get("index", 0))
                raw_block = record.get("content_block", {})
                block = dict(raw_block) if isinstance(raw_block, Mapping) else {}
                block["pointer"] = pointer
                block["partial_json"] = ""
                block["text_chunks"] = []
                blocks[index] = block
            elif record_type == "content_block_delta":
                index = int(record.get("index", 0))
                delta = record.get("delta", {})
                block = blocks.setdefault(index, {"pointer": pointer, "text_chunks": []})
                if isinstance(delta, Mapping) and delta.get("type") == "input_json_delta":
                    block["partial_json"] = str(block.get("partial_json", "")) + str(
                        delta.get("partial_json", "")
                    )
                elif isinstance(delta, Mapping) and delta.get("type") == "text_delta":
                    block.setdefault("text_chunks", []).append(str(delta.get("text", "")))
            elif record_type == "content_block_stop":
                self._finish_stream_block(int(record.get("index", 0)), blocks, pending)
            elif record_type == "message_delta":
                delta_usage = record.get("usage", {})
                if isinstance(delta_usage, Mapping):
                    usage.update(delta_usage)
        if usage:
            pending.append(
                {
                    "event_type": EventType.MODEL_USAGE,
                    "usage": usage,
                    "raw_event_pointer": f"{raw_pointer}#usage",
                }
            )
        pending.append(
            {"event_type": EventType.RUN_COMPLETED, "raw_event_pointer": f"{raw_pointer}#end"}
        )
        return self._finalize(pending)

    @staticmethod
    def _finish_stream_block(
        index: int,
        blocks: dict[int, dict[str, Any]],
        pending: list[dict[str, Any]],
    ) -> None:
        block = blocks.pop(index, {})
        pointer = str(block.get("pointer", "stream#unknown"))
        if block.get("type") == "tool_use":
            partial = str(block.get("partial_json", ""))
            raw_input = block.get("input", {})
            try:
                arguments = json.loads(partial) if partial else dict(raw_input)
            except (json.JSONDecodeError, TypeError, ValueError):
                pending.append(
                    {
                        "event_type": EventType.RUNTIME_ERROR,
                        "message_text": "MALFORMED_TOOL_ARGUMENTS",
                        "raw_event_pointer": pointer,
                    }
                )
                return
            pending.append(
                {
                    "event_type": EventType.TOOL_CALL,
                    "tool_name": str(block.get("name", "")),
                    "tool_arguments": arguments if isinstance(arguments, dict) else {},
                    "raw_event_pointer": pointer,
                }
            )
        elif block.get("type") == "text":
            pending.append(
                {
                    "event_type": EventType.ASSISTANT_MESSAGE,
                    "message_text": "".join(block.get("text_chunks", [])),
                    "raw_event_pointer": pointer,
                }
            )

    def tool_result_event(
        self,
        *,
        tool_name: str,
        result: Any,
        event_index: int,
        raw_pointer: str,
    ) -> ProviderNeutralAgentEvent:
        return self._event(
            event_index=event_index,
            event_type=EventType.TOOL_RESULT,
            tool_name=tool_name,
            tool_result=result,
            raw_event_pointer=raw_pointer,
        )

    def _finalize(self, pending: list[dict[str, Any]]) -> tuple[ProviderNeutralAgentEvent, ...]:
        events = tuple(
            self._event(event_index=index, **values) for index, values in enumerate(pending)
        )
        validate_event_stream(events)
        return events
