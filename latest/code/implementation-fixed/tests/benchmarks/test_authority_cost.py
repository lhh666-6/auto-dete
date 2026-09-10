from __future__ import annotations

import json
from pathlib import Path

from benchmarks.authority_cost import run_cost_benchmark


def test_cost_benchmark_small_profile_emits_raw_complete_cells(tmp_path: Path) -> None:
    config = {
        "schema_version": 1,
        "seed": 17,
        "warmups": 1,
        "trials": 2,
        "admission_fields": [1, 2],
        "admission_changed": [1, "all"],
        "trace_fields": [1, 2],
        "trace_versions": [1, 2],
        "trace_records": [1, 2],
        "storage_transitions": [10],
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    output = tmp_path / "output"
    summary = run_cost_benchmark(config_path, output)
    assert summary["status"] == "complete"
    admission = json.loads((output / "raw" / "admission.json").read_text())
    trace = json.loads((output / "raw" / "trace.json").read_text())
    storage = json.loads((output / "raw" / "storage.json").read_text())
    assert admission["observations"]
    assert trace["observations"]
    assert storage["observations"][0]["transitions"] == 10
    assert (output / "paper_inputs" / "cost_summary.json").exists()
