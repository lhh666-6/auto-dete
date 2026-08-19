"""Strict evidence-backed AI output contracts."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models import AIStatus


class AISuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    field_name: str
    current_candidate: Any
    suggested_value: Any
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_types: tuple[str, ...] = Field(min_length=1)
    reason: str = Field(min_length=1)


class AIReview(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    form_id: str
    status: AIStatus
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"]
    summary: str
    suggestions: tuple[AISuggestion, ...]
    missing_information: tuple[str, ...]
    requires_human_confirmation: Literal[True] = True
