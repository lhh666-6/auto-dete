"""Fail-closed transition from a complete Pilot to the pre-result resource gate."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from .manifest import verify_manifest
from .resource_gate import decide_resource_gate, load_resource_policy


PILOT_EXECUTIONS = 112


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_json_exclusive(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _load_complete_pilot(pilot_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = pilot_root / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Pilot manifest is missing: {manifest_path}")
    manifest_failures = verify_manifest(pilot_root, manifest_path)
    if manifest_failures:
        raise ValueError(f"Pilot manifest verification failed: {manifest_failures}")
    required = (
        pilot_root / "PILOT_REPORT.md",
        pilot_root / "pilot-model-qualification.json",
        pilot_root / "normalized/runs.json",
        pilot_root / "normalized/summary.json",
    )
    missing = [path.as_posix() for path in required if not path.is_file()]
    if missing:
        raise ValueError(f"Pilot is incomplete: {missing}")
    summary = _read_object(pilot_root / "normalized/summary.json")
    rows = json.loads((pilot_root / "normalized/runs.json").read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("Pilot normalized ledger must be a JSON array of objects")
    run_ids = [str(row.get("run_id", "")) for row in rows]
    if (
        summary.get("schema_version") != "agent-authority-summary.v2"
        or int(summary.get("planned_executions", -1)) != PILOT_EXECUTIONS
        or len(rows) != PILOT_EXECUTIONS
        or len(set(run_ids)) != PILOT_EXECUTIONS
        or any(row.get("phase") != "pilot" for row in rows)
    ):
        raise ValueError("Pilot normalized ledger does not cover the exact 112-run plan")
    qualification = _read_object(pilot_root / "pilot-model-qualification.json")
    if qualification.get("schema_version") != "agent-authority-model-qualification.v2":
        raise ValueError("Pilot qualification schema is unsupported")
    qualification_rows = qualification.get("models")
    if not isinstance(qualification_rows, list) or not all(
        isinstance(row, dict) for row in qualification_rows
    ):
        raise ValueError("Pilot qualification roster is malformed")
    qualification_ids = [str(row.get("model_config_id", "")) for row in qualification_rows]
    ledger_ids = {str(row.get("model_config_id", "")) for row in rows}
    if len(qualification_ids) != 4 or len(set(qualification_ids)) != 4:
        raise ValueError("Pilot qualification roster must contain four unique attempted slots")
    if set(qualification_ids) != ledger_ids:
        raise ValueError("Pilot qualification roster differs from the normalized ledger")
    return qualification, qualification_rows


def _resource_rows(
    qualification_rows: list[dict[str, Any]],
    provider_credit: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    if provider_credit.get("schema_version") != "agent-authority-provider-credit.v2":
        raise ValueError("provider-credit schema is unsupported")
    attestations = provider_credit.get("model_configurations")
    if not isinstance(attestations, dict):
        raise ValueError("provider-credit model roster is malformed")
    attempted_ids = {str(row["model_config_id"]) for row in qualification_rows}
    if set(map(str, attestations)) != attempted_ids:
        raise ValueError("provider-credit roster differs from the Pilot roster")
    if any(type(value) is not bool for value in attestations.values()):
        raise ValueError("provider-credit values must be booleans")
    resources: dict[str, dict[str, Any]] = {}
    for row in qualification_rows:
        if row.get("qualification_pass") is not True:
            continue
        model_id = str(row["model_config_id"])
        mean_latency_ms = row.get("mean_latency_ms")
        runtime_failure_rate = row.get("runtime_failure_rate")
        if not isinstance(mean_latency_ms, (int, float)) or mean_latency_ms < 0:
            raise ValueError(f"qualified model lacks valid mean latency: {model_id}")
        if not isinstance(runtime_failure_rate, (int, float)) or not 0 <= runtime_failure_rate <= 1:
            raise ValueError(f"qualified model lacks valid runtime-failure rate: {model_id}")
        resources[model_id] = {
            "mean_total_latency_seconds": float(mean_latency_ms) / 1000.0,
            "runtime_failure_rate": float(runtime_failure_rate),
            "provider_credit_sufficient": attestations[model_id],
        }
    return resources


def write_resource_gate(
    *,
    pilot_root: Path,
    pilot_config_root: Path,
    provider_credit_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Write one hash-bound gate decision without reading scientific result fields."""
    if output_path.exists():
        raise FileExistsError(output_path)
    qualification, qualification_rows = _load_complete_pilot(pilot_root)
    provider_credit = _read_object(provider_credit_path)
    policy_path = pilot_config_root / "resource-policy.json"
    policy = load_resource_policy(policy_path)
    decision = decide_resource_gate(
        qualification,
        _resource_rows(qualification_rows, provider_credit),
        policy,
    )
    decision["input_sha256"] = {
        "pilot_manifest": _digest(pilot_root / "manifest.json"),
        "pilot_qualification": _digest(pilot_root / "pilot-model-qualification.json"),
        "provider_credit": _digest(provider_credit_path),
        "resource_policy": _digest(policy_path),
    }
    _write_json_exclusive(output_path, decision)
    return decision


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--pilot-config", type=Path, required=True)
    parser.add_argument("--provider-credit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    result = write_resource_gate(
        pilot_root=args.pilot_root,
        pilot_config_root=args.pilot_config,
        provider_credit_path=args.provider_credit,
        output_path=args.output,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
