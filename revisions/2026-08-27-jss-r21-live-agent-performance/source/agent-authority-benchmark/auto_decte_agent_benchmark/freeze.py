"""Build the balanced Final configuration after qualification and resource gating."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil
from typing import Any, Mapping

from .manifest import build_manifest, verify_manifest
from .resource_gate import FORBIDDEN_OUTCOME_FIELDS


_EXCLUDED_RUNTIME_NAMES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
    }
)


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def build_final_configuration(
    *,
    pilot_config_root: Path,
    qualification: Mapping[str, Any],
    resource_gate: Mapping[str, Any],
    output_root: Path,
) -> dict[str, Any]:
    """Write one immutable Final config without consulting scientific outcomes."""
    if output_root.exists():
        raise FileExistsError(output_root)
    if resource_gate.get("status") not in {"PASS", "PASS_FALLBACK"}:
        raise ValueError("resource gate must pass before Final configuration")
    if resource_gate.get("scientific_outcomes_read") is not False:
        raise ValueError("scientific outcomes must not enter Final configuration")
    repetitions = int(resource_gate.get("selected_repetitions", 0))
    if repetitions not in {5, 10}:
        raise ValueError("resource gate must select the balanced 5 or 10 repetitions")

    pilot_models = _read_object(pilot_config_root / "pilot.models.json")
    pilot_matrix = _read_object(pilot_config_root / "pilot.matrix.json")
    qualification_rows = {
        str(row["model_config_id"]): row for row in qualification.get("models", [])
    }
    qualified_ids = {
        model_id
        for model_id, row in qualification_rows.items()
        if row.get("qualification_pass") is True
    }
    gate_ids = {str(value) for value in resource_gate.get("qualified_model_config_ids", [])}
    if qualified_ids != gate_ids:
        raise ValueError("qualification and resource gate model sets differ")
    selected_models = [
        model
        for model in pilot_models.get("models", [])
        if str(model.get("model_config_id")) in qualified_ids
    ]
    if {str(model["model_config_id"]) for model in selected_models} != qualified_ids:
        raise ValueError("qualified model is absent from the frozen Pilot roster")
    providers = {str(model["provider"]) for model in selected_models}
    if not {"openai", "deepseek"}.issubset(providers):
        raise ValueError("Final configuration requires both provider families")

    scenario_ids = [str(value) for value in pilot_matrix["scenario_ids"]]
    planned_executions = len(selected_models) * len(scenario_ids) * 3 * repetitions
    if planned_executions != int(resource_gate.get("planned_executions", -1)):
        raise ValueError("resource gate planned execution count is inconsistent")
    final_models = {
        "schema_version": "agent-authority-model-config.v2",
        "qualification_status": "qualified",
        "models": selected_models,
    }
    final_matrix = {
        "schema_version": "agent-authority-matrix.v2",
        "phase": "final",
        "scenario_ids": scenario_ids,
        "prompt_variant_ids": ["V1", "V2", "V3"],
        "repetitions": repetitions,
        "base_seed": int(pilot_matrix["base_seed"]) + 1,
        "planned_executions": planned_executions,
        "citable": True,
    }

    output_root.mkdir(parents=True)
    _write_json(output_root / "final.models.json", final_models)
    _write_json(output_root / "final.matrix.json", final_matrix)
    for name in ("retry-policy.json", "resource-policy.json"):
        shutil.copy2(pilot_config_root / name, output_root / name)
    config_files = sorted(path for path in output_root.iterdir() if path.is_file())
    hashes = {path.name: _hash(path) for path in config_files}
    excluded_ids = [
        str(model["model_config_id"])
        for model in pilot_models.get("models", [])
        if str(model.get("model_config_id")) not in qualified_ids
    ]
    return {
        "schema_version": "agent-authority-final-config-receipt.v2",
        "scientific_outcomes_read": False,
        "selected_model_config_ids": [
            str(model["model_config_id"]) for model in selected_models
        ],
        "excluded_model_config_ids": excluded_ids,
        "selected_repetitions": repetitions,
        "planned_executions": planned_executions,
        "config_files_sha256": hashes,
    }


def _metadata_keys(value: Any) -> set[str]:
    if isinstance(value, Mapping):
        keys = {str(key) for key in value}
        for nested in value.values():
            keys.update(_metadata_keys(nested))
        return keys
    if isinstance(value, (list, tuple)):
        keys: set[str] = set()
        for nested in value:
            keys.update(_metadata_keys(nested))
        return keys
    return set()


def write_frozen_manifest(
    root: Path,
    *,
    runtime_metadata: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind an already staged source/config tree before any Final execution."""
    if not root.is_dir():
        raise FileNotFoundError(root)
    manifest_path = root / "FROZEN.json"
    if manifest_path.exists():
        raise FileExistsError(manifest_path)
    contaminated = FORBIDDEN_OUTCOME_FIELDS.intersection(_metadata_keys(runtime_metadata))
    if contaminated:
        names = ", ".join(sorted(contaminated))
        raise ValueError(f"scientific outcome metadata is prohibited in freeze: {names}")
    manifest = build_manifest(root, manifest_path=manifest_path)
    manifest.update(
        {
            "schema_version": "agent-authority-frozen-source.v2",
            "scientific_outcomes_read": False,
            "runtime_metadata": dict(runtime_metadata),
        }
    )
    _write_json(manifest_path, manifest)
    failures = verify_manifest(root, manifest_path)
    if failures:
        raise RuntimeError(f"new frozen manifest failed verification: {failures}")
    return manifest


def verify_frozen_manifest(root: Path) -> list[str]:
    return verify_manifest(root, root / "FROZEN.json")


def _copy_runtime_tree(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(source)
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if any(part in _EXCLUDED_RUNTIME_NAMES for part in relative.parts):
            continue
        if path.is_file() and path.suffix not in {".pyc", ".pyo"}:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def _copy_required_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def stage_final_freeze(
    *,
    benchmark_root: Path,
    implementation_root: Path,
    final_config_root: Path,
    output_root: Path,
    runtime_metadata: Mapping[str, Any],
) -> dict[str, Any]:
    """Stage the minimal Final runtime tree and bind it before execution."""
    if output_root.exists():
        raise FileExistsError(output_root)
    output_root.mkdir(parents=True)
    benchmark_destination = output_root / "source" / "agent-authority-benchmark"
    implementation_destination = output_root / "source" / "implementation"
    try:
        _copy_runtime_tree(
            benchmark_root / "auto_decte_agent_benchmark",
            benchmark_destination / "auto_decte_agent_benchmark",
        )
        for name in ("pyproject.toml", "uv.lock", "README_REPRODUCE.md"):
            _copy_required_file(benchmark_root / name, benchmark_destination / name)
        _copy_runtime_tree(implementation_root / "app", implementation_destination / "app")
        for name in ("pyproject.toml", "uv.lock"):
            _copy_required_file(implementation_root / name, implementation_destination / name)
        for name in (
            "final.models.json",
            "final.matrix.json",
            "retry-policy.json",
            "resource-policy.json",
        ):
            _copy_required_file(
                final_config_root / name,
                benchmark_destination / "config" / name,
            )
        return write_frozen_manifest(output_root, runtime_metadata=runtime_metadata)
    except BaseException:
        marker = output_root / "FREEZE_FAILED.txt"
        if not marker.exists():
            marker.write_text("Final source freeze staging failed; preserve for diagnosis.\n", encoding="utf-8")
        raise
