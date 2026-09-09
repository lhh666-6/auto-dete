"""Stage paper-facing inputs only from a complete, verified Final benchmark."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
from typing import Any, Mapping

from .manifest import build_manifest, verify_manifest
from .scenarios import scenario_registry


_COPIES = {
    "normalized/runs.json": "normalized/agent_authority_benchmark_runs.json",
    "normalized/runs.csv": "normalized/agent_authority_benchmark_runs.csv",
    "normalized/summary.json": "normalized/agent_authority_benchmark_summary.json",
    "normalized/paper-reporting/statistical_analysis.json": "statistical_analysis.json",
    "normalized/paper-reporting/agent_behavior_table.tex": "tables/agent_behavior_table.tex",
    "normalized/paper-reporting/admission_mechanism_table.tex": (
        "tables/admission_mechanism_table.tex"
    ),
    "normalized/paper-reporting/behavior_vs_authority.svg": (
        "figures/behavior_vs_authority.svg"
    ),
    "normalized/paper-reporting/behavior_vs_authority.pdf": (
        "figures/behavior_vs_authority.pdf"
    ),
    "normalized/paper-reporting/behavior_vs_authority.png": (
        "figures/behavior_vs_authority.png"
    ),
    "normalized/paper-reporting/FIGURE_QA.md": "figures/FIGURE_QA.md",
    "FINAL_REPORT.md": "FINAL_REPORT.md",
}


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _validate_complete_final(final_root: Path) -> dict[str, Any]:
    manifest_path = final_root / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Final manifest is missing: {manifest_path}")
    manifest_failures = verify_manifest(final_root, manifest_path)
    if manifest_failures:
        raise ValueError(f"Final manifest verification failed: {manifest_failures}")
    missing = [relative for relative in _COPIES if not (final_root / relative).is_file()]
    required_config = (
        final_root / "frozen-config/final.matrix.json",
        final_root / "frozen-config/final.models.json",
    )
    missing.extend(path.relative_to(final_root).as_posix() for path in required_config if not path.is_file())
    if missing:
        raise FileNotFoundError(f"Final paper-input source is missing: {sorted(missing)}")

    matrix = _read_object(required_config[0])
    models = _read_object(required_config[1])
    summary = _read_object(final_root / "normalized/summary.json")
    statistics = _read_object(
        final_root / "normalized/paper-reporting/statistical_analysis.json"
    )
    rows = json.loads((final_root / "normalized/runs.json").read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("Final normalized runs must be a JSON array of objects")

    expected_scenarios = tuple(scenario.scenario_id for scenario in scenario_registry())
    scenario_ids = tuple(str(value) for value in matrix.get("scenario_ids", []))
    variant_ids = tuple(str(value) for value in matrix.get("prompt_variant_ids", []))
    repetitions = int(matrix.get("repetitions", 0))
    model_rows = models.get("models", [])
    if not isinstance(model_rows, list) or not all(isinstance(row, dict) for row in model_rows):
        raise ValueError("Final model roster is malformed")
    model_ids = tuple(str(row.get("model_config_id", "")) for row in model_rows)
    providers = {str(row.get("provider", "")) for row in model_rows}
    planned = len(model_ids) * len(scenario_ids) * len(variant_ids) * repetitions
    if (
        matrix.get("schema_version") != "agent-authority-matrix.v2"
        or matrix.get("phase") != "final"
        or matrix.get("citable") is not True
        or scenario_ids != expected_scenarios
        or variant_ids != ("V1", "V2", "V3")
        or repetitions not in {5, 10}
        or len(model_ids) != len(set(model_ids))
        or not {"openai", "deepseek"}.issubset(providers)
        or planned != int(matrix.get("planned_executions", -1))
    ):
        raise ValueError("Final frozen matrix is not the approved complete citable design")

    expected_coordinates = {
        (model_id, scenario_id, variant_id, repetition)
        for model_id in model_ids
        for scenario_id in scenario_ids
        for variant_id in variant_ids
        for repetition in range(1, repetitions + 1)
    }
    actual_coordinates = {
        (
            str(row.get("model_config_id", "")),
            str(row.get("scenario_id", "")),
            str(row.get("prompt_variant_id", "")),
            int(row.get("repetition", 0)),
        )
        for row in rows
    }
    run_ids = [str(row.get("run_id", "")) for row in rows]
    if (
        len(rows) != planned
        or len(set(run_ids)) != planned
        or actual_coordinates != expected_coordinates
        or any(row.get("phase") != "final" for row in rows)
    ):
        raise ValueError("Final normalized ledger does not exactly cover the frozen matrix")
    if (
        summary.get("schema_version") != "agent-authority-summary.v2"
        or int(summary.get("planned_executions", -1)) != planned
        or statistics.get("schema_version") != "agent-authority-statistical-analysis.v2"
    ):
        raise ValueError("Final normalized summary or statistics is inconsistent")
    return {
        "schema_version": "agent-authority-manuscript-input-status.v2",
        "status": "READY_FOR_MANUSCRIPT_INTEGRATION",
        "final_manifest_sha256": _digest(manifest_path),
        "planned_executions": planned,
        "qualified_model_config_ids": list(model_ids),
        "qualified_provider_families": sorted(providers),
        "scenario_ids": list(scenario_ids),
        "prompt_variant_ids": list(variant_ids),
        "repetitions": repetitions,
    }


def stage_manuscript_bundle(*, final_root: Path, output_root: Path) -> dict[str, Any]:
    """Create one no-overwrite paper-input bundle without editing the manuscript."""
    if output_root.exists():
        raise FileExistsError(output_root)
    status = _validate_complete_final(final_root)
    output_root.mkdir(parents=True)
    try:
        for source_relative, destination_relative in _COPIES.items():
            destination = output_root / destination_relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(final_root / source_relative, destination)
        _write_json(output_root / "MANUSCRIPT_INPUT_STATUS.json", status)
        manifest_path = output_root / "manifest.json"
        _write_json(manifest_path, build_manifest(output_root, manifest_path=manifest_path))
        failures = verify_manifest(output_root, manifest_path)
        if failures:
            raise RuntimeError(f"new manuscript-input manifest failed verification: {failures}")
        return status
    except BaseException:
        marker = output_root / "STAGING_FAILED.txt"
        if not marker.exists():
            marker.write_text("Manuscript-input staging failed; preserve for diagnosis.\n", encoding="utf-8")
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = stage_manuscript_bundle(final_root=args.final_root, output_root=args.output)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
