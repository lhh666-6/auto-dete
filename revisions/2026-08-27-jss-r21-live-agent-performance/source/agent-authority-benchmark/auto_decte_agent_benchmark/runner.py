"""Run-plan validation and gated benchmark entry point."""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

from .config import load_phase_configuration
from .generator import build_fixture_spec
from .ledger import PlannedRun, build_run_plan
from .prompts import bind_proposal_metadata, render_prompt
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


def select_phase_plan(
    plan: tuple[PlannedRun, ...],
    *,
    model_ids: tuple[str, ...] | None = None,
    scenario_ids: tuple[str, ...] | None = None,
    variant_ids: tuple[str, ...] | None = None,
) -> tuple[PlannedRun, ...]:
    selected = tuple(
        run
        for run in plan
        if (model_ids is None or run.coordinate.model_config_id in model_ids)
        and (scenario_ids is None or run.coordinate.scenario_id in scenario_ids)
        and (variant_ids is None or run.coordinate.prompt_variant_id in variant_ids)
    )
    if not selected:
        raise ValueError("selectors produced an empty run plan")
    return selected


def dry_run(
    *,
    config_root: Path,
    phase: str,
    output_root: Path | None = None,
    model_ids: tuple[str, ...] | None = None,
    scenario_ids: tuple[str, ...] | None = None,
    variant_ids: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    del output_root
    configuration = load_phase_configuration(config_root, phase)
    plan = select_phase_plan(
        build_phase_plan(config_root=config_root, phase=phase),
        model_ids=model_ids,
        scenario_ids=scenario_ids,
        variant_ids=variant_ids,
    )
    scenarios_by_id = {scenario.scenario_id: scenario for scenario in scenario_registry()}
    semantic_groups: dict[tuple[str, str, int], set[str]] = {}
    rendered_count = 0
    for run in plan:
        scenario = scenarios_by_id[run.coordinate.scenario_id]
        fixture = build_fixture_spec(run.coordinate.case_seed)
        prepared = prepare_scenario(scenario, fixture)
        prompt_context = bind_proposal_metadata(
            prepared.agent_context,
            phase=phase,
            model_config_id=run.coordinate.model_config_id,
            scenario_id=run.coordinate.scenario_id,
            repetition=run.coordinate.repetition,
        )
        rendered = render_prompt(
            scenario,
            run.coordinate.prompt_variant_id,
            prompt_context,
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
    selected_model_ids = {run.coordinate.model_config_id for run in plan}
    selected_models = tuple(
        model for model in configuration.models if model.model_config_id in selected_model_ids
    )
    provider_counts = Counter(model.provider.value for model in selected_models)
    return {
        "schema_version": "agent-authority-dry-run.v2",
        "phase": phase,
        "planned_executions": len(plan),
        "model_configurations": len(selected_models),
        "provider_counts": dict(provider_counts),
        "scenarios": len({run.coordinate.scenario_id for run in plan}),
        "prompt_variants": len({run.coordinate.prompt_variant_id for run in plan}),
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
    phase = parser.add_mutually_exclusive_group(required=True)
    phase.add_argument("--pilot", action="store_true")
    phase.add_argument("--final", action="store_true")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--model", action="append")
    parser.add_argument("--scenario", action="append")
    parser.add_argument("--variant", action="append")
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-new-invocations", type=int)
    parser.add_argument("--launch-lock", type=Path)
    parser.add_argument("--frozen-root", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def _dispatch(
    args: argparse.Namespace,
    *,
    revision_root: Path | None = None,
    implementation_python: Path | None = None,
    live_runner: Any = None,
    launch_lock_verifier: Any = None,
    frozen_manifest_verifier: Any = None,
) -> dict[str, Any]:
    phase = "pilot" if args.pilot else "final"
    configuration = load_phase_configuration(args.config, phase)
    if args.repetitions is not None and args.repetitions != configuration.repetitions:
        raise ValueError("--repetitions must equal the locked matrix value")
    if args.seed is not None and args.seed != configuration.base_seed:
        raise ValueError("--seed must equal the locked matrix value")
    selectors = {
        "model_ids": tuple(args.model) if args.model else None,
        "scenario_ids": tuple(args.scenario) if args.scenario else None,
        "variant_ids": tuple(args.variant) if args.variant else None,
    }
    if phase == "final" and any(selectors.values()) and not args.resume:
        raise ValueError("final selectors are permitted only with --resume")
    if args.dry_run:
        return dry_run(
            config_root=args.config,
            phase=phase,
            output_root=args.output,
            **selectors,
        )
    if args.output is None:
        raise ValueError("--output is required for live execution")
    resolved_revision = revision_root or Path(__file__).resolve().parents[3]
    if implementation_python is None:
        configured_python = os.environ.get("AUTO_DECTE_IMPLEMENTATION_PYTHON")
        implementation_python = (
            Path(configured_python)
            if configured_python
            else resolved_revision / "source" / "implementation" / ".venv" / "Scripts" / "python.exe"
        )
    if not implementation_python.is_file():
        raise FileNotFoundError(f"implementation Python is unavailable: {implementation_python}")
    if live_runner is None:
        from .phase_runner import run_phase

        live_runner = run_phase
    if args.launch_lock is not None:
        if any(selectors.values()):
            raise ValueError("launch-lock execution requires the complete locked plan")
        if launch_lock_verifier is None:
            from .launch_lock import verify_launch_lock

            launch_lock_verifier = verify_launch_lock
        launch_lock_verifier(
            args.launch_lock,
            config_root=args.config,
            output_root=args.output,
            revision_root=resolved_revision,
            benchmark_root=Path(__file__).resolve().parents[1],
            phase=phase,
            resume=args.resume,
            max_new_invocations=args.max_new_invocations,
            dry_run_summary=dry_run(config_root=args.config, phase=phase),
        )
    if phase == "final":
        if args.frozen_root is None:
            raise ValueError("--frozen-root is required for live Final execution")
        if args.frozen_root.resolve() != resolved_revision.resolve():
            raise ValueError("--frozen-root must be the active frozen revision root")
        if frozen_manifest_verifier is None:
            from .freeze import verify_frozen_manifest

            frozen_manifest_verifier = verify_frozen_manifest
        failures = frozen_manifest_verifier(args.frozen_root)
        if failures:
            raise ValueError(f"frozen manifest verification failed before Final: {failures}")
    result = live_runner(
        config_root=args.config,
        output_root=args.output,
        phase=phase,
        revision_root=resolved_revision,
        implementation_python=implementation_python,
        resume=args.resume,
        max_new_invocations=args.max_new_invocations,
        **selectors,
    )
    if phase == "final":
        failures = frozen_manifest_verifier(args.frozen_root)
        if failures:
            raise ValueError(f"frozen manifest verification failed after Final: {failures}")
    return result


def main() -> int:
    args = _parser().parse_args()
    print(json.dumps(_dispatch(args), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
