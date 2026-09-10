import json
from pathlib import Path

from benchmarks.io import write_json
from benchmarks.schema import PredictionRow


def test_json_artifact_is_stable_and_contains_typed_fields(tmp_path: Path) -> None:
    row = PredictionRow(
        case_id="seed-7-digit-3-clean",
        seed=7,
        target="3",
        prediction="3",
        accepted=True,
        score=0.12,
        perturbation="clean",
        severity=0.0,
        latency_ms=1.25,
    )
    target = tmp_path / "predictions.json"
    digest = write_json(target, [row])
    payload = json.loads(target.read_text(encoding="utf-8"))

    assert payload[0]["case_id"] == "seed-7-digit-3-clean"
    assert payload[0]["accepted"] is True
    assert len(digest) == 64
