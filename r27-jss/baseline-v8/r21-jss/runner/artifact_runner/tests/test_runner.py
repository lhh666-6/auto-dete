from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from artifact_runner.integrity import build_manifest, sha256_file, verify_manifest
from artifact_runner.runner import reproduce_paper, run_group


def test_manifest_detects_tamper_and_does_not_hash_itself(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    build_manifest(tmp_path, manifest)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert "manifest.json" not in payload["files"]
    assert verify_manifest(tmp_path, manifest) == []
    (tmp_path / "a.txt").write_text("tampered", encoding="utf-8")
    assert verify_manifest(tmp_path, manifest) == ["hash:a.txt"]


def test_runner_refuses_existing_output_and_retains_failure(tmp_path: Path) -> None:
    package = tmp_path / "package"
    package.mkdir()
    (package / "source_manifest.json").write_text("{}\n", encoding="utf-8")
    lock = package / "source" / "implementation" / "uv.lock"
    lock.parent.mkdir(parents=True)
    lock.write_text("version = 1\n", encoding="utf-8")
    config = {
        "schema_version": 1,
        "commands": [
            {
                "id": "fails",
                "group": "correctness",
                "cwd": ".",
                "argv": [sys.executable, "-c", "import sys; print('kept'); sys.exit(7)"],
                "timeout_seconds": 30,
            }
        ],
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    output = tmp_path / "run"
    assert run_group(package, config_path, output, "correctness") == 1
    receipt = json.loads((output / "raw" / "fails" / "receipt.json").read_text())
    assert receipt["exit_code"] == 7
    assert "kept" in (output / "raw" / "fails" / "stdout.txt").read_text()
    metadata = json.loads((output / "run_metadata.json").read_text())
    assert metadata["source_manifest_sha256"] == sha256_file(
        package / "source_manifest.json"
    )
    assert metadata["dependency_lock_sha256"] == sha256_file(lock)
    with pytest.raises(FileExistsError):
        run_group(package, config_path, output, "correctness")


def test_runner_redirects_tool_state_outside_frozen_source(tmp_path: Path) -> None:
    package = tmp_path / "package"
    package.mkdir()
    script = (
        "import os; from pathlib import Path; "
        "names=('HYPOTHESIS_STORAGE_DIRECTORY','MPLCONFIGDIR','MYPY_CACHE_DIR',"
        "'RUFF_CACHE_DIR','XDG_CACHE_HOME'); "
        "[Path(os.environ[name]).mkdir(parents=True, exist_ok=True) for name in names]; "
        "print('\\n'.join(os.environ[name] for name in names))"
    )
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "commands": [
                    {
                        "id": "state",
                        "group": "correctness",
                        "cwd": ".",
                        "argv": [sys.executable, "-c", script],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "run"
    assert run_group(package, config_path, output, "correctness") == 0
    state_root = output / "raw" / "state" / "runner-state"
    emitted = (output / "raw" / "state" / "stdout.txt").read_text().splitlines()
    assert len(emitted) == 5
    assert all(Path(value).is_relative_to(state_root) for value in emitted)
    assert list(package.iterdir()) == []


def test_reproduce_paper_reads_only_raw_receipts(tmp_path: Path) -> None:
    raw_root = tmp_path / "raw-run"
    receipt_dir = raw_root / "raw" / "case-a"
    receipt_dir.mkdir(parents=True)
    (receipt_dir / "receipt.json").write_text(
        json.dumps({"command_id": "case-a", "group": "correctness", "exit_code": 0}),
        encoding="utf-8",
    )
    output = tmp_path / "paper"
    reproduce_paper(raw_root, output)
    summary = json.loads((output / "paper_inputs" / "run_summary.json").read_text())
    assert summary["total"] == 1
    assert summary["passed"] == 1
    assert summary["source"] == "raw-receipts-only"


def test_reproduce_paper_accepts_utf8_bom_json_artifacts(tmp_path: Path) -> None:
    raw_root = tmp_path / "raw-run"
    receipt_dir = raw_root / "raw" / "finite-catalogue"
    artifact = receipt_dir / "artifacts" / "summary.json"
    artifact.parent.mkdir(parents=True)
    (receipt_dir / "receipt.json").write_text(
        json.dumps(
            {
                "command_id": "finite-catalogue",
                "group": "correctness",
                "exit_code": 0,
            }
        ),
        encoding="utf-8",
    )
    artifact.write_text(json.dumps({"passed": 35, "failed": 0}), encoding="utf-8-sig")

    output = tmp_path / "paper"
    reproduce_paper(raw_root, output)

    normalized = json.loads(
        (output / "paper_inputs" / "conformance_summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert normalized == {"failed": 0, "passed": 35}


def test_reproduce_paper_aggregates_frozen_correctness_and_performance(
    tmp_path: Path,
) -> None:
    frozen = tmp_path / "frozen"
    correctness = frozen / "correctness" / "raw"
    performance = frozen / "performance" / "raw"
    catalogue = correctness / "finite-catalogue"
    quality = correctness / "python-full-tests"
    cost = performance / "authority-cost"
    catalogue.mkdir(parents=True)
    quality.mkdir(parents=True)
    cost.mkdir(parents=True)
    for root, command_id, group in (
        (catalogue, "finite-catalogue", "correctness"),
        (cost, "authority-cost", "performance"),
        (quality, "python-full-tests", "correctness"),
    ):
        (root / "receipt.json").write_text(
            json.dumps(
                {
                    "command_id": command_id,
                    "group": group,
                    "exit_code": 0,
                    "timed_out": False,
                }
            ),
            encoding="utf-8",
        )
        (root / "stdout.txt").write_text("", encoding="utf-8")
        (root / "stderr.txt").write_text("", encoding="utf-8")
    (quality / "stdout.txt").write_text(
        "353 passed in 222.39s (0:03:42)\n", encoding="utf-8"
    )
    (catalogue / "artifacts").mkdir()
    (catalogue / "artifacts" / "summary.json").write_text(
        json.dumps({"passed": 35, "failed": 0}), encoding="utf-8"
    )
    (cost / "artifacts" / "paper_inputs").mkdir(parents=True)
    (cost / "artifacts" / "paper_inputs" / "cost_summary.json").write_text(
        json.dumps({"admission": [{"fields": 1}]}), encoding="utf-8"
    )
    (cost / "artifacts" / "receipt.json").write_text(
        json.dumps({"status": "complete"}), encoding="utf-8"
    )

    output = tmp_path / "paper"
    reproduce_paper(frozen, output)

    run_summary = json.loads((output / "paper_inputs" / "run_summary.json").read_text())
    assert run_summary["total"] == 3
    assert run_summary["passed"] == 3
    assert json.loads((output / "paper_inputs" / "conformance_summary.json").read_text())[
        "passed"
    ] == 35
    assert json.loads((output / "paper_inputs" / "cost_summary.json").read_text())[
        "admission"
    ] == [{"fields": 1}]
    quality_summary = json.loads(
        (output / "paper_inputs" / "quality_summary.json").read_text()
    )
    assert quality_summary["commands"] == [
        {"command_id": "python-full-tests", "exit_code": 0, "passed_tests": 353}
    ]
    lineage = json.loads((output / "processed" / "lineage.json").read_text())
    assert {item["paper_input"] for item in lineage["artifacts"]} == {
        "paper_inputs/conformance_summary.json",
        "paper_inputs/cost_summary.json",
        "paper_inputs/cost_run_metadata.json",
        "paper_inputs/quality_summary.json",
        "paper_inputs/run_summary.json",
    }
