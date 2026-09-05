"""R4 persisted evidence-identity admission and trace tests."""

from pathlib import Path

import pytest
from sqlalchemy import text

from app.application.query_forms import QueryForms
from app.application.review_forms import AuthorityRejectionError
from app.domain.evidence_identity import locator_from_evidence
from tests.conformance.oracle import database_digest
from tests.conformance.test_g3b_conformance import _env, _record_machine


def test_recognition_certificate_uses_persisted_canonical_locator(
    tmp_path: Path,
) -> None:
    _, repo, _, recog, field_ids = _env(tmp_path, ["a"])
    certificate = _record_machine(repo, recog, field_ids["a"], 1)
    evidence_id = repo.get_certificate_evidence_file_id(certificate.certificate_id)
    assert evidence_id is not None
    evidence = repo.get_evidence(evidence_id)
    assert evidence is not None
    assert certificate.evidence_locator == locator_from_evidence(evidence)
    assert evidence.file_id not in certificate.evidence_locator


def test_related_field_substitution_rejects_without_authority_write(
    tmp_path: Path,
) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["a", "b"])
    certificate = _record_machine(repo, recog, field_ids["a"], 1)
    evidence_id = repo.get_certificate_evidence_file_id(certificate.certificate_id)
    assert evidence_id is not None
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE evidence_files SET related_field_id = :field WHERE file_id = :evidence"),
            {"field": field_ids["b"], "evidence": evidence_id},
        )
    before = database_digest(engine)
    with pytest.raises(AuthorityRejectionError) as error:
        reviews.confirm(
            "FORM-1",
            0,
            {"a": 1, "b": 0},
            "reviewer-1",
            "tampered locator",
            certificate_ids_by_field={
                "a": certificate.certificate_id,
                "b": None,
            },
            manual_evidence_ids_by_field={"b": evidence_id},
        )
    assert "EVIDENCE_LOCATOR_MISMATCH" in {failure.code for failure in error.value.failures}
    assert database_digest(engine) == before


def test_trace_detects_persisted_uri_substitution(tmp_path: Path) -> None:
    engine, repo, reviews, recog, field_ids = _env(tmp_path, ["a"])
    certificate = _record_machine(repo, recog, field_ids["a"], 1)
    reviews.confirm(
        "FORM-1",
        0,
        {"a": 1},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"a": certificate.certificate_id},
        manual_evidence_ids_by_field={},
    )
    evidence_id = repo.get_certificate_evidence_file_id(certificate.certificate_id)
    assert evidence_id is not None
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE evidence_files SET uri = :uri WHERE file_id = :evidence"),
            {"uri": "field-crops/ff/rebound.png", "evidence": evidence_id},
        )
    trace = QueryForms(repo).trace("FORM-1", 1)
    assert trace.status == "incomplete"
    assert any(
        "persisted evidence locator mismatch" in failure
        for field in trace.fields
        for failure in field.failures
    )
