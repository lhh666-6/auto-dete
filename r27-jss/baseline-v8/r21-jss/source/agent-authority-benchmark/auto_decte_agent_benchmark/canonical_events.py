"""Provider-neutral model interaction events."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping, Sequence

from .schema import ProviderFamily


class EventType(StrEnum):
    RUN_STARTED = "RUN_STARTED"
    ASSISTANT_MESSAGE = "ASSISTANT_MESSAGE"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    MODEL_USAGE = "MODEL_USAGE"
    TRANSPORT_ERROR = "TRANSPORT_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    RUN_COMPLETED = "RUN_COMPLETED"


@dataclass(frozen=True, slots=True)
class ProviderNeutralAgentEvent:
    provider: ProviderFamily
    model_config_id: str
    timestamp: str
    event_index: int
    event_type: EventType
    raw_event_pointer: str
    tool_name: str | None = None
    tool_arguments: Mapping[str, Any] = field(default_factory=dict)
    tool_result: Any = None
    message_text: str | None = None
    usage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.event_index < 0:
            raise ValueError("event_index must be non-negative")
        if not self.raw_event_pointer:
            raise ValueError("raw_event_pointer is required")
        if self.event_type is EventType.TOOL_CALL and not self.tool_name:
            raise ValueError("tool_name is required for TOOL_CALL")

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider.value,
            "model_config_id": self.model_config_id,
            "timestamp": self.timestamp,
            "event_index": self.event_index,
            "event_type": self.event_type.value,
            "tool_name": self.tool_name,
            "tool_arguments": dict(self.tool_arguments),
            "tool_result": self.tool_result,
            "message_text": self.message_text,
            "usage": dict(self.usage),
            "raw_event_pointer": self.raw_event_pointer,
        }


def validate_event_stream(events: Sequence[ProviderNeutralAgentEvent]) -> None:
    if not events:
        raise ValueError("event stream must not be empty")
    provider = events[0].provider
    model_config_id = events[0].model_config_id
    for expected_index, event in enumerate(events):
        if event.provider is not provider:
            raise ValueError("provider changed within one run")
        if event.model_config_id != model_config_id:
            raise ValueError("model_config_id changed within one run")
        if event.event_index != expected_index:
            raise ValueError("event_index must be contiguous and ordered")
