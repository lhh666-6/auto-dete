"""Executable concrete-to-Alloy refinement checks for the batch contract."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.application.review_forms import (
    AuthorityRejectionError,
    ConcurrentReviewError,
)
from tests.conformance.alloy_projection import (
    AlloyOutcome,
    RejectionProjectionError,
    capture_authority_snapshot,
    project_committed_admission,
    project_rejected_admission,
    run_projection,
)
from tests.conformance.test_g3b_conformance import _env, _record_machine


def _commit_initial(
    tmp_path: Path,
    *,
    candidate_values: dict[str, object],
    committed_values: dict[str, object],
):
    _, repo, reviews, recog, field_ids = _env(tmp_path, list(candidate_values))
    certificates = {
        field: _record_machine(repo, recog, field_ids[field], value)
        for field, value in candidate_values.items()
    }
    reviews.confirm(
        "FORM-1",
        0,
        committed_values,
        "reviewer-1",
        "refinement fixture",
        certificate_ids_by_field={
            field: certificates[field].certificate_id for field in committed_values
        },
        manual_evidence_ids_by_field={},
    )
    return repo, reviews, recog, field_ids


def test_singleton_accept_projects_to_full_batch_relation(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    certificate = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "accepted",
        certificate_ids_by_field={"total_quantity": certificate.certificate_id},
        manual_evidence_ids_by_field={},
    )

    projection = project_committed_admission(
        repo,
        form_id="FORM-1",
        version=1,
        declared_fields=("total_quantity",),
    )

    assert run_projection(projection, tmp_path / "accepted") is AlloyOutcome.SAT
    assert (
        run_projection(
            projection.with_mutation("item_field_binding"),
            tmp_path / "field-mutant",
        )
        is AlloyOutcome.UNSAT
    )


def test_singleton_correction_projects_to_full_batch_relation(
    tmp_path: Path,
) -> None:
    repo, _, _, _ = _commit_initial(
        tmp_path,
        candidate_values={"total_quantity": 7},
        committed_values={"total_quantity": 8},
    )
    projection = project_committed_admission(
        repo,
        form_id="FORM-1",
        version=1,
        declared_fields=("total_quantity",),
    )
    assert run_projection(projection, tmp_path / "alloy") is AlloyOutcome.SAT


def test_initial_multi_field_accept_correction_and_mixed_batches_refine_full(
    tmp_path: Path,
) -> None:
    cases = {
        "all-accept": ({"a": 1, "b": 2}, {"a": 1, "b": 2}),
        "all-correction": ({"a": 1, "b": 2}, {"a": 10, "b": 20}),
        "mixed": ({"a": 1, "b": 2}, {"a": 1, "b": 20}),
    }
    for case, (candidate_values, committed_values) in cases.items():
        case_root = tmp_path / case
        case_root.mkdir()
        repo, _, _, _ = _commit_initial(
            case_root,
            candidate_values=candidate_values,
            committed_values=committed_values,
        )
        projection = project_committed_admission(
            repo,
            form_id="FORM-1",
            version=1,
            declared_fields=("a", "b"),
        )
        assert run_projection(projection, case_root / "alloy") is AlloyOutcome.SAT


def test_delta_admission_preserves_unchanged_source_in_projection(
    tmp_path: Path,
) -> None:
    repo, reviews, recog, field_ids = _commit_initial(
        tmp_path,
        candidate_values={"a": 1, "b": 2},
        committed_values={"a": 1, "b": 2},
    )
    old_b_source = repo.list_record_versions("FORM-1")[-1].fact_sources["b"]
    certificate = _record_machine(repo, recog, field_ids["a"], 3)
    reviews.confirm(
        "FORM-1",
        1,
        {"a": 3},
        "reviewer-1",
        "delta",
        certificate_ids_by_field={"a": certificate.certificate_id},
        manual_evidence_ids_by_field={},
    )
    projection = project_committed_admission(
        repo,
        form_id="FORM-1",
        version=2,
        declared_fields=("a", "b"),
    )
    assert projection.payload["pre"]["fact_sources"]["b"] == old_b_source
    assert projection.payload["post"]["fact_sources"]["b"] == old_b_source
    assert run_projection(projection, tmp_path / "alloy") is AlloyOutcome.SAT


def test_each_persisted_mapping_dimension_is_load_bearing(
    tmp_path: Path,
) -> None:
    repo, _, _, _ = _commit_initial(
        tmp_path,
        candidate_values={"a": 1, "b": 2},
        committed_values={"a": 1, "b": 20},
    )
    projection = project_committed_admission(
        repo,
        form_id="FORM-1",
        version=1,
        declared_fields=("a", "b"),
    )
    mutations = (
        "item_field_binding",
        "evidence_identity_binding",
        "version_binding",
        "freshness_binding",
        "authorization_certificate_binding",
        "principal_binding",
        "authorization_value_binding",
        "transition_bijection",
        "certificate_preexists",
        "evidence_preexists",
        "committed_value_effect",
        "committed_source_effect",
        "transition_field_binding",
        "transition_evidence_binding",
        "transition_version_binding",
        "transition_value_binding",
        "transition_producer_binding",
        "transition_certificate_binding",
        "transition_authorization_binding",
        "initial_snapshot_domain",
    )
    for mutation in mutations:
        outcome = run_projection(
            projection.with_mutation(mutation),
            tmp_path / "mutants" / mutation,
        )
        assert outcome is AlloyOutcome.UNSAT, mutation


def test_stale_rejection_projects_to_zero_write_stutter(tmp_path: Path) -> None:
    repo, reviews, _, _ = _commit_initial(
        tmp_path,
        candidate_values={"a": 1},
        committed_values={"a": 1},
    )
    certificate = repo.list_certificates_for_form("FORM-1")[0]
    before = capture_authority_snapshot(repo, form_id="FORM-1")
    with pytest.raises(ConcurrentReviewError):
        reviews.confirm(
            "FORM-1",
            0,
            {"a": 2},
            "reviewer-2",
            "stale",
            certificate_ids_by_field={"a": certificate.certificate_id},
            manual_evidence_ids_by_field={},
        )
    after = capture_authority_snapshot(repo, form_id="FORM-1")
    projection = project_rejected_admission(
        repo,
        form_id="FORM-1",
        declared_fields=("a",),
        expected_version=0,
        attempted_values={"a": 2},
        certificate_ids_by_field={"a": certificate.certificate_id},
        principal="reviewer-2",
        before=before,
        after=after,
    )
    assert projection.payload["outcome"] == "rejected"
    assert projection.payload["pre"] == projection.payload["post"]
    assert "freshness_binding" in projection.payload["violations"]
    assert run_projection(projection, tmp_path / "stale-alloy") is AlloyOutcome.SAT

    with pytest.raises(RejectionProjectionError):
        project_rejected_admission(
            repo,
            form_id="FORM-1",
            declared_fields=("a",),
            expected_version=0,
            attempted_values={"a": 2},
            certificate_ids_by_field={"a": certificate.certificate_id},
            principal="reviewer-2",
            before=before,
            after=after.with_added_transition("IMPOSSIBLE-WRITE"),
        )


def test_one_invalid_item_rejects_entire_initial_batch_as_stutter(
    tmp_path: Path,
) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["a", "b"])
    cert_a = _record_machine(repo, recog, field_ids["a"], 1)
    cert_b = _record_machine(repo, recog, field_ids["b"], 2)
    before = capture_authority_snapshot(repo, form_id="FORM-1")
    with pytest.raises(AuthorityRejectionError):
        reviews.confirm(
            "FORM-1",
            0,
            {"a": 1, "b": 2},
            "reviewer-1",
            "one invalid item",
            certificate_ids_by_field={
                "a": cert_a.certificate_id,
                "b": cert_a.certificate_id,
            },
            manual_evidence_ids_by_field={},
        )
    after = capture_authority_snapshot(repo, form_id="FORM-1")
    projection = project_rejected_admission(
        repo,
        form_id="FORM-1",
        declared_fields=("a", "b"),
        expected_version=0,
        attempted_values={"a": 1, "b": 2},
        certificate_ids_by_field={
            "a": cert_a.certificate_id,
            "b": cert_a.certificate_id,
        },
        principal="reviewer-1",
        before=before,
        after=after,
    )
    assert projection.payload["pre"] == projection.payload["post"]
    assert "field_binding:b" in projection.payload["violations"]
    assert cert_b.certificate_id in projection.payload["pre"]["certificate_ids"]
    assert run_projection(projection, tmp_path / "invalid-alloy") is AlloyOutcome.SAT
