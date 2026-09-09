from __future__ import annotations

import json
from pathlib import Path

from benchmarks.admission_lifecycle import run_lifecycle


def test_lifecycle_retains_corrected_candidate_and_copy_forward_sources(tmp_path: Path) -> None:
    result = run_lifecycle(tmp_path / "run")
    assert result["status"] == "complete"
    assert result["versions"] == [1, 2]
    assert result["correction"]["machine_candidate"] == 100
    assert result["correction"]["authorized_value"] == 101
    assert result["copy_forward_fields"] == ["batch", "operator"]
    persisted = json.loads((tmp_path / "run" / "raw" / "lifecycle.json").read_text())
    assert persisted == result
