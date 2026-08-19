from pathlib import Path

from sqlalchemy import create_engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.import_forms import ImportForms
from app.application.review_forms import ReviewForms


def test_manual_loop_operates_without_ocr_or_ai(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'demo.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    imports = ImportForms(
        repository, repository, repository, LocalEvidenceStorage(tmp_path / "evidence")
    )
    reviews = ReviewForms(
        repository,
        repository,
        known_producers=frozenset({("human-reviewer", "manual-entry-v1")}),
        known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
    )
    image = tmp_path / "manual-form.png"
    image.write_bytes(b"manual-form")

    evidence = imports.import_image(image, "FORM-0001", "MANUAL", "1", "operator-a")
    values = {
        "employee_id": "E001",
        "total_quantity": 25,
        "qualified_quantity": 24,
    }
    record = reviews.confirm(
        "FORM-0001",
        0,
        values,
        "reviewer-a",
        "manual entry",
        certificate_ids_by_field={field: None for field in values},
        manual_evidence_ids_by_field={field: evidence.file_id for field in values},
    )

    restored = repository.list_record_versions("FORM-0001")
    assert record.version == 1
    assert restored[0].values["qualified_quantity"] == 24
    assert len(repository.list_audit_events("FORM-0001")) == 2
