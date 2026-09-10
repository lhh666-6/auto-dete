"""R3 tests for the central, exact admission-bundle boundary."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from sqlalchemy import insert, update

from app.adapters.database.models import FormRow, RecordVersionRow
from app.application.review_forms import AuthorityRejectionError
from app.domain.authority import (
    AuthorizationBinding,
    FactTransition,
    HumanDecision,
    canonical_json,
)
from app.domain.models import AuditEvent, RecordStatus, RecordVersion, ReviewStatus, utc_now
from tests.conformance.oracle import database_digest
from tests.conformance.test_g3b_conformance import (
    _env,
    _record_machine,
    _valid_admission_bundle,
)


def test_initial_certificate_snapshot_requires_every_declared_field(
    tmp_path: Path,
) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["a", "b"])
    certificate = _record_machine(repo, recog, field_ids["a"], 1)
    before = database_digest(engine)
    with pytest.raises(AuthorityRejectionError) as error:
        reviews.confirm(
            "FORM-1",
            0,
            {"a": 1},
            "reviewer-1",
            "partial initial",
            certificate_ids_by_field={"a": certificate.certificate_id},
            manual_evidence_ids_by_field={},
        )
    assert {failure.code for failure in error.value.failures} == {"INITIAL_FIELD_SET_MISMATCH"}
    assert database_digest(engine) == before


def test_full_subsequent_snapshot_emits_only_changed_field_chain(
    tmp_path: Path,
) -> None:
    _, repo, reviews, recog, field_ids = _env(tmp_path, ["a", "b"])
    cert_a1 = _record_machine(repo, recog, field_ids["a"], 1)
    cert_b1 = _record_machine(repo, recog, field_ids["b"], 2)
    reviews.confirm(
        "FORM-1",
        0,
        {"a": 1, "b": 2},
        "reviewer-1",
        "initial",
        certificate_ids_by_field={
            "a": cert_a1.certificate_id,
            "b": cert_b1.certificate_id,
        },
        manual_evidence_ids_by_field={},
    )
    old_b_source = repo.list_record_versions("FORM-1")[-1].fact_sources["b"]
    cert_a2 = _record_machine(repo, recog, field_ids["a"], 3)
    cert_b2 = _record_machine(repo, recog, field_ids["b"], 2)
    reviews.confirm(
        "FORM-1",
        1,
        {"a": 3, "b": 2},
        "reviewer-1",
        "full snapshot",
        certificate_ids_by_field={
            "a": cert_a2.certificate_id,
            "b": cert_b2.certificate_id,
        },
        manual_evidence_ids_by_field={},
    )
    transitions = repo.list_transitions_for_version("FORM-1", 2)
    assert [transition.field_key for transition in transitions] == ["a"]
    latest = repo.list_record_versions("FORM-1")[-1]
    assert latest.values == {"a": 3, "b": 2}
    assert latest.fact_sources["b"] == old_b_source


def test_post_initial_noop_rejects_without_authority_writes(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["a"])
    cert1 = _record_machine(repo, recog, field_ids["a"], 1)
    reviews.confirm(
        "FORM-1",
        0,
        {"a": 1},
        "reviewer-1",
        "initial",
        certificate_ids_by_field={"a": cert1.certificate_id},
        manual_evidence_ids_by_field={},
    )
    cert2 = _record_machine(repo, recog, field_ids["a"], 1)
    before = database_digest(engine)
    with pytest.raises(AuthorityRejectionError) as error:
        reviews.confirm(
            "FORM-1",
            1,
            {"a": 1},
            "reviewer-1",
            "noop",
            certificate_ids_by_field={"a": cert2.certificate_id},
            manual_evidence_ids_by_field={},
        )
    assert {failure.code for failure in error.value.failures} == {"NO_CHANGED_FIELDS"}
    assert database_digest(engine) == before


def test_repository_rejects_hidden_changed_field_with_zero_writes(
    tmp_path: Path,
) -> None:
    engine, repo, _, recog, field_ids = _env(tmp_path, ["a"])
    cert1, decision1, transition1, record1, audit1, binding1 = _valid_admission_bundle(
        repo, recog, field_ids["a"], 1
    )
    assert repo.append_fact_transition(
        form_id="FORM-1",
        expected_version=0,
        record=record1,
        decisions=[decision1],
        transitions=[transition1],
        derived_certificates=[],
        authorization_bindings=[binding1],
        audit=audit1,
        review_status=ReviewStatus.CONFIRMED,
        export_status=None,
    )
    cert2 = _record_machine(repo, recog, field_ids["a"], 2)
    now = utc_now()
    decision2 = HumanDecision(
        decision_id="FORM-1:2:a",
        reviewer_id="reviewer-1",
        candidate_id=cert2.candidate_id,
        field_key="a",
        reason="hidden change",
        decided_at=now,
    )
    binding2 = AuthorizationBinding(
        binding_id="FORM-1:2:a:AUTH",
        decision_id=decision2.decision_id,
        certificate_id=cert2.certificate_id,
        authorized_value_payload=canonical_json(2),
        bound_at=now,
    )
    record2 = RecordVersion(
        record_id="REC-2",
        form_id="FORM-1",
        version=2,
        previous_version=1,
        status=RecordStatus.CORRECTED,
        values={"a": 2, "hidden": 999},
        change_reason="hidden change",
        confirmed_by="reviewer-1",
        created_at=now,
    )
    transition2 = FactTransition(
        transition_id=decision2.decision_id,
        record_id="FORM-1",
        field_key="a",
        created_version=2,
        record_version_id=record2.record_id,
        decision_id=decision2.decision_id,
        certificate_id=cert2.certificate_id,
        evidence_sha256=cert2.evidence_hash,
        evidence_locator=cert2.evidence_locator,
        producer_id=cert2.producer_id,
        producer_version=cert2.producer_version,
        source_kind=cert2.source_kind,
        template_id=cert2.template_id,
        template_version=cert2.template_version,
        value_payload=canonical_json(2),
        created_at=now,
    )
    audit2 = AuditEvent(
        event_id="EVENT-2",
        form_id="FORM-1",
        event_type="CORRECT",
        actor_id="reviewer-1",
        before={"a": 1},
        after=record2.values,
    )
    before = database_digest(engine)
    with pytest.raises(ValueError, match="declared field domain"):
        repo.append_fact_transition(
            form_id="FORM-1",
            expected_version=1,
            record=record2,
            decisions=[decision2],
            transitions=[transition2],
            derived_certificates=[],
            authorization_bindings=[binding2],
            audit=audit2,
            review_status=ReviewStatus.CONFIRMED,
            export_status=None,
        )
    assert database_digest(engine) == before


def test_repository_rejects_decision_candidate_mismatch(tmp_path: Path) -> None:
    engine, repo, _, recog, field_ids = _env(tmp_path, ["a"])
    certificate, decision, transition, record, audit, binding = _valid_admission_bundle(
        repo, recog, field_ids["a"], 1
    )
    del certificate
    bad_decision = replace(decision, candidate_id="OTHER-CANDIDATE")
    before = database_digest(engine)
    with pytest.raises(ValueError, match="decision candidate mismatch"):
        repo.append_fact_transition(
            form_id="FORM-1",
            expected_version=0,
            record=record,
            decisions=[bad_decision],
            transitions=[transition],
            derived_certificates=[],
            authorization_bindings=[binding],
            audit=audit,
            review_status=ReviewStatus.CONFIRMED,
            export_status=None,
        )
    assert database_digest(engine) == before


def test_legacy_snapshot_bootstraps_complete_certificate_field_set(
    tmp_path: Path,
) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["a", "b"])
    now = utc_now()
    with engine.begin() as connection:
        connection.execute(
            update(FormRow).where(FormRow.form_id == "FORM-1").values(current_record_version=1)
        )
        connection.execute(
            insert(RecordVersionRow).values(
                record_id="LEGACY-1",
                form_id="FORM-1",
                version=1,
                previous_version=None,
                status=RecordStatus.CONFIRMED.value,
                values={"a": 0, "b": 0},
                fact_sources={},
                change_reason="legacy import",
                confirmed_by="legacy",
                created_at=now,
            )
        )
    cert_a = _record_machine(repo, recog, field_ids["a"], 1)
    cert_b = _record_machine(repo, recog, field_ids["b"], 2)
    reviews.confirm(
        "FORM-1",
        1,
        {"a": 1, "b": 2},
        "reviewer-1",
        "certificate bootstrap",
        certificate_ids_by_field={
            "a": cert_a.certificate_id,
            "b": cert_b.certificate_id,
        },
        manual_evidence_ids_by_field={},
    )
    latest = repo.list_record_versions("FORM-1")[-1]
    assert latest.version == 2
    assert latest.values == {"a": 1, "b": 2}
    assert set(latest.fact_sources) == {"a", "b"}
    assert {
        transition.field_key for transition in repo.list_transitions_for_version("FORM-1", 2)
    } == {"a", "b"}
