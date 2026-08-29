"""Append-only phase orchestration from locked plan to normalized artifacts."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Any, Callable, Mapping

from .bridge_client import BridgeClient, BridgeConfig
from .config import load_phase_configuration
from .deepseek_adapter import DeepSeekAdapter, DeepSeekHTTPClient
from .execution import InvocationEnvelope, execute_one, finalize_interrupted_run
from .ledger import PlannedRun
from .manifest import build_manifest, verify_manifest
from .normalization import FAILURE_TERMINAL_CLASSES, normalize_complete_plan, summarize_primary
from .openai_adapter import OpenAICodexAdapter
from .prompts import render_prompt
from .provider_runtime import invoke_deepseek, invoke_openai_codex
from .runner import build_phase_plan
from .schema import BenchmarkPhase, ModelConfiguration, ProviderFamily
from .scenarios import scenario_registry
from .tool_surface import canonical_tool_surface


ProviderInvoker = Callable[
    [ModelConfiguration, str, BridgeClient, Mapping[str, Any]],
    InvocationEnvelope,
]


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_or_verify(path: Path, payload: bytes) -> None:
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"resume artifact differs from regenerated content: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)


def _planned_runs_bytes(plan: tuple[PlannedRun, ...]) -> bytes:
    return (
        "".join(
            json.dumps(run.to_dict(), sort_keys=True, separators=(",", ":")) + "\n"
            for run in plan
        )
    ).encode("utf-8")


def _select_plan(
    plan: tuple[PlannedRun, ...],
    *,
    phase: str,
    model_ids: tuple[str, ...] | None,
    scenario_ids: tuple[str, ...] | None,
    variant_ids: tuple[str, ...] | None,
) -> tuple[PlannedRun, ...]:
    if phase == "final" and any(value is not None for value in (model_ids, scenario_ids, variant_ids)):
        raise ValueError("final selectors are prohibited outside an exact resume")
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


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: json.dumps(value, sort_keys=True, separators=(",", ":"))
                    if isinstance(value, (dict, list))
                    else value
                    for key, value in row.items()
                }
            )


def _csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    import io

    fieldnames = sorted({key for row in rows for key in row})
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                key: json.dumps(value, sort_keys=True, separators=(",", ":"))
                if isinstance(value, (dict, list))
                else value
                for key, value in row.items()
            }
        )
    return buffer.getvalue().encode("utf-8")


def _qualification(rows: list[dict[str, Any]], models: tuple[ModelConfiguration, ...]) -> dict[str, Any]:
    entries = []
    for model in models:
        model_rows = [row for row in rows if row["model_config_id"] == model.model_config_id]
        benign = [row for row in model_rows if row["scenario_id"] == "B1"]
        observed_latencies = [
            int(row["latency_ms"])
            for row in model_rows
            if isinstance(row.get("latency_ms"), (int, float))
        ]
        runtime_failures = sum(
            row["terminal_class"] in FAILURE_TERMINAL_CLASSES for row in model_rows
        )
        benign_pass = bool(benign) and all(row.get("benign_task_completion") is True for row in benign)
        tool_use_pass = bool(benign) and all(bool(row.get("tool_calls")) for row in benign)
        raw_trace_pass = bool(model_rows) and all(bool(row.get("raw_trace_paths")) for row in model_rows)
        qualification_pass = benign_pass and tool_use_pass and raw_trace_pass
        entries.append(
            {
                "model_config_id": model.model_config_id,
                "provider": model.provider.value,
                "requested_model": model.requested_model,
                "qualification_pass": qualification_pass,
                "tool_use_pass": tool_use_pass,
                "raw_trace_pass": raw_trace_pass,
                "tool_schema_pass": True,
                "benign_case_pass": benign_pass,
                "runtime_failure_rate": runtime_failures / len(model_rows) if model_rows else None,
                "mean_latency_ms": (
                    sum(observed_latencies) / len(observed_latencies)
                    if observed_latencies
                    else None
                ),
                "token_usage": [row.get("token_usage", []) for row in model_rows],
                "reason_if_unavailable": None if qualification_pass else "PILOT_QUALIFICATION_FAILED",
            }
        )
    return {"schema_version": "agent-authority-model-qualification.v2", "models": entries}


def _default_provider_invoker(
    *,
    revision_root: Path,
    implementation_python: Path,
    run_root: Path,
    timeout_seconds: float,
) -> ProviderInvoker:
    implementation_root = revision_root / "source" / "implementation"
    benchmark_source = Path(__file__).resolve().parents[1]

    def invoke(
        model: ModelConfiguration,
        prompt: str,
        bridge: BridgeClient,
        _prepared: Mapping[str, Any],
    ) -> InvocationEnvelope:
        if model.provider is ProviderFamily.DEEPSEEK:
            api_key = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
            base_url = os.environ.get("ANTHROPIC_BASE_URL", model.endpoint_origin)
            client = DeepSeekHTTPClient(base_url=base_url, api_key=api_key)
            return invoke_deepseek(
                adapter=DeepSeekAdapter(model),
                request_sender=client.send,
                bridge=bridge,
                prompt=prompt,
                timeout_seconds=timeout_seconds,
            )
        codex_text = shutil.which("codex.exe") or shutil.which("codex")
        if codex_text is None:
            raise FileNotFoundError("Codex executable is unavailable")
        workspace = run_root / "agent-workspace"
        workspace.mkdir(exist_ok=True)
        return invoke_openai_codex(
            adapter=OpenAICodexAdapter(model),
            codex=Path(codex_text),
            workspace=workspace,
            server_python=Path(sys.executable),
            server_source=benchmark_source,
            implementation_root=implementation_root,
            implementation_python=implementation_python,
            data_root=run_root / "data",
            prompt=prompt,
            timeout_seconds=timeout_seconds,
        )

    return invoke


def run_phase(
    *,
    config_root: Path,
    output_root: Path,
    phase: str,
    revision_root: Path,
    implementation_python: Path,
    model_ids: tuple[str, ...] | None = None,
    scenario_ids: tuple[str, ...] | None = None,
    variant_ids: tuple[str, ...] | None = None,
    provider_invoker: ProviderInvoker | None = None,
    timeout_seconds: float = 300.0,
    resume: bool = False,
) -> dict[str, Any]:
    if output_root.exists() and not resume:
        raise FileExistsError(f"refusing to overwrite phase output: {output_root}")
    if resume and not output_root.is_dir():
        raise FileNotFoundError(f"resume output does not exist: {output_root}")
    configuration = load_phase_configuration(config_root, phase)
    full_plan = build_phase_plan(config_root=config_root, phase=phase)
    plan = _select_plan(
        full_plan,
        phase=phase,
        model_ids=model_ids,
        scenario_ids=scenario_ids,
        variant_ids=variant_ids,
    )
    complete_locked_plan = tuple(run.coordinate.run_id for run in plan) == tuple(
        run.coordinate.run_id for run in full_plan
    )
    selected_model_ids = {run.coordinate.model_config_id for run in plan}
    models = tuple(
        model for model in configuration.models if model.model_config_id in selected_model_ids
    )
    models_by_id = {model.model_config_id: model for model in models}
    scenarios_by_id = {scenario.scenario_id: scenario for scenario in scenario_registry()}
    output_root.mkdir(parents=True, exist_ok=resume)
    (output_root / "runs").mkdir(exist_ok=resume)
    (output_root / "setup-templates").mkdir(exist_ok=resume)
    frozen_config = output_root / "frozen-config"
    frozen_config.mkdir(exist_ok=resume)
    for name in (f"{phase}.models.json", f"{phase}.matrix.json", "retry-policy.json"):
        source = config_root / name
        target = frozen_config / name
        if resume:
            if not target.is_file() or target.read_bytes() != source.read_bytes():
                raise ValueError(f"resume configuration mismatch: {name}")
        else:
            shutil.copy2(source, target)
    _write_or_verify(
        frozen_config / "canonical-tool-surface.json",
        _json_bytes(canonical_tool_surface()),
    )
    _write_or_verify(output_root / "planned-runs.jsonl", _planned_runs_bytes(plan))

    manifest_path = output_root / "manifest.json"
    if resume and manifest_path.is_file():
        failures = verify_manifest(output_root, manifest_path)
        if failures:
            raise RuntimeError(f"existing phase manifest failed verification: {failures}")
        return json.loads((output_root / "normalized" / "summary.json").read_text(encoding="utf-8"))

    prepared_by_case: dict[tuple[str, int], tuple[Path, dict[str, Any]]] = {}
    implementation_root = revision_root / "source" / "implementation"
    for run in plan:
        key = (run.coordinate.scenario_id, run.coordinate.case_seed)
        if key in prepared_by_case:
            continue
        template_root = output_root / "setup-templates" / f"{key[0]}-{key[1]}"
        data_root = template_root / "data"
        if template_root.is_dir():
            prepared_path = template_root / "prepared.json"
            if not prepared_path.is_file() or not data_root.is_dir():
                raise RuntimeError(f"incomplete setup template cannot be resumed: {template_root}")
            prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
        else:
            template_root.mkdir()
            bridge = BridgeClient(
                BridgeConfig(data_root, implementation_root, implementation_python, 60.0)
            )
            prepared = bridge.host("prepare-scenario", scenario_id=key[0])
            _write_json(template_root / "prepared.json", prepared)
        prepared_by_case[key] = (data_root, prepared)

    records: list[dict[str, Any]] = []
    for run in plan:
        model = models_by_id[run.coordinate.model_config_id]
        scenario = scenarios_by_id[run.coordinate.scenario_id]
        template_data, prepared = prepared_by_case[
            (run.coordinate.scenario_id, run.coordinate.case_seed)
        ]
        rendered = render_prompt(scenario, run.coordinate.prompt_variant_id, prepared)
        run_root = output_root / "runs" / run.coordinate.run_id
        if (run_root / "run.json").is_file():
            record = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
            if record.get("run_id") != run.coordinate.run_id:
                raise ValueError(f"terminal run identity mismatch: {run_root}")
            records.append(record)
            continue
        if run_root.is_dir():
            records.append(
                finalize_interrupted_run(
                    run=run,
                    model=model,
                    scenario=scenario,
                    run_root=run_root,
                )
            )
            continue
        bridge = BridgeClient(
            BridgeConfig(run_root / "data", implementation_root, implementation_python, 60.0)
        )
        invoker = provider_invoker or _default_provider_invoker(
            revision_root=revision_root,
            implementation_python=implementation_python,
            run_root=run_root,
            timeout_seconds=timeout_seconds,
        )
        records.append(
            execute_one(
                run=run,
                model=model,
                scenario=scenario,
                prepared=prepared,
                prompt_text=rendered.text,
                run_root=run_root,
                bridge=bridge,
                invoke=lambda _attempt, invoker=invoker, model=model, prompt=rendered.text,
                bridge=bridge, prepared=prepared: invoker(model, prompt, bridge, prepared),
                template_data_root=template_data,
            )
        )

    normalized_root = output_root / "normalized"
    normalized_root.mkdir(exist_ok=resume)
    rows = normalize_complete_plan(plan, records, expected_phase=BenchmarkPhase(phase))
    summary = summarize_primary(rows)
    _write_or_verify(normalized_root / "runs.json", _json_bytes(rows))
    _write_or_verify(normalized_root / "summary.json", _json_bytes(summary))
    _write_or_verify(normalized_root / "runs.csv", _csv_bytes(rows))
    if phase == "pilot" and complete_locked_plan:
        qualification = _qualification(rows, models)
        _write_or_verify(
            output_root / "pilot-model-qualification.json", _json_bytes(qualification)
        )
    report_name = (
        "PILOT_REPORT.md"
        if phase == "pilot" and complete_locked_plan
        else "FINAL_REPORT.md"
        if phase == "final" and complete_locked_plan
        else "DIAGNOSTIC_REPORT.md"
    )
    report = (
        "# Agent Authority Benchmark Phase Report\n\n"
        f"Phase: {phase}\n\n"
        f"Run scope: {'complete locked plan' if complete_locked_plan else 'diagnostic subset'}\n\n"
        f"Planned executions: {summary['planned_executions']}\n\n"
        f"Runtime failures: {summary['runtime_failures']}\n\n"
        "Agent-behavior evidence and admission-mechanism evidence are reported separately.\n"
    )
    _write_or_verify(output_root / report_name, report.encode("utf-8"))
    _write_json(manifest_path, build_manifest(output_root, manifest_path=manifest_path))
    failures = verify_manifest(output_root, manifest_path)
    if failures:
        raise RuntimeError(f"new phase manifest failed verification: {failures}")
    return summary
