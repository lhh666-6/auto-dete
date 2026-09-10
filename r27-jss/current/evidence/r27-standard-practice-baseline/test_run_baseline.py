"""Minimal regression test for the ordinary approval/audit-log baseline."""
import json
import tempfile
from pathlib import Path

from run_baseline import run_all


def test_baseline_summary():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "run"
        summary = run_all(out)
        assert summary["cases"] == 9
        assert summary["divergence_from_candidate_bound"] == [
            "equal-value-substitution",
            "paired-reviewed-candidate",
        ]
        assert summary["capabilities_relative_to_candidate_bound"][
            "reviewed_candidate_persisted"] is False
        assert summary["capabilities_relative_to_candidate_bound"][
            "per_field_sources_reconstructable_from_audit"] is True
        assert summary["capabilities_relative_to_candidate_bound"][
            "paired_histories_distinguishable"] is False
        runs = json.loads((out / "runs.json").read_text(encoding="utf-8"))
        by_case = {r["case_id"]: r for r in runs}
        assert by_case["equal-value-substitution"]["observed"]["accepted"] is True
        assert by_case["legal-correction"]["observed"]["accepted"] is True
        assert by_case["paired-reviewed-candidate"]["observed"]["states_equal"] is True


if __name__ == "__main__":
    test_baseline_summary()
    print("baseline regression test: PASS")
