from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from release_tools.r17_release import (
    compare_correctness_semantics,
    compare_exact_inputs,
    compare_performance_descriptively,
    main,
    verify_declared_manifest,
    verify_manifest,
    write_manifest,
)


def _write_json(root: Path, name: str, value: object) -> None:
    (root / name).write_text(json.dumps(value), encoding="utf-8")


def test_manifest_detects_one_byte_tamper(tmp_path: Path) -> None:
    (tmp_path / "source").mkdir()
    target = tmp_path / "source" / "contract.txt"
    target.write_text("locked\n", encoding="utf-8")
    manifest = tmp_path / "release_manifest.json"

    write_manifest(tmp_path, manifest)
    assert verify_manifest(tmp_path, manifest) == []

    target.write_text("locked!\n", encoding="utf-8")
    assert verify_manifest(tmp_path, manifest) == ["hash:source/contract.txt"]


def test_exact_input_comparison_reports_missing_extra_and_hash(tmp_path: Path) -> None:
    expected = tmp_path / "expected"
    actual = tmp_path / "actual"
    expected.mkdir()
    actual.mkdir()
    (expected / "same.json").write_text("{}\n", encoding="utf-8")
    (actual / "same.json").write_text("{}\n", encoding="utf-8")
    (expected / "changed.json").write_text("{\"v\":1}\n", encoding="utf-8")
    (actual / "changed.json").write_text("{\"v\":2}\n", encoding="utf-8")
    (expected / "missing.json").write_text("{}\n", encoding="utf-8")
    (actual / "extra.json").write_text("{}\n", encoding="utf-8")

    result = compare_exact_inputs(expected, actual)

    assert result["status"] == "FAIL"
    assert result["missing"] == ["missing.json"]
    assert result["extra"] == ["extra.json"]
    assert result["hash_mismatches"] == ["changed.json"]


def test_correctness_semantics_ignore_timing_but_reject_outcome_drift(tmp_path: Path) -> None:
    expected = tmp_path / "expected"
    actual = tmp_path / "actual"
    expected.mkdir()
    actual.mkdir()
    base = [{
        "profile": "S1",
        "command": "P1",
        "class": "regression",
        "expected": "UNSAT",
        "actual": "UNSAT",
        "status": "PASS",
        "model": "model.als",
        "wall_ms": 10,
    }]
    changed_timing = [{**base[0], "wall_ms": 999}]
    _write_json(expected, "alloy_results.json", base)
    _write_json(actual, "alloy_results.json", changed_timing)

    assert compare_correctness_semantics(expected, actual)["status"] == "PASS"

    _write_json(actual, "alloy_results.json", [{**changed_timing[0], "actual": "SAT"}])
    result = compare_correctness_semantics(expected, actual)
    assert result["status"] == "FAIL"
    assert result["mismatches"] == ["alloy_results.json"]


def test_correctness_semantics_project_lifecycle_run_ids_but_keep_values(
    tmp_path: Path,
) -> None:
    expected = tmp_path / "expected"
    actual = tmp_path / "actual"
    expected.mkdir()
    actual.mkdir()
    stable = {
        "schema_version": 1,
        "status": "complete",
        "trace_status": "complete",
        "copy_forward_fields": ["batch", "operator"],
        "correction": {
            "authorized_value": 101,
            "machine_candidate": 100,
            "transition_id": "FORM-LIFE:2:quantity",
        },
        "export_values_equal_final": True,
        "final_values": {"batch": "B-1", "operator": "OP-7", "quantity": 101},
        "initial_values": {"batch": "B-1", "operator": "OP-7", "quantity": 10},
        "input_sha256": hashlib.sha256(b"input").hexdigest(),
        "versions": [1, 2],
    }
    baseline = {
        **stable,
        "correction": {
            **stable["correction"],
            "certificate_id": hashlib.sha256(b"certificate-a").hexdigest(),
        },
        "export_sha256": hashlib.sha256(b"export-a").hexdigest(),
        "input_evidence_locator": json.dumps(
            {
                "form_id": "FORM-LIFE",
                "related_field_id": None,
                "uri": "images/aa/random-a.png",
                "v": 1,
            }
        ),
    }
    rerun = {
        **stable,
        "correction": {
            **stable["correction"],
            "certificate_id": hashlib.sha256(b"certificate-b").hexdigest(),
        },
        "export_sha256": hashlib.sha256(b"export-b").hexdigest(),
        "input_evidence_locator": json.dumps(
            {
                "form_id": "FORM-LIFE",
                "related_field_id": None,
                "uri": "images/bb/random-b.png",
                "v": 1,
            }
        ),
    }
    _write_json(expected, "lifecycle_summary.json", baseline)
    _write_json(actual, "lifecycle_summary.json", rerun)

    assert compare_correctness_semantics(expected, actual)["status"] == "PASS"

    rerun["correction"]["authorized_value"] = 102
    _write_json(actual, "lifecycle_summary.json", rerun)
    result = compare_correctness_semantics(expected, actual)
    assert result["status"] == "FAIL"
    assert result["mismatches"] == ["lifecycle_summary.json"]


