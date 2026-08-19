from pathlib import Path

from sqlalchemy import create_engine

from app.adapters.ai.disabled import DisabledAIReview
from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.export.xlsx import XlsxExporter
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.export_forms import ExportForms
from app.application.import_forms import ImportForms
from app.application.query_forms import FormFilters, QueryForms
from app.application.review_forms import ReviewForms
from app.domain.models import AIStatus


def test_ai_disabled_does_not_block_import_review_or_export(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'demo.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    imports = ImportForms(
        repository, repository, repository, LocalEvidenceStorage(tmp_path / "evidence")
    )
    image = tmp_path / "scan.png"
    image.write_bytes(b"image")
    evidence = imports.import_image(image, "FORM-0001", "T1", "1", "operator")
    values = {"employee_id": "E001", "total_quantity": 10}
    ReviewForms(
        repository,
        repository,
        known_producers=frozenset({("human-reviewer", "manual-entry-v1")}),
        known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
    ).confirm(
        "FORM-0001",
        0,
        values,
        "reviewer",
        "confirmed",
        certificate_ids_by_field={field: None for field in values},
        manual_evidence_ids_by_field={field: evidence.file_id for field in values},
    )

    ai_review = DisabledAIReview().review("FORM-0001", {})
    batch = ExportForms(repository, XlsxExporter(), QueryForms(repository)).export(
        "OUTPUT", FormFilters(), tmp_path / "exports", "finance"
    )

    assert ai_review.status is AIStatus.NOT_RUN
    assert Path(batch.file_path).exists()
