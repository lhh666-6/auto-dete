from __future__ import annotations

from pathlib import Path

from benchmarks.ai_origin_lifecycle import load_ai_candidate, run_ai_origin_lifecycle

R18_ROOT = Path(__file__).resolve().parents[4]
FIXTURE = R18_ROOT / "fixtures" / "ai-origin"


def test_load_ai_candidate_verifies_fixture_and_preserves_raw_values() -> None:
    candidate = load_ai_candidate(FIXTURE)

    assert candidate.record_id == "SYN-AI-2026-001"
    assert candidate.fields == {
        "quantity": 100,
        "batch": "B-AI-17",
        "operator": "OP-AI-3",
    }
    assert candidate.engine == "openai-codex-hosted-session"
    assert candidate.model_version == "not_exposed_by_host"
    assert candidate.fixture_sha256


def test_run_ai_origin_lifecycle_covers_six_declared_contract_paths(tmp_path: Path) -> None:
    result = run_ai_origin_lifecycle(FIXTURE, tmp_path / "run")

    assert result["schema_version"] == 1
    assert result["fixture"]["record_id"] == "SYN-AI-2026-001"
    cases = {case["id"]: case for case in result["cases"]}
    assert set(cases) == {
        "A1_all_accept",
        "A2_singleton_correction",
        "A3_all_correction",
        "A4_mixed_copy_forward",
        "A5_stale_replay",
        "A6_invalid_item_atomic_rejection",
    }
    assert cases["A1_all_accept"]["observed_outcome"] == "accepted"
    assert cases["A2_singleton_correction"]["observed_outcome"] == "corrected"
    assert cases["A3_all_correction"]["observed_outcome"] == "corrected"
    assert cases["A4_mixed_copy_forward"]["observed_outcome"] == "mixed_committed"
    assert cases["A5_stale_replay"]["observed_outcome"] == "rejected_stale"
    assert cases["A6_invalid_item_atomic_rejection"]["observed_outcome"] == "rejected_invalid_item"
    assert (
        cases["A5_stale_replay"]["database_digest_before"]
        == cases["A5_stale_replay"]["database_digest_after"]
    )
    assert (
        cases["A6_invalid_item_atomic_rejection"]["database_digest_before"]
        == cases["A6_invalid_item_atomic_rejection"]["database_digest_after"]
    )
