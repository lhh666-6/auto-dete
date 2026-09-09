"""Fail-closed transition from a complete Pilot to the pre-result resource gate."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
from typing import Any, Mapping

from .freeze import build_final_configuration, stage_final_freeze, verify_frozen_manifest
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
    provider_credit_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Write one hash-bound gate decision without reading scientific result fields."""
    if output_path.exists():
        raise FileExistsError(output_path)
    qualification, qualification_rows = _load_complete_pilot(pilot_root)
    provider_credit = _read_object(provider_credit_path)
    policy_path = pilot_root / "frozen-config" / "resource-policy.json"
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


def write_final_config(
    *,
    qualification_path: Path,
    resource_gate_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Create a Final configuration only from the qualification bound by the gate."""
    if output_root.exists():
        raise FileExistsError(output_root)
    qualification = _read_object(qualification_path)
    resource_gate = _read_object(resource_gate_path)
    input_hashes = resource_gate.get("input_sha256", {})
    if input_hashes.get("pilot_qualification") != _digest(qualification_path):
        raise ValueError("resource-gate qualification hash does not match the selected file")
    pilot_root = qualification_path.parent
    manifest_path = pilot_root / "manifest.json"
    if input_hashes.get("pilot_manifest") != _digest(manifest_path):
        raise ValueError("resource-gate Pilot manifest hash does not match the selected Pilot")
    manifest_failures = verify_manifest(pilot_root, manifest_path)
    if manifest_failures:
        raise ValueError(f"Pilot manifest verification failed: {manifest_failures}")
    pilot_config_root = pilot_root / "frozen-config"
    if input_hashes.get("resource_policy") != _digest(
        pilot_config_root / "resource-policy.json"
    ):
        raise ValueError("resource-gate policy hash does not match the frozen Pilot policy")
    receipt = build_final_configuration(
        pilot_config_root=pilot_config_root,
        qualification=qualification,
        resource_gate=resource_gate,
        output_root=output_root,
    )
    receipt["input_sha256"] = {
        "pilot_qualification": _digest(qualification_path),
        "resource_gate": _digest(resource_gate_path),
    }
    shutil.copy2(qualification_path, output_root / "PILOT_MODEL_QUALIFICATION.json")
    shutil.copy2(resource_gate_path, output_root / "FINAL_RESOURCE_GATE.json")
    _write_json_exclusive(output_root / "FINAL_CONFIG_RECEIPT.json", receipt)
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    gate = commands.add_parser("gate")
    gate.add_argument("--pilot-root", type=Path, required=True)
    gate.add_argument("--provider-credit", type=Path, required=True)
    gate.add_argument("--output", type=Path, required=True)
    final_config = commands.add_parser("final-config")
    final_config.add_argument("--qualification", type=Path, required=True)
    final_config.add_argument("--resource-gate", type=Path, required=True)
    final_config.add_argument("--output", type=Path, required=True)
    freeze = commands.add_parser("freeze")
    freeze.add_argument("--benchmark-root", type=Path, required=True)
    freeze.add_argument("--implementation-root", type=Path, required=True)
    freeze.add_argument("--final-config", type=Path, required=True)
    freeze.add_argument("--runtime-metadata", type=Path, required=True)
    freeze.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify-freeze")
    verify.add_argument("--root", type=Path, required=True)
    return parser


def _dispatch(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "gate":
        return write_resource_gate(
            pilot_root=args.pilot_root,
            provider_credit_path=args.provider_credit,
            output_path=args.output,
        )
    if args.command == "final-config":
        return write_final_config(
            qualification_path=args.qualification,
            resource_gate_path=args.resource_gate,
            output_root=args.output,
        )
    if args.command == "freeze":
        return stage_final_freeze(
            benchmark_root=args.benchmark_root,
            implementation_root=args.implementation_root,
            final_config_root=args.final_config,
            output_root=args.output,
            runtime_metadata=_read_object(args.runtime_metadata),
        )
    failures = verify_frozen_manifest(args.root)
    if failures:
        raise ValueError(f"frozen manifest verification failed: {failures}")
    return {
        "schema_version": "agent-authority-frozen-source-verification.v2",
        "status": "PASS",
        "failures": [],
    }


def main() -> int:
    result = _dispatch(_parser().parse_args())
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
