"""Execute the locked R21 live-agent experiment and preserve its evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from auto_decte_live_agent.experiment import (
    build_codex_command,
    evaluate_scenario,
    parse_events,
    prepare_scenario,
    scenario_specs,
    summarize_outcomes,
)
from auto_decte_live_agent.server import BridgeClient, BridgeConfig

EXPERIMENT_SCHEMA = "auto-decte.live-agent-experiment.v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _run_utf8(
    command: list[str],
    *,
    cwd: Path,
    timeout: float,
    stdin: int | None = None,
) -> subprocess.CompletedProcess[str]:
    """Capture subprocess text without depending on the Windows ANSI code page."""
    return subprocess.run(
        command,
        cwd=cwd,
        stdin=stdin,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def probe_database_digest(
    *,
    implementation_python: Path,
    server_source: Path,
    implementation_root: Path,
    database_path: Path,
) -> str:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(server_source.resolve()), str(implementation_root.resolve()))
    )
    completed = subprocess.run(
        [
            str(implementation_python.resolve()),
            "-m",
            "auto_decte_live_agent.state_probe",
            str(database_path.resolve()),
        ],
        cwd=implementation_root,
        env=environment,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"database probe failed: {completed.stderr.strip()}")
    payload = json.loads(completed.stdout)
    digest = payload.get("database_digest")
    if not isinstance(digest, str) or len(digest) != 64:
        raise RuntimeError("database probe returned an invalid digest")
    return digest


def _version(command: list[str], *, cwd: Path) -> str:
    completed = _run_utf8(command, cwd=cwd, timeout=30)
    text = (completed.stdout or completed.stderr).strip()
    return text if completed.returncode == 0 else f"ERROR({completed.returncode}): {text}"


def _primary_fact_version(receipt: dict[str, Any]) -> int:
    forms = receipt.get("forms", [])
    for form in forms if isinstance(forms, list) else []:
        if isinstance(form, dict) and form.get("form_id") == "FORM-DSH-1":
            return int(form["current_record_version"])
    raise RuntimeError("primary fixture form is missing from authority receipt")


def _attempt_host_confirmation(
    spec: Any, prepared: dict[str, Any], bridge: BridgeClient
) -> dict[str, Any] | None:
    if spec.kind not in {"stale_replay", "cross_record", "cross_field"}:
        return None
    operation = "host-confirm" if spec.kind == "stale_replay" else "host-confirm-substitution"
    values: dict[str, object]
    if spec.kind == "stale_replay":
        values = {
            "certificate_id": prepared["stale_certificate_id"],
            "value": 8,
            "expected_version": 0,
            "actor_id": "reviewer-1",
        }
    else:
        values = {
            "certificate_id": prepared["substitution_certificate_id"],
            "target_form_id": prepared["form_id"],
            "target_field_key": prepared["field_key"],
            "value": 8,
            "expected_version": 0,
            "actor_id": "reviewer-1",
        }
    try:
        result = bridge.host(operation, **values)
    except RuntimeError as error:
        return {
            "attempted": True,
            "rejected": True,
            "operation": operation,
            "error": str(error),
        }
    return {
        "attempted": True,
        "rejected": False,
        "operation": operation,
        "result": result,
    }


def run_experiment(
    *,
    output_root: Path,
    revision_root: Path,
    implementation_python: Path,
    model: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    if output_root.exists():
        raise FileExistsError(f"refusing to overwrite experiment output: {output_root}")
    implementation_root = revision_root / "source" / "implementation"
    server_source = revision_root / "source" / "live-agent-experiment"
    codex_text = shutil.which("codex.exe")
    if codex_text is None:
        raise FileNotFoundError("codex.exe was not found on PATH")
    codex = Path(codex_text)
    for required in (implementation_python, implementation_root, server_source, codex):
        if not required.exists():
            raise FileNotFoundError(required)

    source_paths = {
        "experiment.py": server_source / "auto_decte_live_agent" / "experiment.py",
        "runner.py": server_source / "auto_decte_live_agent" / "runner.py",
        "server.py": server_source / "auto_decte_live_agent" / "server.py",
        "state_probe.py": server_source / "auto_decte_live_agent" / "state_probe.py",
        "dsh_bridge.py": implementation_root / "app" / "integrations" / "dsh_bridge.py",
    }
    source_hashes_before = {name: _sha256(path) for name, path in source_paths.items()}

    output_root.mkdir(parents=True)
    workspace = output_root / "agent-workspace"
    workspace.mkdir()
    started_at = _utc_now()
    outcomes: list[dict[str, Any]] = []

    for spec in scenario_specs():
        scenario_root = output_root / "scenarios" / spec.scenario_id
        data_root = scenario_root / "data"
        scenario_root.mkdir(parents=True)
        bridge = BridgeClient(
            BridgeConfig(
                data_root=data_root,
                implementation_root=implementation_root,
                python_executable=implementation_python,
            )
        )
        prepared = prepare_scenario(spec, bridge)
        prompt = spec.prompt_template.format(**prepared)
        (scenario_root / "prompt.txt").write_text(prompt + "\n", encoding="utf-8")
        database_path = data_root / "database" / "demo.db"
        before_digest = probe_database_digest(
            implementation_python=implementation_python,
            server_source=server_source,
            implementation_root=implementation_root,
            database_path=database_path,
        )
        command = build_codex_command(
            codex=codex,
            model=model,
            workspace=workspace,
            server_python=Path(sys.executable),
            server_source=server_source,
            data_root=data_root,
            implementation_root=implementation_root,
            implementation_python=implementation_python,
            prompt=prompt,
        )
        scenario_started_at = _utc_now()
        try:
            completed = _run_utf8(
                command,
                cwd=workspace,
                stdin=subprocess.DEVNULL,
                timeout=timeout_seconds,
            )
            returncode = completed.returncode
            raw_jsonl = completed.stdout or ""
            stderr = completed.stderr or ""
            timed_out = False
        except subprocess.TimeoutExpired as error:
            returncode = -1
            raw_jsonl = error.stdout or ""
            stderr = (error.stderr or "") + f"\nTIMEOUT_AFTER_SECONDS={timeout_seconds}\n"
            timed_out = True
        (scenario_root / "raw.jsonl").write_text(raw_jsonl, encoding="utf-8")
        (scenario_root / "stderr.txt").write_text(stderr, encoding="utf-8")
        parsed = parse_events(raw_jsonl)
        _write_json(scenario_root / "parsed.json", parsed)
        host_confirmation = _attempt_host_confirmation(spec, prepared, bridge)
        if host_confirmation is not None:
            _write_json(scenario_root / "host_confirmation.json", host_confirmation)
        after_digest = probe_database_digest(
            implementation_python=implementation_python,
            server_source=server_source,
            implementation_root=implementation_root,
            database_path=database_path,
        )
        authority_receipt = bridge.host("export-receipt")
        _write_json(scenario_root / "authority_receipt.json", authority_receipt)
        outcome = evaluate_scenario(
            spec,
            parsed,
            before_digest=before_digest,
            after_digest=after_digest,
            post_fact_version=_primary_fact_version(authority_receipt),
            expected_form_id=str(prepared["form_id"]),
            expected_field_key=str(prepared["field_key"]),
            host_confirmation=host_confirmation,
        )
        outcome.update(
            {
                "codex_returncode": returncode,
                "timed_out": timed_out,
                "started_at": scenario_started_at,
                "ended_at": _utc_now(),
            }
        )
        _write_json(scenario_root / "outcome.json", outcome)
        outcomes.append(outcome)

    summary = summarize_outcomes(outcomes)
    source_hashes_after = {name: _sha256(path) for name, path in source_paths.items()}
    sources_unchanged = source_hashes_before == source_hashes_after
    summary["all_passed"] = bool(summary["all_passed"] and sources_unchanged)
    receipt = {
        "schema": EXPERIMENT_SCHEMA,
        "started_at": started_at,
        "ended_at": _utc_now(),
        "model": model,
        "sources_unchanged_during_run": sources_unchanged,
        **summary,
        "scenarios": outcomes,
    }
    _write_json(output_root / "receipt.json", receipt)
    metadata = {
        "schema": EXPERIMENT_SCHEMA,
        "codex_version": _version([str(codex), "--version"], cwd=workspace),
        "codex_path": str(codex.resolve()),
        "requested_model": model,
        "model_reasoning_effort": "low",
        "approval_policy": "never",
        "mcp_default_tools_approval_mode": "approve",
        "enabled_tools": ["auto_decte_propose", "auto_decte_verify"],
        "sandbox": "read-only",
        "host_python": sys.version,
        "implementation_python_version": _version(
            [str(implementation_python.resolve()), "--version"], cwd=implementation_root
        ),
        "platform": platform.platform(),
        "source_hashes_before": source_hashes_before,
        "source_hashes_after": source_hashes_after,
        "sources_unchanged_during_run": sources_unchanged,
        "started_at": started_at,
        "ended_at": receipt["ended_at"],
    }
    _write_json(output_root / "run_metadata.json", metadata)
    return receipt


def recompute_derived(output_root: Path) -> dict[str, Any]:
    """Rebuild only derived outcomes while preserving the first derivation verbatim."""
    receipt_path = output_root / "receipt.json"
    metadata_path = output_root / "run_metadata.json"
    if not receipt_path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError("completed experiment receipt and metadata are required")
    archive = output_root / "initial-derived"
    if archive.exists():
        raise FileExistsError(f"refusing to overwrite initial derivation archive: {archive}")
    archive.mkdir()
    shutil.copy2(receipt_path, archive / "receipt.json")
    shutil.copy2(metadata_path, archive / "run_metadata.json")
    original_receipt_sha256 = _sha256(receipt_path)
    outcomes: list[dict[str, Any]] = []
    for spec in scenario_specs():
        scenario_root = output_root / "scenarios" / spec.scenario_id
        archived_scenario = archive / "scenarios" / spec.scenario_id
        archived_scenario.mkdir(parents=True)
        outcome_path = scenario_root / "outcome.json"
        parsed_path = scenario_root / "parsed.json"
        shutil.copy2(outcome_path, archived_scenario / "outcome.json")
        shutil.copy2(parsed_path, archived_scenario / "parsed.json")
        old = json.loads(outcome_path.read_text(encoding="utf-8"))
        raw = (scenario_root / "raw.jsonl").read_text(encoding="utf-8")
        parsed = parse_events(raw)
        _write_json(parsed_path, parsed)
        outcome = evaluate_scenario(
            spec,
            parsed,
            before_digest=str(old["before_digest"]),
            after_digest=str(old["after_digest"]),
            post_fact_version=int(old["post_fact_version"]),
        )
        for key in ("codex_returncode", "timed_out", "started_at", "ended_at"):
            outcome[key] = old[key]
        _write_json(outcome_path, outcome)
        outcomes.append(outcome)
    summary = summarize_outcomes(outcomes)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    recomputed_at = _utc_now()
    receipt.update(summary)
    receipt["scenarios"] = outcomes
    receipt["derived_recomputed_at"] = recomputed_at
    receipt["initial_receipt_sha256"] = original_receipt_sha256
    evaluator_path = (
        output_root.parents[3]
        / "source"
        / "live-agent-experiment"
        / "auto_decte_live_agent"
        / "experiment.py"
    )
    evaluator_sha256 = _sha256(evaluator_path)
    receipt["derived_evaluator_sha256"] = evaluator_sha256
    _write_json(receipt_path, receipt)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["derived_recomputation"] = {
        "at": recomputed_at,
        "evaluator_sha256": evaluator_sha256,
        "reason": (
            "Codex failed MCP calls encode error text in result.content while status is failed; "
            "the absent confirmation tool was reported with certificate-confirmation wording"
        ),
        "initial_derived_archive": "initial-derived",
    }
    _write_json(metadata_path, metadata)
    derivation_receipt = {
        "schema": EXPERIMENT_SCHEMA,
        "status": "complete",
        "raw_events_modified": False,
        "authority_receipts_modified": False,
        "initial_receipt_sha256": original_receipt_sha256,
        "evaluator_sha256": evaluator_sha256,
        "recomputed_at": recomputed_at,
        **summary,
    }
    _write_json(output_root / "derivation_receipt.json", derivation_receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--revision-root", type=Path, required=True)
    parser.add_argument("--implementation-python", type=Path, required=True)
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--timeout-seconds", type=float, default=300.0)
    args = parser.parse_args()
    receipt = run_experiment(
        output_root=args.output.resolve(),
        revision_root=args.revision_root.resolve(),
        implementation_python=args.implementation_python.resolve(),
        model=args.model,
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if receipt["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
