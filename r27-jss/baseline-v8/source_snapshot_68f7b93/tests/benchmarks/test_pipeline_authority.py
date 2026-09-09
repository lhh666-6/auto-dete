"""Red tests for the pipeline authority integration benchmark."""

import json
from pathlib import Path

from benchmarks.pipeline_authority_benchmark import (
    FIXED_CLOCK,
    METRIC_KEYS,
    run_pipeline_benchmark,
)


def _run(output: Path) -> dict[str, object]:
    return run_pipeline_benchmark(output, now=FIXED_CLOCK, seed=20260817)


def test_runner_output_schema(tmp_path: Path) -> None:
    summary = _run(tmp_path / "run")
    metrics = summary["metrics"]
    assert set(metrics) == set(METRIC_KEYS)
    for key in METRIC_KEYS:
        if "rate" in key or "coverage" in key:
            assert 0.0 <= metrics[key] <= 1.0
    assert metrics["automatic_completion_rate"] == 0.0
    assert metrics["review_burden"] == 1.0
    assert metrics["silent_fault_escape_rate"] >= 0.0


def test_runner_is_deterministic_with_fixed_clock(tmp_path: Path) -> None:
    first = _run(tmp_path / "a")
    second = _run(tmp_path / "b")
    assert first == second


def test_runner_trace_verified_via_real_queries(tmp_path: Path) -> None:
    summary = _run(tmp_path / "run")
    metrics = summary["metrics"]
    # the two injected corruptions (tampered producer, deleted transition)
    # must be detected by the real trace path
    assert metrics["corruption_detection_rate"] == 1.0
    assert metrics["invalid_transition_rejection_rate"] == 1.0
    assert metrics["valid_certificate_coverage"] == 1.0
    assert metrics["stale_transition_containment"] == 1.0
    assert summary["trace_statuses"].count("incomplete") == 3
    assert summary["trace_statuses"].count("complete") == metrics["cases"]
    # rejection/coverage/detection metrics are counted, never constants
    assert "invalid_transition_rejection_rate" in metrics
    assert "corruption_detection_rate" in metrics


def test_manifest_fields(tmp_path: Path) -> None:
    output = tmp_path / "run"
    _run(output)
    manifest_path = output / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["clean_before_run"] in (True, False)
    assert isinstance(manifest["git_status_porcelain"], str)
    assert isinstance(manifest["ignored_untracked_paths"], list)
    assert len(manifest["source_commit"]) == 40
    assert manifest["seeds"] == [20260817]
    assert manifest["started_utc"] == manifest["ended_utc"] == FIXED_CLOCK.isoformat()
    artifact_names = {item["path"] for item in manifest["artifacts"]}
    assert "pipeline_authority.json" in artifact_names
    assert "manifest.json" not in artifact_names
    for item in manifest["artifacts"]:
        assert len(item["sha256"]) == 64
