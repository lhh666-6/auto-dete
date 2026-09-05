"""Read-only Pilot launch-lock verification before any provider invocation."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _manifest_path(lock_path: Path, value: object) -> Path:
    relative = Path(str(value))
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("launch lock manifest path must be a safe sibling path")
    return lock_path.parent / relative


def _verify_selected_manifest(
    root: Path,
    manifest_path: Path,
    expected_digest: str,
    *,
    label: str,
) -> tuple[list[str], int]:
    failures: list[str] = []
    if not manifest_path.is_file():
        return [f"{label}_MANIFEST_MISSING"], 0
    if _digest(manifest_path) != expected_digest:
        failures.append(f"{label}_MANIFEST_HASH")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    selections = [str(value) for value in manifest.get("selection", [])]
    expected = {str(item["path"]): item for item in manifest.get("files", [])}
    actual = {
        path.relative_to(root).as_posix(): path
        for pattern in selections
        for path in root.glob(pattern)
        if path.is_file()
    }
    for relative in sorted(set(expected) - set(actual)):
        failures.append(f"{label}_MISSING:{relative}")
    for relative in sorted(set(actual) - set(expected)):
        failures.append(f"{label}_EXTRA:{relative}")
    for relative in sorted(set(expected) & set(actual)):
        item = expected[relative]
        path = actual[relative]
        if path.stat().st_size != int(item["bytes"]) or _digest(path) != item["sha256"]:
            failures.append(f"{label}_HASH_OR_SIZE:{relative}")
    return failures, len(expected)


def verify_launch_lock(
    lock_path: Path,
    *,
    config_root: Path,
    output_root: Path,
    revision_root: Path,
    benchmark_root: Path,
    phase: str,
    resume: bool,
    max_new_invocations: int | None,
    dry_run_summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify every locked execution input without writing or invoking a provider."""
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    if lock.get("schema_version") != "agent-authority-pilot-launch-lock.v2":
        failures.append("LOCK_SCHEMA")
    if phase != "pilot" or lock.get("phase") != "pilot":
        failures.append("PHASE")
    expected_output = (revision_root / str(lock.get("output_root", ""))).resolve()
    if output_root.resolve() != expected_output:
        failures.append("OUTPUT_ROOT")
    if resume and not output_root.is_dir():
        failures.append("RESUME_ROOT_MISSING")
    if not resume and output_root.exists():
        failures.append("FIRST_RUN_ROOT_EXISTS")
    if max_new_invocations != int(lock.get("max_new_invocations_per_command", -1)):
        failures.append("MAX_NEW_INVOCATIONS")
    if max_new_invocations != 1:
        failures.append("QUOTA_SINGLE_INVOCATION")

    config_hashes = lock.get("config_sha256", {})
    if not isinstance(config_hashes, dict):
        failures.append("CONFIG_HASHES")
        config_hashes = {}
    for name, expected in sorted(config_hashes.items()):
        path = config_root / str(name)
        if not path.is_file() or _digest(path) != str(expected):
            failures.append(f"CONFIG:{name}")
    retry_path = config_root / "retry-policy.json"
    if retry_path.is_file():
        try:
            retry_policy = json.loads(retry_path.read_text(encoding="utf-8"))
            retry_value = int(retry_policy.get("max_transport_retry", -1))
        except (json.JSONDecodeError, AttributeError, TypeError, ValueError):
            retry_value = -1
        if retry_value != int(lock.get("max_transport_retry", -2)):
            failures.append("RETRY_POLICY")
    if int(lock.get("max_transport_retry", -1)) != 0:
        failures.append("QUOTA_ZERO_RETRY")

    benchmark_manifest = _manifest_path(lock_path, lock.get("benchmark_source_manifest", ""))
    benchmark_failures, benchmark_count = _verify_selected_manifest(
        benchmark_root,
        benchmark_manifest,
        str(lock.get("benchmark_source_manifest_sha256", "")),
        label="BENCHMARK",
    )
    failures.extend(benchmark_failures)
    implementation_manifest = _manifest_path(
        lock_path, lock.get("implementation_source_manifest", "")
    )
    implementation_failures, implementation_count = _verify_selected_manifest(
        revision_root / "source" / "implementation",
        implementation_manifest,
        str(lock.get("implementation_source_manifest_sha256", "")),
        label="IMPLEMENTATION",
    )
    failures.extend(implementation_failures)

    if dry_run_summary.get("phase") != phase:
        failures.append("DRY_RUN_PHASE")
    if int(dry_run_summary.get("planned_executions", -1)) != int(
        lock.get("planned_executions", -2)
    ):
        failures.append("DRY_RUN_COUNT")
    if dry_run_summary.get("run_plan_sha256") != lock.get("run_plan_sha256"):
        failures.append("DRY_RUN_PLAN_HASH")
    if int(dry_run_summary.get("model_calls", -1)) != 0:
        failures.append("DRY_RUN_MODEL_CALLS")

    if failures:
        raise ValueError(f"launch lock verification failed: {failures}")
    return {
        "schema_version": "agent-authority-launch-lock-verification.v2",
        "status": "PASS",
        "benchmark_files_verified": benchmark_count,
        "implementation_files_verified": implementation_count,
        "config_files_verified": len(config_hashes),
        "planned_executions": int(dry_run_summary["planned_executions"]),
        "model_calls": 0,
    }
