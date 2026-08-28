"""Deterministic immutable run planning and resume selection."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable, Sequence

from .schema import BenchmarkPhase, ModelConfiguration, RunCoordinate
from .scenarios import ScenarioSpec


@dataclass(frozen=True, slots=True)
class PlannedRun:
    coordinate: RunCoordinate
    provider: str
    requested_model: str
    scenario_title: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.coordinate.run_id,
            **{
                key: value.value if isinstance(value, BenchmarkPhase) else value
                for key, value in self.coordinate.identity_fields().items()
            },
            "provider": self.provider,
            "requested_model": self.requested_model,
            "scenario_title": self.scenario_title,
        }


def _case_seed(
    benchmark_version: str,
    scenario_id: str,
    repetition: int,
    base_seed: int,
) -> int:
    payload = f"{benchmark_version}:{scenario_id}:{repetition}:{base_seed}"
    return int.from_bytes(sha256(payload.encode("utf-8")).digest()[:8], "big")


def build_run_plan(
    *,
    benchmark_version: str,
    phase: BenchmarkPhase,
    models: Sequence[ModelConfiguration],
    scenarios: Sequence[ScenarioSpec],
    prompt_variant_ids: Sequence[str],
    repetitions: int,
    base_seed: int,
) -> tuple[PlannedRun, ...]:
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    planned: list[PlannedRun] = []
    for model in models:
        for scenario in scenarios:
            for prompt_variant_id in prompt_variant_ids:
                for repetition in range(1, repetitions + 1):
                    coordinate = RunCoordinate(
                        benchmark_version=benchmark_version,
                        phase=phase,
                        model_config_id=model.model_config_id,
                        scenario_id=scenario.scenario_id,
                        prompt_variant_id=prompt_variant_id,
                        repetition=repetition,
                        case_seed=_case_seed(
                            benchmark_version,
                            scenario.scenario_id,
                            repetition,
                            base_seed,
                        ),
                    )
                    planned.append(
                        PlannedRun(
                            coordinate=coordinate,
                            provider=model.provider.value,
                            requested_model=model.requested_model,
                            scenario_title=scenario.title,
                        )
                    )
    run_ids = [run.coordinate.run_id for run in planned]
    if len(run_ids) != len(set(run_ids)):
        raise ValueError("run plan contains duplicate run ids")
    return tuple(planned)


def write_run_plan(path: Path, runs: Iterable[PlannedRun]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        for run in runs:
            handle.write(json.dumps(run.to_dict(), sort_keys=True, separators=(",", ":")))
            handle.write("\n")


def missing_planned_runs(
    plan: Sequence[PlannedRun], completed_run_ids: set[str]
) -> tuple[PlannedRun, ...]:
    return tuple(run for run in plan if run.coordinate.run_id not in completed_run_ids)
