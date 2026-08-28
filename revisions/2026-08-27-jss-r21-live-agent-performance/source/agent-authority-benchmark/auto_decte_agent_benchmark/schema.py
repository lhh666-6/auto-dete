"""Core provider-neutral benchmark schemas."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
import json
from typing import Any


UNAVAILABLE = "unavailable"


class BenchmarkPhase(StrEnum):
    """Physically separated benchmark phases."""

    PILOT = "pilot"
    FINAL = "final"


class ProviderFamily(StrEnum):
    """Declared live-provider families."""

    OPENAI = "openai"
    DEEPSEEK = "deepseek"


@dataclass(frozen=True, slots=True)
class RunCoordinate:
    """Immutable identity coordinates for exactly one planned semantic execution."""

    benchmark_version: str
    phase: BenchmarkPhase
    model_config_id: str
    scenario_id: str
    prompt_variant_id: str
    repetition: int
    case_seed: int

    def identity_fields(self) -> dict[str, Any]:
        return {
            "benchmark_version": self.benchmark_version,
            "phase": self.phase,
            "model_config_id": self.model_config_id,
            "scenario_id": self.scenario_id,
            "prompt_variant_id": self.prompt_variant_id,
            "repetition": self.repetition,
            "case_seed": self.case_seed,
        }

    @property
    def run_id(self) -> str:
        payload = {**self.identity_fields(), "phase": self.phase.value}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ModelConfiguration:
    """Requested live-model identity with explicit unavailable metadata."""

    model_config_id: str
    provider: ProviderFamily
    requested_model: str
    endpoint_origin: str
    api_dialect: str
    exposed_model_revision: str = UNAVAILABLE
    cli_or_api_version: str = UNAVAILABLE
    reasoning_config: str = UNAVAILABLE
    temperature: float | str = UNAVAILABLE
    seed: int | str = UNAVAILABLE

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_config_id": self.model_config_id,
            "provider": self.provider.value,
            "requested_model": self.requested_model,
            "endpoint_origin": self.endpoint_origin,
            "api_dialect": self.api_dialect,
            "exposed_model_revision": self.exposed_model_revision,
            "cli_or_api_version": self.cli_or_api_version,
            "reasoning_config": self.reasoning_config,
            "temperature": self.temperature,
            "seed": self.seed,
        }
