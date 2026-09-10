import json
from pathlib import Path

from benchmarks.run_resilience import run_resilience


def test_resilience_runner_records_all_operational_checks(tmp_path: Path) -> None:
    output = tmp_path / "resilience.json"
    result = run_resilience(output, repetitions=6, warmups=2)
    payload = json.loads(output.read_text(encoding="utf-8"))[0]

    assert all(result.checks.values())
    assert all(payload["checks"].values())
    assert len(payload["latency"]["warm_ms"]) == 6
    assert len(payload["latency"]["cold_ms"]) == 6
