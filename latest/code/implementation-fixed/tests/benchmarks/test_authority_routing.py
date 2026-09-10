"""Benchmark tests for the round-2 authority-contract benchmarks."""

from pathlib import Path

from benchmarks.authority_routing import (
    BUDGETS,
    EVAL_SEEDS,
    INVALID_TRANSITION_FAMILIES,
    WRONG_MODES,
    run_authority_routing,
)

FIXED_CASES = 27
TOTAL_CASES = FIXED_CASES + 200


def test_architecture_safety_uses_unified_case_sets(tmp_path: Path) -> None:
    summary = run_authority_routing(tmp_path)
    by_arch = {row.architecture: row for row in summary["architecture_results"]}
    assert {row.cases for row in by_arch.values()} == {TOTAL_CASES}
    assert by_arch["A"].facts_created == TOTAL_CASES - 2  # abstained scenarios
    assert by_arch["A"].unauthorized_transitions == by_arch["A"].facts_created
    assert by_arch["B"].facts_created == TOTAL_CASES
    assert by_arch["B"].unauthorized_transitions == TOTAL_CASES
    assert by_arch["A"].valid_certificate_coverage == 0.0
    assert by_arch["B"].valid_certificate_coverage == 0.0
    assert by_arch["A"].reverse_trace_completeness == 0.0
    assert by_arch["B"].reverse_trace_completeness == 0.0
    assert by_arch["A"].invalid_transition_rejection_rate == 0.0
    assert by_arch["B"].invalid_transition_rejection_rate == 0.0


def test_architecture_c_measures_contract_without_hardcoding(tmp_path: Path) -> None:
    summary = run_authority_routing(tmp_path)
    by_arch = {row.architecture: row for row in summary["architecture_results"]}
    c = by_arch["C"]
    assert c.unauthorized_transitions == 0
    assert c.reverse_trace_completeness == 1.0
    assert c.stale_transition_containment == 1.0
    assert c.invalid_transition_rejection_rate == 1.0
    assert c.valid_certificate_coverage > 0.9
    assert c.p1_probe_attempts == c.p1_probe_blocked == 11
    # every created C fact carries a real transition id
    c_cases = [row for row in summary["cases"] if row.architecture == "C"]
    assert all(row.transition_id is not None for row in c_cases if row.fact_created)


def test_novelty_gates(tmp_path: Path) -> None:
    summary = run_authority_routing(tmp_path)
    gates = summary["gates"]
    assert gates["N1_enforced"] is True
    assert gates["N2_pass"] is True
    assert set(gates["N2_distinguishable_cases"]) == {"s-06", "s-07", "s-08"}
    assert gates["N4_independent_faults"] >= 49
    assert gates["N4_uncorrelated_mode_present"] is True
    assert gates["c_unauthorized_transitions"] == 0
    assert gates["c_reverse_trace_complete"] is True
    assert gates["c_stale_containment"] is True
    assert gates["calibration_seed"] == 424242
    assert len(gates["evaluation_seeds"]) == len(EVAL_SEEDS)
    n3 = gates["N3"]
    assert n3["verdict"] in {"PASS", "FAIL"}
    assert set(n3["thresholds"]) == {
        "win_rate",
        "never_worse",
        "uncorrelated_delta_floor",
    }
    # reported statistics must be inside [0, 1]
    for key in ("correlated_win_rate_025", "correlated_win_rate_050", "correlated_never_worse_075"):
        assert 0.0 <= n3[key] <= 1.0


def test_all_invalid_families_rejected_with_fact_unchanged(tmp_path: Path) -> None:
    summary = run_authority_routing(tmp_path)
    examples = {example["fault"]: example for example in summary["rejection_examples"]}
    assert set(examples) == set(INVALID_TRANSITION_FAMILIES)
    assert len(INVALID_TRANSITION_FAMILIES) == 17
    assert all(example["fact_unchanged"] for example in examples.values())
    assert all(example["rejection_codes"] for example in examples.values())


def test_fail_closed_probes_rejected(tmp_path: Path) -> None:
    summary = run_authority_routing(tmp_path)
    c_by_case = {row.case_id: row for row in summary["cases"] if row.architecture == "C"}
    expected = {
        "s-22": ("INVALID_CONFIDENCE",),  # confidence NaN
        "s-23": ("INVALID_CONFIDENCE",),  # confidence 2.0
        "s-24": ("EMPTY_CANDIDATE_ID",),
        "s-25": ("EMPTY_TEMPLATE",),
        "s-26": ("EMPTY_TARGET_RECORD",),
        "s-27": ("FUTURE_CREATED_AT",),
    }
    for case_id, codes in expected.items():
        outcome = c_by_case[case_id]
        assert outcome.rejected
        assert set(outcome.rejection_codes) == set(codes)
        assert not outcome.fact_created


def test_producer_neutral_contract(tmp_path: Path) -> None:
    summary = run_authority_routing(tmp_path)
    producers = {
        row.producer_id: row
        for row in summary["producer_summaries"]
        if row.producer_id in {"recognizer-a", "recognizer-b"}
    }
    assert set(producers) == {"recognizer-a", "recognizer-b"}
    # 24 fixed scenarios use recognizer-a (s-09 unknown, s-15/s-16 recognizer-b),
    # plus 100 pool cases each; the 16 producer-a invalid fixed scenarios reject.
    assert producers["recognizer-a"].cases == 124
    assert producers["recognizer-b"].cases == 102
    assert producers["recognizer-a"].rejected == 16
    assert producers["recognizer-b"].rejected == 0
    for producer in producers.values():
        assert producer.allowed + producer.rejected == producer.cases


def test_routing_experiment_structure(tmp_path: Path) -> None:
    summary = run_authority_routing(tmp_path)
    aggregates = {row.mode: row for row in summary["aggregates"]}
    assert set(aggregates) == set(WRONG_MODES)
    assert len(summary["aggregates"]) == len(WRONG_MODES) * len(BUDGETS)
    for aggregate in summary["aggregates"]:
        assert aggregate.seeds == len(EVAL_SEEDS)
        assert 0.0 <= aggregate.win_rate <= 1.0
        assert 0.0 <= aggregate.never_worse_rate <= 1.0
    seed_rows = summary["seed_rows"]
    assert len(seed_rows) == len(WRONG_MODES) * len(EVAL_SEEDS) * len(BUDGETS)
    assert {row.mode for row in seed_rows} == set(WRONG_MODES)


def test_calibration_is_executable_and_disjoint(tmp_path: Path) -> None:
    summary = run_authority_routing(tmp_path)
    selected = summary["calibration_selected"]
    assert selected.confidence_threshold in {0.5, 0.6, 0.7}
    assert selected.weight_uncertainty in {0.3, 0.5, 0.7}
    assert len(summary["calibration_rows"]) == 9
    assert summary["gates"]["calibration_seed"] not in set(EVAL_SEEDS)


def test_benchmark_is_deterministic(tmp_path: Path) -> None:
    first = run_authority_routing(tmp_path / "first")
    second = run_authority_routing(tmp_path / "second")
    assert first["architecture_results"] == second["architecture_results"]
    assert first["aggregates"] == second["aggregates"]
    assert first["seed_rows"] == second["seed_rows"]
    assert first["rejection_examples"] == second["rejection_examples"]
    assert first["gates"] == second["gates"]
