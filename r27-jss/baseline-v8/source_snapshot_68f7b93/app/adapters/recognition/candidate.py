"""Common recognition candidate value object."""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class RecognitionCandidate(Generic[T]):
    value: T | None
    confidence: float
    engine: str
    model_version: str
    reason_code: str
    accepted: bool = True
    decision_score: float | None = None