def test_performance_comparison_requires_same_grid_and_positive_latencies(
    tmp_path: Path,
) -> None:
    expected = tmp_path / "expected.json"
    actual = tmp_path / "actual.json"
    baseline = {
        "admission": [{
            "fields": 1,
            "changed": 1,
            "trials": 200,
            "full_p50_ms": 2.0,
            "full_p95_ms": 3.0,
            "lower_p50_ms": 1.0,
            "paired_mean_delta_ms": 1.0,
            "paired_mean_delta_95ci_ms": [0.5, 1.5],
        }],
        "trace": [{
            "fields": 1,
            "versions": 1,
            "records": 1,
            "trials": 200,
            "p50_ms": 1.0,
            "p95_ms": 2.0,
        }],
        "storage": [{
            "transitions": 1000,
            "incremental_bytes": 100,
            "full": {"main_bytes": 200},
            "lower": {"main_bytes": 100},
        }],
    }
    rerun = json.loads(json.dumps(baseline))
    rerun["admission"][0]["full_p50_ms"] = 2.5
    expected.write_text(json.dumps(baseline), encoding="utf-8")
    actual.write_text(json.dumps(rerun), encoding="utf-8")

    result = compare_performance_descriptively(expected, actual)
    assert result["status"] == "PASS"
    assert result["grid"] == {"admission": 1, "trace": 1, "storage": 1}

    rerun["trace"][0]["p50_ms"] = 0
    actual.write_text(json.dumps(rerun), encoding="utf-8")
    result = compare_performance_descriptively(expected, actual)
    assert result["status"] == "FAIL"
    assert "nonpositive:trace:p50_ms" in result["failures"]


def test_manifest_refuses_output_inside_covered_tree(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    manifest = tmp_path / "release_manifest.json"
    write_manifest(tmp_path, manifest)

    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert [item["path"] for item in payload["files"]] == ["a.txt"]
    assert payload["schema_version"] == 1
    assert payload["file_count"] == 1
    assert payload["total_bytes"] == 1


def test_manifest_allows_new_reproduction_outputs_only_under_declared_prefix(
    tmp_path: Path,
) -> None:
    frozen = tmp_path / "evidence" / "frozen"
    reproduced = tmp_path / "evidence" / "reproduced"
    frozen.mkdir(parents=True)
    reproduced.mkdir(parents=True)
    (frozen / "locked.json").write_text("{}", encoding="utf-8")
    manifest = tmp_path / "release_manifest.json"

    write_manifest(tmp_path, manifest, exclude_prefixes=("evidence/reproduced",))
    (reproduced / "new.json").write_text("{}", encoding="utf-8")

    assert verify_manifest(tmp_path, manifest) == []
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["excluded_prefixes"] == ["evidence/reproduced"]


def test_manifest_rejects_symlink(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("x", encoding="utf-8")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(source)
    except OSError:
        pytest.skip("symlink creation is unavailable")

    with pytest.raises(ValueError, match="symlink"):
        write_manifest(tmp_path, tmp_path / "release_manifest.json")


def test_cli_writes_machine_readable_verification_report(tmp_path: Path) -> None:
    (tmp_path / "artifact.txt").write_text("locked", encoding="utf-8")
    manifest = tmp_path / "release_manifest.json"
    report = tmp_path.parent / "verify-report.json"
    write_manifest(tmp_path, manifest)

    exit_code = main(
        [
            "verify-manifest",
            "--root",
            str(tmp_path),
            "--manifest",
            str(manifest),
            "--report",
            str(report),
        ]
    )

    assert exit_code == 0
    assert json.loads(report.read_text(encoding="utf-8")) == {
        "failures": [],
        "status": "PASS",
    }


def test_declared_manifest_ignores_r17_additions_but_detects_locked_drift(
    tmp_path: Path,
) -> None:
    locked = tmp_path / "source" / "locked.py"
    locked.parent.mkdir()
    locked.write_text("value = 1\n", encoding="utf-8")
    digest = hashlib.sha256(locked.read_bytes()).hexdigest()
    manifest = tmp_path / "source_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "algorithm": "sha256",
                "files": {
                    "source/locked.py": {
                        "bytes": locked.stat().st_size,
                        "sha256": digest,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "paper").mkdir()
    (tmp_path / "paper" / "main.tex").write_text("paper", encoding="utf-8")

    assert verify_declared_manifest(tmp_path, manifest) == []

    locked.write_text("value = 2\n", encoding="utf-8")
    assert verify_declared_manifest(tmp_path, manifest) == ["hash:source/locked.py"]


def test_cli_verifies_declared_legacy_manifest(tmp_path: Path) -> None:
    locked = tmp_path / "locked.txt"
    locked.write_text("locked", encoding="utf-8")
    manifest = tmp_path / "source_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "files": {
                    "locked.txt": {
                        "bytes": 6,
                        "sha256": hashlib.sha256(locked.read_bytes()).hexdigest(),
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    report = tmp_path.parent / "declared-report.json"

    assert main(
        [
            "verify-declared",
            "--root",
            str(tmp_path),
            "--manifest",
            str(manifest),
            "--report",
            str(report),
        ]
    ) == 0
    assert json.loads(report.read_text(encoding="utf-8"))["status"] == "PASS"
