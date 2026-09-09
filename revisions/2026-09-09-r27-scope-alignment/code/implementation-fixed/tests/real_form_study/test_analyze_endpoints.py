"""Endpoint-analysis tests against hand-computed dummy expectations.

The dummy fixture (6 forms, 12 fields; 5 confirmatory forms) has known
ground truth computed by hand:

- accuracy 8/10 (F-004 qualified 37!=36, F-005 total 51!=50)
- r_danger 1/3 (F-005 total retained wrong; F-002 total and F-003 qualified
  corrected) -> flagged imprecise/descriptive (<30 wrong values)
- retention 6/9 (F-005 qualified abstained -> not machine-presented)
- completion 1.0 (all confirmatory fields reviewed)
- R2 agreement: 3/4 exact, 3/4 raw, kappa 0.5 (F-002 qualified disagrees)
- sensitivity: ambiguous excluded 8/9; manual-route separate 7/8
- form-level timing mean 84 s, median 90 s
"""

import json
from pathlib import Path

import pytest

from analysis.real_form_study.analyze_endpoints import (
    analyze_study,
    form_clustered_bootstrap,
    primary_endpoints,
    reviewer_agreement,
    sensitivity_analyses,
)
from analysis.real_form_study.build_analysis_dataset import build_analysis_dataset
from tests.real_form_study.dummy_study_data import write_dummy_study_data


def _stub_docs(tmp_path: Path) -> None:
    """The manifest hashes the locked protocol and dictionary; tests stub
    them so the manifest contract can be exercised hermetically."""
    docs = tmp_path / "docs" / "dsh"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "human-review-study-protocol.md").write_text("stub protocol", encoding="utf-8")
    (docs / "human-review-study-data-dictionary.md").write_text("stub dictionary", encoding="utf-8")


def _run(tmp_path: Path, seed: int = 20260817) -> dict[str, object]:
    write_dummy_study_data(tmp_path)
    _stub_docs(tmp_path)
    return analyze_study(tmp_path, tmp_path / "artifacts", tmp_path, bootstrap_seed=seed)


def test_primary_endpoints_hand_computed(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    fields = build_analysis_dataset(tmp_path)
    primary = primary_endpoints(fields)
    assert primary["completion_rate"] == pytest.approx(1.0)
    assert primary["final_factual_accuracy"] == pytest.approx(0.8)
    assert primary["r_danger"] == pytest.approx(1 / 3)
    assert primary["r_danger_numerator"] == 1
    assert primary["r_danger_denominator"] == 3
    assert primary["r_danger_wrong_forms"] == 3
    assert primary["r_danger_imprecise_descriptive"] is True
    assert primary["reviewed_machine_value_retention"] == pytest.approx(6 / 9)
    denominators = primary["denominators"]
    assert denominators["eligible_fields"] == 10
    assert denominators["reviewed_evaluable_fields"] == 10
    assert denominators["machine_presented_fields"] == 9


def test_bootstrap_deterministic_and_bounded(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    fields = build_analysis_dataset(tmp_path)
    first = form_clustered_bootstrap(fields, seed=42)
    second = form_clustered_bootstrap(fields, seed=42)
    assert first == second
    for interval in first.values():
        assert interval["lower"] <= interval["point"] <= interval["upper"]
    accuracy = first["final_factual_accuracy"]
    assert 0.0 <= accuracy["lower"] <= accuracy["upper"] <= 1.0


def test_r2_agreement_hand_computed(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    fields = build_analysis_dataset(tmp_path)
    agreement = reviewer_agreement(fields, tmp_path / "review_decisions.csv")
    assert agreement["shared_fields"] == 4
    assert agreement["forms"] == 2
    assert agreement["exact_final_value_agreement"] == pytest.approx(0.75)
    assert agreement["raw_action_agreement"] == pytest.approx(0.75)
    assert agreement["cohen_kappa_overall"] == pytest.approx(0.5)
    assert agreement["disagreement_count"] == 1
    one_vs_rest = agreement["one_vs_rest"]
    assert set(one_vs_rest) == {
        "retain_machine",
        "correct_machine",
        "manual_entry",
        "abstain_reacquire",
    }


def test_sensitivity_analyses_hand_computed(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    fields = build_analysis_dataset(tmp_path)
    sensitivity = sensitivity_analyses(fields)
    assert sensitivity["ambiguous_fields"] == 1
    assert sensitivity["unresolved_fields"] == 1
    assert sensitivity["ambiguous_excluded"] == pytest.approx(8 / 9)
    assert sensitivity["ambiguous_counted_unresolved"] == pytest.approx(0.8)
    assert sensitivity["manual_route_fields"] == 2
    assert sensitivity["manual_route_separate"] == pytest.approx(7 / 8)
    assert sensitivity["form_weighted_accuracy"] == pytest.approx(0.8)


def test_secondary_endpoints_hand_computed(tmp_path: Path) -> None:
    results = _run(tmp_path)
    secondary = results["secondary"]
    assert secondary["machine_candidate_exact_match_accuracy"] == pytest.approx(6 / 9)
    assert secondary["machine_abstention_rate"] == pytest.approx(0.1)
    assert secondary["correction_burden"] == pytest.approx(3 / 9)
    assert secondary["manual_entry_burden"] == pytest.approx(0.1)
    assert secondary["unnecessary_change_rate"] == pytest.approx(1 / 3)
    assert secondary["form_level_exact_accuracy"] == pytest.approx(0.6)
    assert secondary["trace_completeness_among_reviewed"] == pytest.approx(0.8)
    assert secondary["certificate_coverage_among_confirmed"] == pytest.approx(0.9)
    timing = secondary["form_level_timing_seconds"]
    assert timing is not None
    assert timing["mean_seconds"] == pytest.approx(84.0)
    assert timing["median_seconds"] == pytest.approx(90.0)
    assert timing["forms_with_timing"] == 5


def test_analysis_is_deterministic_same_seed(tmp_path: Path) -> None:
    first_dir = tmp_path / "a"
    second_dir = tmp_path / "b"
    write_dummy_study_data(tmp_path / "data")
    _stub_docs(tmp_path)
    analyze_study(tmp_path / "data", first_dir, tmp_path, bootstrap_seed=7)
    analyze_study(tmp_path / "data", second_dir, tmp_path, bootstrap_seed=7)
    first = (first_dir / "endpoint_results.json").read_bytes()
    second = (second_dir / "endpoint_results.json").read_bytes()
    assert first == second


def test_artifacts_and_manifest_contract(tmp_path: Path) -> None:
    results = _run(tmp_path)
    artifacts = tmp_path / "artifacts"
    assert results["primary"] is not None
    for name in (
        "endpoint_results.json",
        "endpoint_tables.csv",
        "figure_data.csv",
        "study_flow.csv",
        "exclusions.csv",
        "protocol_deviations.md",
        "manifest.json",
    ):
        assert (artifacts / name).exists(), name
    manifest = json.loads((artifacts / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    assert len(manifest["locked_protocol_sha256"]) == 64
    assert len(manifest["locked_form_list_sha256"]) == 64
    assert len(manifest["data_dictionary_sha256"]) == 64
    assert manifest["bootstrap_seed"] == 20260817
    assert manifest["bootstrap_resamples"] == 10000
    names = {item["path"] for item in manifest["artifacts"]}
    assert "endpoint_results.json" in names
    assert "manifest.json" not in names
    for item in manifest["artifacts"]:
        assert len(item["sha256"]) == 64
        assert item["bytes"] > 0
