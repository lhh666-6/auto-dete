"""Stable command-line interface from frozen source to paper inputs."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from artifact_runner.integrity import build_manifest, sha256_file, verify_manifest


def _new_output(output: Path) -> None:
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)


def _expanded_argv(
    argv: list[str], package_root: Path, output: Path, artifact_output: Path
) -> list[str]:
    substitutions = {
        "{package_root}": str(package_root),
        "{output}": str(output),
        "{artifact_output}": str(artifact_output),
        "{python}": sys.executable,
    }
    return [substitutions.get(item, item) for item in argv]


def run_group(package_root: Path, config_path: Path, output: Path, group: str) -> int:
    _new_output(output)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise ValueError("unsupported runner config schema")
    raw = output / "raw"
    raw.mkdir()
    failures = 0
    for command in config.get("commands", []):
        if command.get("group") != group:
            continue
        command_id = str(command["id"])
        command_root = raw / command_id
        command_root.mkdir()
        artifact_output = command_root / "artifacts"
        runner_state = command_root / "runner-state"
        runner_state.mkdir()
        argv = _expanded_argv(list(command["argv"]), package_root, output, artifact_output)
        cwd = (package_root / str(command["cwd"])).resolve()
        started = time.perf_counter()
        timed_out = False
        try:
            completed = subprocess.run(
                argv,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=int(command.get("timeout_seconds", 3600)),
                check=False,
                env={
                    **os.environ,
                    **{str(key): str(value) for key, value in command.get("env", {}).items()},
                    "PYTHONHASHSEED": "0",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "HYPOTHESIS_STORAGE_DIRECTORY": str(runner_state / "hypothesis"),
                    "MPLCONFIGDIR": str(runner_state / "matplotlib"),
                    "MYPY_CACHE_DIR": str(runner_state / "mypy"),
                    "RUFF_CACHE_DIR": str(runner_state / "ruff"),
                    "XDG_CACHE_HOME": str(runner_state / "xdg"),
                },
            )
            exit_code = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as error:
            exit_code = 124
            timed_out = True
            stdout = error.stdout or ""
            stderr = error.stderr or ""
        duration = time.perf_counter() - started
        (command_root / "stdout.txt").write_text(stdout, encoding="utf-8")
        (command_root / "stderr.txt").write_text(stderr, encoding="utf-8")
        receipt = {
            "schema_version": 1,
            "command_id": command_id,
            "group": group,
            "argv": argv,
            "cwd": str(command["cwd"]),
            "exit_code": exit_code,
            "timed_out": timed_out,
            "duration_seconds": duration,
            "stdout_sha256": sha256_file(command_root / "stdout.txt"),
            "stderr_sha256": sha256_file(command_root / "stderr.txt"),
        }
        (command_root / "receipt.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        failures += int(exit_code != 0)
    metadata = {
        "schema_version": 1,
        "group": group,
        "platform": platform.platform(),
        "python": sys.version,
        "config_sha256": sha256_file(config_path),
        "source_manifest_sha256": sha256_file(package_root / "source_manifest.json")
        if (package_root / "source_manifest.json").is_file()
        else None,
        "dependency_lock_sha256": sha256_file(
            package_root / "source" / "implementation" / "uv.lock"
        )
        if (package_root / "source" / "implementation" / "uv.lock").is_file()
        else None,
        "command_failures": failures,
    }
    (output / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    build_manifest(output, output / "manifest.json")
    return int(failures != 0)


def _raw_group_roots(raw_root: Path) -> list[Path]:
    if (raw_root / "raw").is_dir():
        return [raw_root]
    return [
        candidate
        for candidate in (raw_root / "correctness", raw_root / "performance")
        if (candidate / "raw").is_dir()
    ]


def _copy_json_artifact(
    source: Path,
    raw_root: Path,
    processed: Path,
    paper_inputs: Path,
    output_name: str,
) -> dict[str, object]:
    payload = json.loads(source.read_text(encoding="utf-8-sig"))
    processed_path = processed / output_name
    paper_path = paper_inputs / output_name
    normalized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    processed_path.write_text(normalized, encoding="utf-8")
    shutil.copy2(processed_path, paper_path)
    return {
        "paper_input": f"paper_inputs/{output_name}",
        "source": source.relative_to(raw_root).as_posix(),
        "source_sha256": sha256_file(source),
        "paper_input_sha256": sha256_file(paper_path),
    }


def _write_quality_summary(
    receipts: list[tuple[Path, dict[str, Any]]],
    raw_root: Path,
    processed: Path,
    paper_inputs: Path,
) -> dict[str, object] | None:
    quality_ids = {
        "python-full-tests",
        "python-static",
        "python-types",
        "paper-stateful",
        "paper-rollback-concurrency",
    }
    commands: list[dict[str, object]] = []
    sources: list[dict[str, str]] = []
    for receipt_path, receipt in receipts:
        command_id = str(receipt["command_id"])
        if command_id not in quality_ids:
            continue
        stdout_path = receipt_path.parent / "stdout.txt"
        stdout = stdout_path.read_text(encoding="utf-8") if stdout_path.is_file() else ""
        item: dict[str, object] = {
            "command_id": command_id,
            "exit_code": int(receipt["exit_code"]),
        }
        if match := re.search(r"(\d+) passed(?:,| in)", stdout):
            item["passed_tests"] = int(match.group(1))
        if match := re.search(r"(\d+) failed(?:,| in)", stdout):
            item["failed_tests"] = int(match.group(1))
        if match := re.search(r"Success: no issues found in (\d+) source files", stdout):
            item["typed_source_files"] = int(match.group(1))
        commands.append(item)
        for source in (receipt_path, stdout_path):
            if source.is_file():
                sources.append(
                    {
                        "source": source.relative_to(raw_root).as_posix(),
                        "source_sha256": sha256_file(source),
                    }
                )
    if not commands:
        return None
    payload = {"schema_version": 1, "commands": commands}
    normalized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    processed_path = processed / "quality_summary.json"
    paper_path = paper_inputs / "quality_summary.json"
    processed_path.write_text(normalized, encoding="utf-8")
    shutil.copy2(processed_path, paper_path)
    return {
        "paper_input": "paper_inputs/quality_summary.json",
        "paper_input_sha256": sha256_file(paper_path),
        "sources": sources,
    }


def reproduce_paper(raw_root: Path, output: Path) -> None:
    _new_output(output)
    group_roots = _raw_group_roots(raw_root)
    if not group_roots:
        raise FileNotFoundError(f"no raw command roots under {raw_root}")
    receipts: list[tuple[Path, dict[str, Any]]] = []
    for group_root in group_roots:
        for path in sorted((group_root / "raw").glob("*/receipt.json")):
            receipts.append((path, json.loads(path.read_text(encoding="utf-8"))))
    processed = output / "processed"
    paper_inputs = output / "paper_inputs"
    processed.mkdir()
    paper_inputs.mkdir()
    normalized = [
        {
            "command_id": item["command_id"],
            "group": item["group"],
            "exit_code": item["exit_code"],
            "timed_out": item.get("timed_out", False),
        }
        for _, item in receipts
    ]
    (processed / "normalized_receipts.json").write_text(
        json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = {
        "schema_version": 1,
        "source": "raw-receipts-only",
        "total": len(normalized),
        "passed": sum(item["exit_code"] == 0 for item in normalized),
        "failed": sum(item["exit_code"] != 0 for item in normalized),
        "commands": normalized,
    }
    (paper_inputs / "run_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    artifact_specs = {
        "alloy-batch": [("artifacts/command_results.json", "alloy_results.json")],
        "formal-refinement": [
            ("artifacts/manifest.json", "formal_refinement_summary.json")
        ],
        "finite-catalogue": [("artifacts/summary.json", "conformance_summary.json")],
        "document-lifecycle": [
            ("artifacts/raw/lifecycle.json", "lifecycle_summary.json")
        ],
        "authority-cost": [
            ("artifacts/paper_inputs/cost_summary.json", "cost_summary.json"),
            ("artifacts/receipt.json", "cost_run_metadata.json"),
        ],
    }
    lineage: list[dict[str, object]] = []
    for receipt_path, receipt in receipts:
        command_id = str(receipt["command_id"])
        if receipt["exit_code"] != 0:
            continue
        for relative, output_name in artifact_specs.get(command_id, []):
            source = receipt_path.parent / relative
            if not source.is_file():
                raise FileNotFoundError(f"passed command missing artifact: {source}")
            lineage.append(
                _copy_json_artifact(
                    source, raw_root, processed, paper_inputs, output_name
                )
            )
    quality_lineage = _write_quality_summary(
        receipts, raw_root, processed, paper_inputs
    )
    if quality_lineage is not None:
        lineage.append(quality_lineage)
    for group_root in group_roots:
        metadata = group_root / "run_metadata.json"
        if metadata.is_file():
            group_name = group_root.name if len(group_roots) > 1 else "run"
            lineage.append(
                _copy_json_artifact(
                    metadata,
                    raw_root,
                    processed,
                    paper_inputs,
                    f"{group_name}_environment.json",
                )
            )
    receipt_sources = [
        {
            "source": path.relative_to(raw_root).as_posix(),
            "source_sha256": sha256_file(path),
        }
        for path, _ in receipts
    ]
    lineage.append(
        {
            "paper_input": "paper_inputs/run_summary.json",
            "paper_input_sha256": sha256_file(paper_inputs / "run_summary.json"),
            "sources": receipt_sources,
        }
    )
    (processed / "lineage.json").write_text(
        json.dumps(
            {"schema_version": 1, "artifacts": lineage}, indent=2, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )
    build_manifest(output, output / "manifest.json")


def verify(package_root: Path) -> list[str]:
    failures: list[str] = []
    for relative in ("source_manifest.json",):
        manifest = package_root / relative
        if manifest.exists():
            failures.extend(
                f"{relative}:{item}" for item in verify_manifest(package_root, manifest)
            )
    evidence_manifest = package_root / "evidence" / "frozen" / "manifest.json"
    if evidence_manifest.exists():
        failures.extend(
            f"evidence/frozen/manifest.json:{item}"
            for item in verify_manifest(package_root / "evidence" / "frozen", evidence_manifest)
        )
    if not (package_root / "source_manifest.json").exists():
        failures.append("missing:source_manifest.json")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=("verify", "reproduce-paper", "rerun-correctness", "rerun-performance", "full"),
    )
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--raw-root", type=Path)
    args = parser.parse_args()
    if args.mode == "verify":
        failures = verify(args.package_root)
        for failure in failures:
            print(failure)
        return int(bool(failures))
    if args.output is None:
        parser.error("--output is required for this mode")
    if args.mode == "reproduce-paper":
        reproduce_paper(args.raw_root or args.package_root / "evidence" / "frozen", args.output)
        return 0
    if args.config is None:
        parser.error("--config is required for rerun modes")
    if args.mode in {"rerun-correctness", "rerun-performance"}:
        group = "correctness" if args.mode.endswith("correctness") else "performance"
        return run_group(args.package_root, args.config, args.output, group)
    _new_output(args.output)
    correctness = args.output / "correctness"
    performance = args.output / "performance"
    correctness_code = run_group(args.package_root, args.config, correctness, "correctness")
    performance_code = run_group(args.package_root, args.config, performance, "performance")
    if correctness_code or performance_code:
        return 1
    reproduce_paper(args.output, args.output / "paper")
    build_manifest(args.output, args.output / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
