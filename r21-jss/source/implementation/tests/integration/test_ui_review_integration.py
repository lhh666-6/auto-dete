"""UI review page integration: persisted machine certificates (P1-1).

The production review page must let the reviewer choose a DB-loaded machine
certificate per field or the manual path, and pass ids only. These tests
drive the page's selection helper against the real services.
"""

from pathlib import Path

import numpy as np
import pytest
from sqlalchemy import create_engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.recognition.candidate import RecognitionCandidate
from app.adapters.recognition.opencv import OpenCvImagePipeline
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.query_forms import QueryForms
from app.application.recognize_forms import RecognizeForms
from app.application.review_forms import ReviewForms
from app.domain.models import EvidenceFile, EvidenceType, Form, FormField
from app.ui.pages.review import ReviewValuesError, build_selection


def _env(tmp_path: Path):
    """FORM-1 with EVID-1, one recognized machine field, and one plain field."""
    from datetime import UTC, datetime

    NOW = datetime(2026, 8, 17, 9, 0, tzinfo=UTC)
    engine = create_engine(f"sqlite:///{tmp_path / 'ui.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    repository.add_form(
        Form(form_id="FORM-1", template_id="T1", template_version="1", created_at=NOW)
    )
    repository.add_evidence(
        EvidenceFile(
            file_id="EVID-1",
            form_id="FORM-1",
            type=EvidenceType.ORIGINAL_IMAGE,
            uri="ev-1",
            sha256="ab" * 32,
            created_at=NOW,
        )
    )
    repository.add_form_field(
        FormField("FIELD-1", "FORM-1", "total_quantity", {"x": 0, "y": 0, "w": 8, "h": 8})
    )
    repository.add_form_field(
        FormField("FIELD-2", "FORM-1", "qualified_quantity", {"x": 0, "y": 0, "w": 8, "h": 8})
    )
    reviews = ReviewForms(
        repository,
        repository,
        authority_read=repository,
        admission=repository,
        known_producers=frozenset(
            {
                ("human-reviewer", "manual-entry-v1"),
                ("recognizer-a", "1.0"),
            }
        ),
        known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
    )
    recognition = RecognizeForms(
        repository,
        repository,
        repository,
        LocalEvidenceStorage(tmp_path / "evidence"),
        OpenCvImagePipeline(),
        candidate_writer=repository,
    )
    crop = np.full((64, 48), 255, dtype=np.uint8)
    recognition.record_candidate(
        "FORM-1",
        "FIELD-1",
        crop,
        RecognitionCandidate(7, 0.9, "recognizer-a", "1.0", "OK"),
        "machine",
    )
    certificate = repository.list_certificates_for_form("FORM-1")[0]
    return repository, reviews, certificate


def test_eligible_certificates_scoped_by_field_and_version(tmp_path: Path) -> None:
    _, reviews, certificate = _env(tmp_path)

    eligible = reviews.eligible_certificates("FORM-1", 0, "total_quantity")
    assert [item.certificate_id for item in eligible] == [certificate.certificate_id]
    # wrong field: no eligibility
    assert reviews.eligible_certificates("FORM-1", 0, "qualified_quantity") == []
    # wrong expected version: no eligibility
    assert reviews.eligible_certificates("FORM-1", 1, "total_quantity") == []


def test_ui_build_selection_machine_and_manual_fields(tmp_path: Path) -> None:
    repository, reviews, certificate = _env(tmp_path)

    values = {"total_quantity": 7, "qualified_quantity": 5}
    certificate_ids_by_field, manual_evidence_ids_by_field = build_selection(
        reviews,
        "FORM-1",
        0,
        values,
        {"total_quantity": certificate.certificate_id, "qualified_quantity": None},
        "EVID-1",
    )
    assert certificate_ids_by_field == {
        "total_quantity": certificate.certificate_id,
        "qualified_quantity": None,
    }
    assert manual_evidence_ids_by_field == {"qualified_quantity": "EVID-1"}

    record = reviews.confirm(
        "FORM-1",
        0,
        values,
        "reviewer-1",
        "ui review",
        certificate_ids_by_field=certificate_ids_by_field,
        manual_evidence_ids_by_field=manual_evidence_ids_by_field,
    )
    assert record.version == 1
    transitions = {
        transition.field_key: transition
        for transition in repository.list_transitions_for_version("FORM-1", 1)
    }
    # machine-bound field keeps the persisted certificate
    assert transitions["total_quantity"].certificate_id == certificate.certificate_id
    # manual field derives a MANUAL_ENTRY certificate
    manual_transition = transitions["qualified_quantity"]
    assert manual_transition.producer_id == "human-reviewer"
    manual_certificate = repository.get_certificate(manual_transition.certificate_id)
    assert manual_certificate is not None
    assert manual_certificate.source_kind.value == "MANUAL_ENTRY"
    # the whole version traces complete through the real query path
    trace = QueryForms(repository).trace("FORM-1")
    assert trace.status == "complete"
    assert all(field.status == "complete" for field in trace.fields)


def test_ui_build_selection_requires_evidence_for_manual_field(tmp_path: Path) -> None:
    _, reviews, certificate = _env(tmp_path)

    with pytest.raises(ReviewValuesError):
        build_selection(
            reviews,
            "FORM-1",
            0,
            {"total_quantity": 7},
            {"total_quantity": None},
            None,
        )


def test_ui_build_selection_passes_ids_only(tmp_path: Path) -> None:
    _, _, certificate = _env(tmp_path)

    values = {"total_quantity": 7}
    certificate_ids_by_field, manual_evidence_ids_by_field = build_selection(
        reviews=None,  # type: ignore[arg-type]
        form_id="FORM-1",
        expected_version=0,
        values=values,
        chosen_by_field={"total_quantity": certificate.certificate_id},
        manual_evidence_id=None,
    )
    assert certificate_ids_by_field == {"total_quantity": certificate.certificate_id}
    assert manual_evidence_ids_by_field == {}
