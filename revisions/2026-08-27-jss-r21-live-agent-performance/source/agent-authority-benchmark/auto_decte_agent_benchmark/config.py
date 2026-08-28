"""Strict loading of phase configuration without credentials."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .schema import ModelConfiguration, ProviderFamily
from .scenarios import scenario_registry


@dataclass(frozen=True, slots=True)
class PhaseConfiguration:
    phase: str
    models: tuple[ModelConfiguration, ...]
    scenario_ids: tuple[str, ...]
    prompt_variant_ids: tuple[str, ...]
    repetitions: int
    base_seed: int

    @property
    def planned_execution_count(self) -> int:
        return (
            len(self.models)
            * len(self.scenario_ids)
            * len(self.prompt_variant_ids)
            * self.repetitions
        )


def _read_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"configuration must be an object: {path}")
    return data


def load_phase_configuration(config_root: Path, phase: str) -> PhaseConfiguration:
    models_data = _read_object(config_root / f"{phase}.models.json")
    matrix_data = _read_object(config_root / f"{phase}.matrix.json")
    raw_models = models_data.get("models", [])
    if not isinstance(raw_models, list):
        raise ValueError("models must be a list")
    models = tuple(
        ModelConfiguration(
            model_config_id=str(raw["model_config_id"]),
            provider=ProviderFamily(str(raw["provider"])),
            requested_model=str(raw["requested_model"]),
            endpoint_origin=str(raw["endpoint_origin"]),
            api_dialect=str(raw["api_dialect"]),
            exposed_model_revision=str(raw.get("exposed_model_revision", "unavailable")),
            cli_or_api_version=str(raw.get("cli_or_api_version", "unavailable")),
            reasoning_config=str(raw.get("reasoning_config", "unavailable")),
            temperature=raw.get("temperature", "unavailable"),
            seed=raw.get("seed", "unavailable"),
        )
        for raw in raw_models
        if isinstance(raw, dict)
    )
    model_ids = [model.model_config_id for model in models]
    if len(model_ids) != len(set(model_ids)):
        raise ValueError("duplicate model_config_id")
    scenario_ids = tuple(str(value) for value in matrix_data.get("scenario_ids", ()))
    if not scenario_ids:
        scenario_ids = tuple(scenario.scenario_id for scenario in scenario_registry())
    expected_scenarios = tuple(scenario.scenario_id for scenario in scenario_registry())
    if scenario_ids != expected_scenarios:
        raise ValueError("matrix must contain the exact frozen scenario registry")
    variants = tuple(str(value) for value in matrix_data.get("prompt_variant_ids", ()))
    repetitions = int(matrix_data.get("repetitions", 0))
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    return PhaseConfiguration(
        phase=phase,
        models=models,
        scenario_ids=scenario_ids,
        prompt_variant_ids=variants,
        repetitions=repetitions,
        base_seed=int(matrix_data.get("base_seed", 0)),
    )
