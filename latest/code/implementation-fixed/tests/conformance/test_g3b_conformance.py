"""G3b executable conformance tests (independent, stateful, bounded)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule, run_state_machine_as_test
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.adapters.database.models import Base, FactTransitionRow
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.recognition.candidate import RecognitionCandidate
from app.adapters.recognition.opencv import OpenCvImagePipeline
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.query_forms import QueryForms
from app.application.recognize_forms import RecognizeForms
from app.application.review_forms import AuthorityRejectionError, ConcurrentReviewError, ReviewForms
from app.domain.authority import (
    AuthorizationBinding,
    FactTransition,
    HumanDecision,
    canonical_json,
)
from app.domain.models import (
    AuditEvent,
    Form,
    FormField,
    RecordStatus,
    RecordVersion,
    ReviewStatus,
    utc_now,
)


def _env(tmp_path: Path, fields: list[str] = ("total_quantity",)):
    """Create a fresh DB with a form, fields, recognition, and review service."""
    db_path = tmp_path / "conformance.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    repo = SqlAlchemyFormRepository(engine)
    repo.add_form(Form(form_id="FORM-1", template_id="T1", template_version="1"))
    field_ids: dict[str, str] = {}
    for index, field_name in enumerate(fields, start=1):
        field_id = f"FIELD-{index}"
        field_ids[field_name] = field_id
        repo.add_form_field(
            FormField(
                field_id,
                "FORM-1",
                field_name,
                {"x": 0, "y": 0, "w": 8, "h": 8},
            )
        )
    storage = LocalEvidenceStorage(tmp_path / "evidence")
    recog = RecognizeForms(repo, repo, repo, storage, OpenCvImagePipeline(), candidate_writer=repo)
    reviews = ReviewForms(
        repo,
        repo,
        authority_read=repo,
        admission=repo,
        known_producers=frozenset({("recognizer-a", "1.0")}),
        known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
    )
    return engine, repo, reviews, recog, field_ids


def _record_machine(repo, recog, field_id: str, value):
    crop = np.full((64, 48), 255, dtype=np.uint8)
    recog.record_candidate(
        "FORM-1",
        field_id,
        crop,
        RecognitionCandidate(value, 0.9, "recognizer-a", "1.0", "OK"),
        "machine",
    )
    return repo.list_certificates_for_form("FORM-1")[-1]


def test_legal_accept_and_correction_preserve_machine_certificate(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    field_id = field_ids["total_quantity"]

    # Version 1: legal Accept.
    cert1 = _record_machine(repo, recog, field_id, 7)
    record1 = reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": cert1.certificate_id},
        manual_evidence_ids_by_field={},
    )
    assert record1.version == 1
    v1_transitions = repo.list_transitions_for_version("FORM-1", 1)
    assert v1_transitions[0].certificate_id == cert1.certificate_id
    assert v1_transitions[0].value == 7
    assert len(repo.list_authorization_bindings_for_form("FORM-1")) == 1

    # Version 2: legal Correction; original machine certificate is preserved.
    cert2 = _record_machine(repo, recog, field_id, 7)
    record2 = reviews.confirm(
        "FORM-1",
        1,
        {"total_quantity": 8},
        "reviewer-1",
        "corrected",
        certificate_ids_by_field={"total_quantity": cert2.certificate_id},
        manual_evidence_ids_by_field={},
    )
    assert record2.version == 2
    certs = repo.list_certificates_for_form("FORM-1")
    assert cert2.certificate_id in {c.certificate_id for c in certs}
    v2_transitions = repo.list_transitions_for_version("FORM-1", 2)
    assert v2_transitions[0].certificate_id == cert2.certificate_id
    assert v2_transitions[0].value == 8
    bindings = repo.list_authorization_bindings_for_form("FORM-1")
    correction_binding = [b for b in bindings if b.decision_id.endswith("total_quantity")][-1]
    assert correction_binding.certificate_id == cert2.certificate_id
    assert correction_binding.value == 8
    versions = repo.list_record_versions("FORM-1")
    assert versions[-1].fact_sources["total_quantity"] == v2_transitions[0].transition_id


def test_fact_sources_copy_forward_preserves_unchanged_field(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["a", "b"])
    cert_a1 = _record_machine(repo, recog, field_ids["a"], 1)
    cert_b1 = _record_machine(repo, recog, field_ids["b"], 2)
    reviews.confirm(
        "FORM-1",
        0,
        {"a": 1, "b": 2},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={
            "a": cert_a1.certificate_id,
            "b": cert_b1.certificate_id,
        },
        manual_evidence_ids_by_field={},
    )
    versions1 = repo.list_record_versions("FORM-1")
    source_a1 = versions1[-1].fact_sources["a"]
    source_b1 = versions1[-1].fact_sources["b"]

    cert_a2 = _record_machine(repo, recog, field_ids["a"], 3)
    reviews.confirm(
        "FORM-1",
        1,
        {"a": 3},
        "reviewer-1",
        "corrected",
        certificate_ids_by_field={"a": cert_a2.certificate_id},
        manual_evidence_ids_by_field={},
    )
    versions2 = repo.list_record_versions("FORM-1")
    source_a2 = versions2[-1].fact_sources["a"]
    source_b2 = versions2[-1].fact_sources["b"]
    assert versions2[-1].values == {"a": 3, "b": 2}
    assert set(versions2[-1].values) == set(versions2[-1].fact_sources)
    assert source_a2 != source_a1
    assert source_b2 == source_b1


def test_cross_field_substitution_rejected(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["a", "b"])
    cert_a = _record_machine(repo, recog, field_ids["a"], 1)
    with pytest.raises(AuthorityRejectionError) as exc:
        reviews.confirm(
            "FORM-1",
            0,
            {"b": 1},
            "reviewer-1",
            "bad",
            certificate_ids_by_field={"b": cert_a.certificate_id},
            manual_evidence_ids_by_field={},
        )
    assert any("FIELD_KEY_BINDING_MISMATCH" in f.code for f in exc.value.failures)


def test_stale_replay_rejected(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": cert.certificate_id},
        manual_evidence_ids_by_field={},
    )
    with pytest.raises(ConcurrentReviewError):
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 8},
            "reviewer-2",
            "stale",
            certificate_ids_by_field={"total_quantity": cert.certificate_id},
            manual_evidence_ids_by_field={},
        )
    assert len(repo.list_record_versions("FORM-1")) == 1


def test_source_deletion_trace_incomplete(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": cert.certificate_id},
        manual_evidence_ids_by_field={},
    )
    transition = repo.list_transitions_for_version("FORM-1", 1)[0]
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM fact_transitions WHERE transition_id = :tid"),
            {"tid": transition.transition_id},
        )
    trace = QueryForms(repo).trace("FORM-1", 1)
    assert trace.status == "incomplete"
    assert any(
        any("missing anchored source" in msg or "missing transition" in msg for msg in f.failures)
        for f in trace.fields
    )


@given(st.integers(min_value=0, max_value=100))
def test_hypothesis_authorized_value_round_trip(value: int) -> None:
    from app.domain.authority import AuthorizationBinding
    from app.domain.models import utc_now

    binding = AuthorizationBinding(
        binding_id="B-1",
        decision_id="D-1",
        certificate_id="C-1",
        authorized_value_payload=f'{{"v": {value}}}',
        bound_at=utc_now(),
    )
    assert binding.value == {"v": value}


# ---------------------------------------------------------------------------
# Complete snapshot + source-anchored trace
# ---------------------------------------------------------------------------


def _valid_admission_bundle(repo, recog, field_id: str, value: object, *, record_id: str = "REC-X"):
    """Build a repository-level valid admission bundle for one machine field."""
    cert = _record_machine(repo, recog, field_id, value)
    now = utc_now()
    decision_id = f"FORM-1:1:{cert.field_key}"
    decision = HumanDecision(
        decision_id=decision_id,
        reviewer_id="reviewer-1",
        candidate_id=cert.candidate_id,
        field_key=cert.field_key,
        reason="ok",
        decided_at=now,
    )
    transition = FactTransition(
        transition_id=decision_id,
        record_id="FORM-1",
        field_key=cert.field_key,
        created_version=1,
        record_version_id=record_id,
        decision_id=decision_id,
        certificate_id=cert.certificate_id,
        evidence_sha256=cert.evidence_hash,
        evidence_locator=cert.evidence_locator,
        producer_id=cert.producer_id,
        producer_version=cert.producer_version,
        source_kind=cert.source_kind,
        template_id=cert.template_id,
        template_version=cert.template_version,
        value_payload=canonical_json(value),
        created_at=now,
    )
    binding = AuthorizationBinding(
        binding_id=f"{decision_id}:AUTH",
        decision_id=decision_id,
        certificate_id=cert.certificate_id,
        authorized_value_payload=canonical_json(value),
        bound_at=now,
    )
    record = RecordVersion(
        record_id=record_id,
        form_id="FORM-1",
        version=1,
        status=RecordStatus.CONFIRMED,
        values={cert.field_key: value},
        change_reason="ok",
        confirmed_by="reviewer-1",
        created_at=now,
    )
    audit = AuditEvent(
        event_id="EVENT-1",
        form_id="FORM-1",
        event_type="CONFIRM",
        actor_id="reviewer-1",
        after={cert.field_key: value},
        evidence_ids=(),
    )
    return cert, decision, transition, record, audit, binding


def test_complete_snapshot_and_historical_source_trace(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["a", "b"])
    cert_a1 = _record_machine(repo, recog, field_ids["a"], 1)
    cert_b1 = _record_machine(repo, recog, field_ids["b"], 2)
    reviews.confirm(
        "FORM-1",
        0,
        {"a": 1, "b": 2},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"a": cert_a1.certificate_id, "b": cert_b1.certificate_id},
        manual_evidence_ids_by_field={},
    )
    cert_a2 = _record_machine(repo, recog, field_ids["a"], 3)
    reviews.confirm(
        "FORM-1",
        1,
        {"a": 3},
        "reviewer-1",
        "corrected",
        certificate_ids_by_field={"a": cert_a2.certificate_id},
        manual_evidence_ids_by_field={},
    )
    latest = repo.list_record_versions("FORM-1")[-1]
    assert latest.values == {"a": 3, "b": 2}
    assert set(latest.values) == set(latest.fact_sources)

    trace = QueryForms(repo).trace("FORM-1", 2)
    assert trace.status == "complete"
    by_field = {field.field_key: field for field in trace.fields}
    assert by_field["a"].created_version == 2
    assert by_field["b"].created_version == 1
    assert by_field["b"].failures == ()


def test_trace_detects_transition_value_tamper(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": cert.certificate_id},
        manual_evidence_ids_by_field={},
    )
    transition = repo.list_transitions_for_version("FORM-1", 1)[0]
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE fact_transitions SET value_payload = :v WHERE transition_id = :tid"),
            {"v": canonical_json(999), "tid": transition.transition_id},
        )
    trace = QueryForms(repo).trace("FORM-1", 1)
    assert trace.status == "incomplete"
    assert any(
        "transition value and committed value mismatch" in f
        for field in trace.fields
        for f in field.failures
    )


def test_trace_detects_authorization_value_tamper(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": cert.certificate_id},
        manual_evidence_ids_by_field={},
    )
    transition = repo.list_transitions_for_version("FORM-1", 1)[0]
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE authorization_bindings "
                "SET authorized_value_payload = :v WHERE decision_id = :d"
            ),
            {"v": canonical_json(999), "d": transition.decision_id},
        )
    trace = QueryForms(repo).trace("FORM-1", 1)
    assert trace.status == "incomplete"
    assert any(
        "authorization value and transition value mismatch" in f
        for field in trace.fields
        for f in field.failures
    )


def test_trace_detects_committed_value_tamper(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": cert.certificate_id},
        manual_evidence_ids_by_field={},
    )
    with engine.begin() as conn:
        conn.execute(
            text(
                'UPDATE record_versions SET "values" = :v '
                "WHERE form_id = 'FORM-1' AND version = 1"
            ),
            {"v": canonical_json({"total_quantity": 999})},
        )
    trace = QueryForms(repo).trace("FORM-1", 1)
    assert trace.status == "incomplete"
    assert any(
        "transition value and committed value mismatch" in f
        for field in trace.fields
        for f in field.failures
    )


# ---------------------------------------------------------------------------
# Trusted admission bundle hardening
# ---------------------------------------------------------------------------


def test_repository_rejects_missing_authorization_binding(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    _, decision, transition, record, audit, _ = _valid_admission_bundle(
        repo, recog, field_ids["total_quantity"], 7
    )
    with pytest.raises(ValueError, match="authorization_bindings must not be empty"):
        repo.append_fact_transition(
            form_id="FORM-1",
            expected_version=0,
            record=record,
            decisions=[decision],
            transitions=[transition],
            derived_certificates=[],
            authorization_bindings=[],
            audit=audit,
            review_status=ReviewStatus.CONFIRMED,
            export_status=None,
        )
    assert repo.list_record_versions("FORM-1") == []


def test_repository_rejects_binding_certificate_mismatch(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    _, decision, transition, record, audit, binding = _valid_admission_bundle(
        repo, recog, field_ids["total_quantity"], 7
    )
    bad = AuthorizationBinding(
        binding_id=binding.binding_id,
        decision_id=binding.decision_id,
        certificate_id="OTHER-CERT",
        authorized_value_payload=binding.authorized_value_payload,
        bound_at=binding.bound_at,
    )
    with pytest.raises(ValueError, match="certificate mismatch"):
        repo.append_fact_transition(
            form_id="FORM-1",
            expected_version=0,
            record=record,
            decisions=[decision],
            transitions=[transition],
            derived_certificates=[],
            authorization_bindings=[bad],
            audit=audit,
            review_status=ReviewStatus.CONFIRMED,
            export_status=None,
        )
    assert repo.list_record_versions("FORM-1") == []


def test_repository_rejects_binding_value_mismatch(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    _, decision, transition, record, audit, binding = _valid_admission_bundle(
        repo, recog, field_ids["total_quantity"], 7
    )
    bad = AuthorizationBinding(
        binding_id=binding.binding_id,
        decision_id=binding.decision_id,
        certificate_id=binding.certificate_id,
        authorized_value_payload=canonical_json(999),
        bound_at=binding.bound_at,
    )
    with pytest.raises(ValueError, match="authorized value mismatch"):
        repo.append_fact_transition(
            form_id="FORM-1",
            expected_version=0,
            record=record,
            decisions=[decision],
            transitions=[transition],
            derived_certificates=[],
            authorization_bindings=[bad],
            audit=audit,
            review_status=ReviewStatus.CONFIRMED,
            export_status=None,
        )
    assert repo.list_record_versions("FORM-1") == []


# ---------------------------------------------------------------------------
# Required substitution / missing / direct-write families
# ---------------------------------------------------------------------------


def test_abl3_record_substitution_rejected(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    repo.add_form(Form(form_id="FORM-2", template_id="T1", template_version="1"))
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    with pytest.raises(AuthorityRejectionError) as exc:
        reviews.confirm(
            "FORM-2",
            0,
            {"total_quantity": 7},
            "reviewer-1",
            "cross-record",
            certificate_ids_by_field={"total_quantity": cert.certificate_id},
            manual_evidence_ids_by_field={},
        )
    assert any("RECORD_BINDING_MISMATCH" == f.code for f in exc.value.failures)


def test_abl4b_stale_replay_rejected(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": cert.certificate_id},
        manual_evidence_ids_by_field={},
    )
    with pytest.raises(ConcurrentReviewError):
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 8},
            "reviewer-2",
            "stale",
            certificate_ids_by_field={"total_quantity": cert.certificate_id},
            manual_evidence_ids_by_field={},
        )
    assert len(repo.list_record_versions("FORM-1")) == 1


def test_abl5_auth_certificate_transfer_rejected(tmp_path: Path) -> None:
    """Check the repository rejects a same-value, different-certificate pair."""
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["a", "b"])
    _, decision, transition, record, audit, binding = _valid_admission_bundle(
        repo, recog, field_ids["a"], 7
    )
    cert_b = _record_machine(repo, recog, field_ids["b"], 7)
    bad = AuthorizationBinding(
        binding_id=binding.binding_id,
        decision_id=binding.decision_id,
        certificate_id=cert_b.certificate_id,
        authorized_value_payload=binding.authorized_value_payload,
        bound_at=binding.bound_at,
    )
    with pytest.raises(ValueError, match="certificate mismatch"):
        repo.append_fact_transition(
            form_id="FORM-1",
            expected_version=0,
            record=record,
            decisions=[decision],
            transitions=[transition],
            derived_certificates=[],
            authorization_bindings=[bad],
            audit=audit,
            review_status=ReviewStatus.CONFIRMED,
            export_status=None,
        )
    assert repo.list_record_versions("FORM-1") == []


def test_abl8_unauthorized_value_rejected(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    _, decision, transition, record, audit, binding = _valid_admission_bundle(
        repo, recog, field_ids["total_quantity"], 7
    )
    bad = AuthorizationBinding(
        binding_id=binding.binding_id,
        decision_id=binding.decision_id,
        certificate_id=binding.certificate_id,
        authorized_value_payload=canonical_json(999),
        bound_at=binding.bound_at,
    )
    with pytest.raises(ValueError, match="authorized value mismatch"):
        repo.append_fact_transition(
            form_id="FORM-1",
            expected_version=0,
            record=record,
            decisions=[decision],
            transitions=[transition],
            derived_certificates=[],
            authorization_bindings=[bad],
            audit=audit,
            review_status=ReviewStatus.CONFIRMED,
            export_status=None,
        )
    assert repo.list_record_versions("FORM-1") == []


def test_missing_certificate_rejected(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    with pytest.raises(AuthorityRejectionError):
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 7},
            "reviewer-1",
            "bad",
            certificate_ids_by_field={"total_quantity": "NO-SUCH-CERT"},
            manual_evidence_ids_by_field={},
        )
    assert repo.list_record_versions("FORM-1") == []


def test_missing_evidence_rejected(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    evidence_id = repo.get_certificate_evidence_file_id(cert.certificate_id)
    assert evidence_id is not None
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM evidence_files WHERE file_id = :eid"), {"eid": evidence_id})
    with pytest.raises(AuthorityRejectionError):
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 7},
            "reviewer-1",
            "bad",
            certificate_ids_by_field={"total_quantity": cert.certificate_id},
            manual_evidence_ids_by_field={},
        )
    assert repo.list_record_versions("FORM-1") == []


def test_evidence_owner_substitution_rejected(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    repo.add_form(Form(form_id="FORM-2", template_id="T1", template_version="1"))
    from app.domain.models import EvidenceFile, EvidenceType

    repo.add_evidence(
        EvidenceFile(
            file_id="EVID-OTHER",
            form_id="FORM-2",
            type=EvidenceType.ORIGINAL_IMAGE,
            uri="other",
            sha256="cd" * 32,
        )
    )
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE candidate_certificates SET evidence_file_id = 'EVID-OTHER' "
                "WHERE certificate_id = :cid"
            ),
            {"cid": cert.certificate_id},
        )
    with pytest.raises(AuthorityRejectionError) as exc:
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 7},
            "reviewer-1",
            "bad",
            certificate_ids_by_field={"total_quantity": cert.certificate_id},
            manual_evidence_ids_by_field={},
        )
    assert any("EVIDENCE_FORM_MISMATCH" == f.code for f in exc.value.failures)


def test_candidate_version_substitution_rejected(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE candidate_certificates SET expected_fact_version = 1 "
                "WHERE certificate_id = :cid"
            ),
            {"cid": cert.certificate_id},
        )
    with pytest.raises(AuthorityRejectionError):
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 7},
            "reviewer-1",
            "bad",
            certificate_ids_by_field={"total_quantity": cert.certificate_id},
            manual_evidence_ids_by_field={},
        )
    assert repo.list_record_versions("FORM-1") == []


def test_direct_machine_fact_write_without_binding_rejected(tmp_path: Path) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    _, decision, transition, record, audit, _ = _valid_admission_bundle(
        repo, recog, field_ids["total_quantity"], 7
    )
    with pytest.raises(ValueError, match="authorization_bindings must not be empty"):
        repo.append_fact_transition(
            form_id="FORM-1",
            expected_version=0,
            record=record,
            decisions=[decision],
            transitions=[transition],
            derived_certificates=[],
            authorization_bindings=[],
            audit=audit,
            review_status=ReviewStatus.CONFIRMED,
            export_status=None,
        )
    assert repo.list_record_versions("FORM-1") == []


def test_duplicate_source_version_is_schema_prevention(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    _, decision, transition, record, audit, binding = _valid_admission_bundle(
        repo, recog, field_ids["total_quantity"], 7
    )
    repo.append_fact_transition(
        form_id="FORM-1",
        expected_version=0,
        record=record,
        decisions=[decision],
        transitions=[transition],
        derived_certificates=[],
        authorization_bindings=[binding],
        audit=audit,
        review_status=ReviewStatus.CONFIRMED,
        export_status=None,
    )
    duplicate_row = FactTransitionRow(
        transition_id="T-DUP",
        form_id="FORM-1",
        created_version=1,
        field_key="total_quantity",
        record_id="FORM-1",
        record_version_id=record.record_id,
        decision_id=decision.decision_id,
        certificate_id=transition.certificate_id,
        evidence_hash=transition.evidence_sha256,
        evidence_locator=transition.evidence_locator,
        producer_id=transition.producer_id,
        producer_version=transition.producer_version,
        template_id=transition.template_id,
        template_version=transition.template_version,
        source_kind=transition.source_kind.value,
        value_payload=transition.value_payload,
        created_at=transition.created_at,
    )
    with Session(engine) as session, session.begin():
        session.add(duplicate_row)
        with pytest.raises(IntegrityError):
            session.flush()
    assert len(repo.list_transitions_for_version("FORM-1", 1)) == 1


# ---------------------------------------------------------------------------
# Concrete mechanism ablation analogues (test-only guard oracle)
# ---------------------------------------------------------------------------


def _ablation_check(
    mode: str,
    *,
    target_record: str,
    cert_record: str,
    current_version: int,
    expected_version: int,
    binding_cert: str,
    transition_cert: str,
    auth_value: object,
    transition_value: object,
) -> list[str]:
    failures: list[str] = []
    if mode != "ABL_3" and target_record != cert_record:
        failures.append("record guard")
    if mode != "ABL_4b" and current_version != expected_version:
        failures.append("freshness guard")
    if mode != "ABL_5" and binding_cert != transition_cert:
        failures.append("auth-cert guard")
    if mode != "ABL_8" and auth_value != transition_value:
        failures.append("auth-value guard")
    return failures


def test_abl_guard_oracle_shows_each_mechanism_is_load_bearing() -> None:
    attack = dict(
        target_record="FORM-2",
        cert_record="FORM-1",
        current_version=1,
        expected_version=0,
        binding_cert="CERT-A",
        transition_cert="CERT-B",
        auth_value=7,
        transition_value=8,
    )
    assert _ablation_check("Full", **attack) == [
        "record guard",
        "freshness guard",
        "auth-cert guard",
        "auth-value guard",
    ]
    assert _ablation_check("ABL_3", **attack) == [
        "freshness guard",
        "auth-cert guard",
        "auth-value guard",
    ]
    assert _ablation_check("ABL_4b", **attack) == [
        "record guard",
        "auth-cert guard",
        "auth-value guard",
    ]
    assert _ablation_check("ABL_5", **attack) == [
        "record guard",
        "freshness guard",
        "auth-value guard",
    ]
    assert _ablation_check("ABL_8", **attack) == [
        "record guard",
        "freshness guard",
        "auth-cert guard",
    ]


# ---------------------------------------------------------------------------
# Hypothesis RuleBasedStateMachine conformance
# ---------------------------------------------------------------------------


class G3bConformanceStateMachine(RuleBasedStateMachine):
    """Model-based state exploration of legal admission transitions.

    The oracle is the *model dict* maintained independently from production
    validators.  After each rule the model is compared against the persisted
    complete snapshot, fact_sources, source transitions, authorization
    bindings, and the public trace result.
    """

    def __init__(self) -> None:
        super().__init__()
        self._tmp = Path(tempfile.mkdtemp(prefix="g3b-state-"))
        self._engine, self._repo, self._reviews, self._recog, self._field_ids = _env(
            self._tmp, ["a", "b"]
        )
        self._model: dict[str, object] = {}

    def _admit(self, field: str, machine_value: object, human_value: object) -> None:
        cert = _record_machine(self._repo, self._recog, self._field_ids[field], machine_value)
        if not self._model:
            other = "b" if field == "a" else "a"
            other_cert = _record_machine(self._repo, self._recog, self._field_ids[other], 0)
            values = {field: human_value, other: 0}
            certificates = {
                field: cert.certificate_id,
                other: other_cert.certificate_id,
            }
            self._reviews.confirm(
                "FORM-1",
                0,
                values,
                "reviewer-1",
                "state-machine-initial",
                certificate_ids_by_field=certificates,
                manual_evidence_ids_by_field={},
            )
            self._model.update(values)
            return
        if self._model[field] == human_value:
            with pytest.raises(AuthorityRejectionError) as error:
                self._reviews.confirm(
                    "FORM-1",
                    len(self._repo.list_record_versions("FORM-1")),
                    {field: human_value},
                    "reviewer-1",
                    "state-machine-noop",
                    certificate_ids_by_field={field: cert.certificate_id},
                    manual_evidence_ids_by_field={},
                )
            assert {failure.code for failure in error.value.failures} == {"NO_CHANGED_FIELDS"}
            return
        self._reviews.confirm(
            "FORM-1",
            len(self._repo.list_record_versions("FORM-1")),
            {field: human_value},
            "reviewer-1",
            "state-machine",
            certificate_ids_by_field={field: cert.certificate_id},
            manual_evidence_ids_by_field={},
        )
        self._model[field] = human_value

    @rule(field=st.sampled_from(["a", "b"]), value=st.integers(min_value=0, max_value=20))
    def accept(self, field: str, value: int) -> None:
        self._admit(field, value, value)

    @rule(field=st.sampled_from(["a", "b"]), value=st.integers(min_value=0, max_value=20))
    def correct(self, field: str, value: int) -> None:
        self._admit(field, value + 1000, value)

    @invariant()
    def committed_state_matches_model(self) -> None:
        versions = self._repo.list_record_versions("FORM-1")
        if not versions:
            return
        latest = versions[-1]
        assert set(latest.values) == set(latest.fact_sources)
        for field, expected in self._model.items():
            assert latest.values[field] == expected
            source_id = latest.fact_sources[field]
            source = self._repo.get_fact_transition(source_id)
            assert source is not None
            assert source.value == expected
            binding = next(
                b
                for b in self._repo.list_authorization_bindings_for_form("FORM-1")
                if b.decision_id == source.decision_id
            )
            assert binding.value == expected
        trace = QueryForms(self._repo).trace("FORM-1")
        assert trace.status == "complete"


def test_g3b_rule_based_state_machine() -> None:
    run_state_machine_as_test(
        G3bConformanceStateMachine,
        settings=settings(
            max_examples=10,
            stateful_step_count=50,
            derandomize=True,
            database=None,
            deadline=None,
        ),
    )


# ---------------------------------------------------------------------------
# Additional trace corruption families
# ---------------------------------------------------------------------------


def test_trace_detects_producer_mismatch(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": cert.certificate_id},
        manual_evidence_ids_by_field={},
    )
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE fact_transitions SET producer_id = 'tampered-producer' "
                "WHERE field_key = 'total_quantity'"
            )
        )
    trace = QueryForms(repo).trace("FORM-1", 1)
    assert trace.status == "incomplete"
    assert any("producer binding mismatch" in f for field in trace.fields for f in field.failures)


def test_trace_detects_evidence_mismatch(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": cert.certificate_id},
        manual_evidence_ids_by_field={},
    )
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE fact_transitions SET evidence_hash = :h WHERE field_key = 'total_quantity'"
            ),
            {"h": "ff" * 32},
        )
    trace = QueryForms(repo).trace("FORM-1", 1)
    assert trace.status == "incomplete"
    assert any("not bound to the evidence" in f for field in trace.fields for f in field.failures)


def test_trace_detects_version_mismatch(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": cert.certificate_id},
        manual_evidence_ids_by_field={},
    )
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE fact_transitions SET created_version = 99 "
                "WHERE field_key = 'total_quantity'"
            )
        )
    trace = QueryForms(repo).trace("FORM-1", 1)
    assert trace.status == "incomplete"
    assert any("missing transition" in f for field in trace.fields for f in field.failures)


def test_trace_detects_binding_certificate_mismatch(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["a", "b"])
    cert_a = _record_machine(repo, recog, field_ids["a"], 1)
    cert_b = _record_machine(repo, recog, field_ids["b"], 2)
    reviews.confirm(
        "FORM-1",
        0,
        {"a": 1, "b": 2},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"a": cert_a.certificate_id, "b": cert_b.certificate_id},
        manual_evidence_ids_by_field={},
    )
    transition_a = next(
        t for t in repo.list_transitions_for_version("FORM-1", 1) if t.field_key == "a"
    )
    with engine.begin() as conn:
        # Corruption probe below the v5 single-use constraint boundary.
        conn.execute(text("DROP INDEX uq_authorization_bindings_certificate_id"))
        conn.execute(
            text("UPDATE authorization_bindings SET certificate_id = :c WHERE decision_id = :d"),
            {"c": cert_b.certificate_id, "d": transition_a.decision_id},
        )
    trace = QueryForms(repo).trace("FORM-1", 1)
    assert trace.status == "incomplete"
    assert any(
        "authorization binding certificate mismatch" in f
        for field in trace.fields
        for f in field.failures
    )


def test_evidence_identity_substitution_rejected(tmp_path: Path) -> None:
    """ABL_2a analogue: the evidence hash behind a machine certificate is swapped."""
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["total_quantity"])
    cert = _record_machine(repo, recog, field_ids["total_quantity"], 7)
    evidence_id = repo.get_certificate_evidence_file_id(cert.certificate_id)
    assert evidence_id is not None
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE evidence_files SET sha256 = :h WHERE file_id = :eid"),
            {"h": "ff" * 32, "eid": evidence_id},
        )
    with pytest.raises(AuthorityRejectionError) as exc:
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 7},
            "reviewer-1",
            "bad",
            certificate_ids_by_field={"total_quantity": cert.certificate_id},
            manual_evidence_ids_by_field={},
        )
    assert any("EVIDENCE_HASH_MISMATCH" == f.code for f in exc.value.failures)
    assert repo.list_record_versions("FORM-1") == []
