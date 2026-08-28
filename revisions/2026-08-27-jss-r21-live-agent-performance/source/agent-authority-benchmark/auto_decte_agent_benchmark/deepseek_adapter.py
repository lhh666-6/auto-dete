"""Anthropic-compatible DeepSeek response normalization."""

from __future__ import annotations

import json
from typing import Any, Mapping

from .canonical_events import EventType, ProviderNeutralAgentEvent, validate_event_stream
from .schema import ModelConfiguration, ProviderFamily


class DeepSeekAdapter:
    def __init__(self, configuration: ModelConfiguration) -> None:
        if configuration.provider is not ProviderFamily.DEEPSEEK:
            raise ValueError("DeepSeekAdapter requires a DeepSeek configuration")
        self.configuration = configuration

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
