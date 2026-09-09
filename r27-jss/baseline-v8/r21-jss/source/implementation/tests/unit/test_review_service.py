from pathlib import Path

import pytest
from sqlalchemy import create_engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.import_forms import ImportForms
from app.application.review_forms import ConcurrentReviewError, ReviewForms
from app.domain.models import FormField, RecordStatus, ReviewStatus


def build_services(tmp_path: Path) -> tuple[ImportForms, ReviewForms, SqlAlchemyFormRepository]:
    engine = create_engine(f"sqlite:///{tmp_path / 'demo.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    imports = ImportForms(
        repository, repository, repository, LocalEvidenceStorage(tmp_path / "evidence")
    )
    reviews = ReviewForms(
        repository,
        repository,
        authority_read=repository,
        admission=repository,
        known_producers=frozenset({("human-reviewer", "manual-entry-v1")}),
        known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
    )
    return imports, reviews, repository


def test_confirmation_and_correction_append_versions_and_audits(tmp_path: Path) -> None:
    imports, reviews, repository = build_services(tmp_path)
    image = tmp_path / "scan.png"
    image.write_bytes(b"image")
    evidence = imports.import_image(image, "FORM-0001", "T1", "1", "operator-a")
    repository.add_form_field(
        FormField("FIELD-1", "FORM-0001", "total_quantity", {"x": 0, "y": 0, "w": 8, "h": 8})
    )

    first = reviews.confirm(
        form_id="FORM-0001",
        expected_version=0,
        values={"total_quantity": 10},
        actor_id="reviewer-a",
        reason="initial confirmation",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": evidence.file_id},
    )
    second = reviews.confirm(
        form_id="FORM-0001",
        expected_version=1,
        values={"total_quantity": 12},
        actor_id="reviewer-b",
        reason="paper correction box",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": evidence.file_id},
    )

    assert first.status is RecordStatus.CONFIRMED
    assert second.status is RecordStatus.CORRECTED
    assert second.previous_version == 1
    assert repository.get_form("FORM-0001").review_status is ReviewStatus.CONFIRMED  # type: ignore[union-attr]
    assert [event.event_type for event in repository.list_audit_events("FORM-0001")] == [
        "IMPORT",
        "CONFIRM",
        "CORRECT",
    ]
    assert repository.list_audit_events("FORM-0001")[-1].before == {"total_quantity": 10}


def test_review_rejects_a_stale_expected_version(tmp_path: Path) -> None:
    imports, reviews, repository = build_services(tmp_path)
    image = tmp_path / "scan.png"
    image.write_bytes(b"image")
    evidence = imports.import_image(image, "FORM-0001", "T1", "1", "operator-a")
    repository.add_form_field(
        FormField("FIELD-1", "FORM-0001", "total_quantity", {"x": 0, "y": 0, "w": 8, "h": 8})
    )
    reviews.confirm(
        "FORM-0001",
        0,
        {"total_quantity": 10},
        "reviewer-a",
        "initial",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": evidence.file_id},
    )

    with pytest.raises(ConcurrentReviewError):
        reviews.confirm(
            "FORM-0001",
            0,
            {"total_quantity": 11},
            "reviewer-b",
            "stale",
            certificate_ids_by_field={"total_quantity": None},
            manual_evidence_ids_by_field={"total_quantity": evidence.file_id},
        )
