from pathlib import Path

from benchmarks.trust_faults import (
    run_candidate_isolation_ablation,
    run_fault_matrix,
    run_randomized_fault_stress,
)


def test_machine_faults_do_not_change_confirmed_fact(tmp_path: Path) -> None:
    outcomes = run_fault_matrix(tmp_path)
    assert {item.fault for item in outcomes} == {
        "wrong_recognition",
        "wrong_llm_suggestion",
        "irrelevant_retrieval",
        "stale_human_replay",
        "duplicate_evidence",
        "attempted_direct_fact_write",
    }
    assert all(item.fact_unchanged for item in outcomes if item.machine_originated)
    assert all(item.fact_unchanged for item in outcomes)
    assert all(item.audit_complete for item in outcomes)
    direct = next(item for item in outcomes if item.fault == "attempted_direct_fact_write")
    assert direct.attempted_paths == 12
    assert direct.blocked_paths == 12


def test_candidate_isolation_is_necessary_to_prevent_machine_fact_transition(
    tmp_path: Path,
) -> None:
    outcome = run_candidate_isolation_ablation(tmp_path)

    assert outcome.isolated_fact_changed is False
    assert outcome.isolation_removed_fact_changed is True
    assert outcome.injected_value == 999


def test_randomized_fault_stress_runs_every_family_per_trial(tmp_path: Path) -> None:
    outcomes = run_randomized_fault_stress(tmp_path, trials_per_family=3, seed=73)

    assert len(outcomes) == 15
    assert {item.family for item in outcomes} == {
        "wrong_recognition",
        "wrong_llm_suggestion",
        "irrelevant_retrieval",
        "stale_human_replay",
        "duplicate_evidence",
    }
    assert all(item.contained for item in outcomes)
