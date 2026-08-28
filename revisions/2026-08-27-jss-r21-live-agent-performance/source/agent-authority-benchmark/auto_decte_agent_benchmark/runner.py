"""Run-plan validation and gated benchmark entry point."""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .config import load_phase_configuration
from .generator import build_fixture_spec
from .ledger import PlannedRun, build_run_plan
from .prompts import render_prompt
from .scenario_builders import prepare_scenario
from .schema import BenchmarkPhase
from .scenarios import scenario_registry
from .tool_surface import (
    assert_logical_tool_equivalence,
    canonical_tool_surface,
    deepseek_tool_schemas,
    openai_tool_schemas,
)


def build_phase_plan(*, config_root: Path, phase: str) -> tuple[PlannedRun, ...]:
    configuration = load_phase_configuration(config_root, phase)
    scenarios_by_id = {scenario.scenario_id: scenario for scenario in scenario_registry()}
    scenarios = tuple(scenarios_by_id[scenario_id] for scenario_id in configuration.scenario_ids)
    return build_run_plan(
        benchmark_version="agent-authority-benchmark-v2",
        phase=BenchmarkPhase(phase),
        models=configuration.models,
        scenarios=scenarios,
        prompt_variant_ids=configuration.prompt_variant_ids,
        repetitions=configuration.repetitions,
        base_seed=configuration.base_seed,
    )


def dry_run(*, config_root: Path, phase: str, output_root: Path | None = None) -> dict[str, Any]:
    del output_root
    configuration = load_phase_configuration(config_root, phase)
    plan = build_phase_plan(config_root=config_root, phase=phase)
    scenarios_by_id = {scenario.scenario_id: scenario for scenario in scenario_registry()}
    semantic_groups: dict[tuple[str, str, int], set[str]] = {}
    rendered_count = 0
    for run in plan:
        scenario = scenarios_by_id[run.coordinate.scenario_id]
        fixture = build_fixture_spec(run.coordinate.case_seed)
        prepared = prepare_scenario(scenario, fixture)
        rendered = render_prompt(
            scenario,
            run.coordinate.prompt_variant_id,
            prepared.agent_context,
        )
        key = (
            run.coordinate.model_config_id,
            run.coordinate.scenario_id,
            run.coordinate.repetition,
        )
        semantic_groups.setdefault(key, set()).add(rendered.semantic_payload_sha256)
        rendered_count += 1
    if any(len(hashes) != 1 for hashes in semantic_groups.values()):
        raise ValueError("prompt variants changed scenario semantics")
    surface = canonical_tool_surface()
    assert_logical_tool_equivalence(
        surface,
        {
            "openai": openai_tool_schemas(surface),
            "deepseek": deepseek_tool_schemas(surface),
        },
    )
    canonical = json.dumps(
        [run.to_dict() for run in plan], sort_keys=True, separators=(",", ":")
    )
    provider_counts = Counter(model.provider.value for model in configuration.models)
    return {
        "schema_version": "agent-authority-dry-run.v2",
        "phase": phase,
        "planned_executions": len(plan),
        "model_configurations": len(configuration.models),
        "provider_counts": dict(provider_counts),
        "scenarios": len(configuration.scenario_ids),
        "prompt_variants": len(configuration.prompt_variant_ids),
        "repetitions": configuration.repetitions,
        "rendered_prompts": rendered_count,
        "scenario_builder_validations": rendered_count,
        "semantic_equivalence_groups": len(semantic_groups),
        "logical_tool_surface_equivalent": True,
        "run_plan_sha256": sha256(canonical.encode("utf-8")).hexdigest(),
        "model_calls": 0,
        "database_writes": 0,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-root", type=Path, required=True)
    parser.add_argument("--phase", choices=("pilot", "final"), required=True)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    if not args.dry_run:
        raise SystemExit("live execution is gated; use --dry-run until the local gate passes")
    print(
        json.dumps(
            dry_run(
                config_root=args.config_root,
                phase=args.phase,
                output_root=args.output_root,
            ),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
