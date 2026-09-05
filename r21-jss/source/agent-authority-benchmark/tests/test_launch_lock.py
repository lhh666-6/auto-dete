from hashlib import sha256
import json
from pathlib import Path

import pytest

def require_verify_launch_lock():
    try:
        from auto_decte_agent_benchmark.launch_lock import verify_launch_lock
    except ModuleNotFoundError:
        verify_launch_lock = None
    assert verify_launch_lock is not None, "launch-lock verifier is missing"
    return verify_launch_lock


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _source_manifest(root: Path, selection: list[str]) -> dict[str, object]:
    paths = sorted({path for pattern in selection for path in root.glob(pattern) if path.is_file()})
    return {
        "schema_version": "agent-authority-selected-source-manifest.v2",
        "selection": selection,
        "files": [
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _digest(path),
            }
            for path in paths
        ],
    }


def locked_fixture(tmp_path: Path) -> dict[str, Path]:
    revision = tmp_path / "revision"
    benchmark = revision / "source/agent-authority-benchmark"
    implementation = revision / "source/implementation"
    config = benchmark / "config"
    preflight = revision / "evidence/preflight"
    (benchmark / "auto_decte_agent_benchmark").mkdir(parents=True)
    (implementation / "app").mkdir(parents=True)
    config.mkdir()
    (benchmark / "auto_decte_agent_benchmark/runner.py").write_text(
        "VALUE = 1\n", encoding="utf-8"
    )
    (benchmark / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
    (benchmark / "uv.lock").write_text("version = 1\n", encoding="utf-8")
    (implementation / "app/domain.py").write_text("VALUE = 2\n", encoding="utf-8")
    (implementation / "pyproject.toml").write_text(
        "[project]\nname='implementation'\n", encoding="utf-8"
    )
    (implementation / "uv.lock").write_text("version = 1\n", encoding="utf-8")
    config_values = {
        "pilot.models.json": {"schema_version": "models"},
        "pilot.matrix.json": {"schema_version": "matrix"},
        "resource-policy.json": {"schema_version": "resource"},
        "retry-policy.json": {"max_transport_retry": 0},
    }
    for name, value in config_values.items():
        _write_json(config / name, value)
    benchmark_manifest = _source_manifest(
        benchmark,
        ["auto_decte_agent_benchmark/**/*.py", "config/*.json", "pyproject.toml", "uv.lock"],
    )
    implementation_manifest = _source_manifest(
        implementation,
        ["app/**/*.py", "pyproject.toml", "uv.lock"],
    )
    benchmark_manifest_path = preflight / "benchmark-source-manifest.json"
    implementation_manifest_path = preflight / "implementation-source-manifest.json"
    _write_json(benchmark_manifest_path, benchmark_manifest)
    _write_json(implementation_manifest_path, implementation_manifest)
    lock = {
        "schema_version": "agent-authority-pilot-launch-lock.v2",
        "phase": "pilot",
        "benchmark_source_manifest": benchmark_manifest_path.name,
        "benchmark_source_manifest_sha256": _digest(benchmark_manifest_path),
        "implementation_source_manifest": implementation_manifest_path.name,
        "implementation_source_manifest_sha256": _digest(implementation_manifest_path),
        "config_sha256": {name: _digest(config / name) for name in config_values},
        "max_new_invocations_per_command": 1,
        "max_transport_retry": 0,
        "output_root": "evidence/pilot/fixture",
        "planned_executions": 112,
        "run_plan_sha256": "a" * 64,
    }
    lock_path = preflight / "PILOT2_LAUNCH_LOCK.json"
    _write_json(lock_path, lock)
    return {
        "revision": revision,
        "benchmark": benchmark,
        "implementation": implementation,
        "config": config,
        "lock": lock_path,
        "output": revision / lock["output_root"],
    }


def dry_run_summary() -> dict[str, object]:
    return {
        "phase": "pilot",
        "planned_executions": 112,
        "run_plan_sha256": "a" * 64,
        "model_calls": 0,
    }


def test_valid_launch_lock_verifies_all_selected_sources_before_first_run(tmp_path) -> None:
    fixture = locked_fixture(tmp_path)
    verify_launch_lock = require_verify_launch_lock()

    result = verify_launch_lock(
        fixture["lock"],
        config_root=fixture["config"],
        output_root=fixture["output"],
        revision_root=fixture["revision"],
        benchmark_root=fixture["benchmark"],
        phase="pilot",
        resume=False,
        max_new_invocations=1,
        dry_run_summary=dry_run_summary(),
    )

    assert result["status"] == "PASS"
    assert result["benchmark_files_verified"] == 7
    assert result["implementation_files_verified"] == 3


@pytest.mark.parametrize("target", ["config", "implementation", "benchmark"])
def test_launch_lock_rejects_source_or_config_drift_before_provider_call(
    tmp_path: Path, target: str
) -> None:
    fixture = locked_fixture(tmp_path)
    verify_launch_lock = require_verify_launch_lock()
    if target == "config":
        path = fixture["config"] / "retry-policy.json"
    elif target == "implementation":
        path = fixture["implementation"] / "app/domain.py"
    else:
        path = fixture["benchmark"] / "auto_decte_agent_benchmark/runner.py"
    path.write_bytes(path.read_bytes() + b"# drift\n")

    with pytest.raises(ValueError, match="launch lock verification failed"):
        verify_launch_lock(
            fixture["lock"],
            config_root=fixture["config"],
            output_root=fixture["output"],
            revision_root=fixture["revision"],
            benchmark_root=fixture["benchmark"],
            phase="pilot",
            resume=False,
            max_new_invocations=1,
            dry_run_summary=dry_run_summary(),
        )


def test_launch_lock_rejects_wrong_output_and_resume_state(tmp_path) -> None:
    fixture = locked_fixture(tmp_path)
    verify_launch_lock = require_verify_launch_lock()

    with pytest.raises(ValueError, match="launch lock verification failed"):
        verify_launch_lock(
            fixture["lock"],
            config_root=fixture["config"],
            output_root=fixture["revision"] / "evidence/pilot/wrong",
            revision_root=fixture["revision"],
            benchmark_root=fixture["benchmark"],
            phase="pilot",
            resume=False,
            max_new_invocations=1,
            dry_run_summary=dry_run_summary(),
        )

    fixture["output"].mkdir(parents=True)
    result = verify_launch_lock(
        fixture["lock"],
        config_root=fixture["config"],
        output_root=fixture["output"],
        revision_root=fixture["revision"],
        benchmark_root=fixture["benchmark"],
        phase="pilot",
        resume=True,
        max_new_invocations=1,
        dry_run_summary=dry_run_summary(),
    )

    assert result["status"] == "PASS"
