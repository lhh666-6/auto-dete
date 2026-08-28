"""Codex/OpenAI JSONL normalization."""

from __future__ import annotations

import json
from typing import Any

from .canonical_events import EventType, ProviderNeutralAgentEvent, validate_event_stream
from .schema import ModelConfiguration, ProviderFamily


class OpenAICodexAdapter:
    def __init__(self, configuration: ModelConfiguration) -> None:
        if configuration.provider is not ProviderFamily.OPENAI:
            raise ValueError("OpenAICodexAdapter requires an OpenAI configuration")
        self.configuration = configuration

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
