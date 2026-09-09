from pathlib import Path

from sqlalchemy import create_engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.export.xlsx import XlsxExporter
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.export_forms import ExportForms
from app.application.import_forms import ImportForms
from app.application.query_forms import FormFilters, QueryForms
from app.application.review_forms import ReviewForms


def test_every_supported_mutation_has_actor_before_after_reason_and_evidence(
    tmp_path: Path,
) -> None:
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
    exports = ExportForms(repository, XlsxExporter(), QueryForms(repository))
    image = tmp_path / "scan.png"
    image.write_bytes(b"image")
    evidence = imports.import_image(image, "FORM-0001", "T1", "1", "operator")

    def confirm_one(version: int, value: int, actor: str, reason: str) -> None:
        reviews.confirm(
            "FORM-0001", version, {"total_quantity": value}, actor, reason,
            certificate_ids_by_field={"total_quantity": None},
            manual_evidence_ids_by_field={"total_quantity": evidence.file_id},
        )

    confirm_one(0, 10, "reviewer-a", "initial")
    confirm_one(1, 11, "reviewer-b", "correction")
    exports.export("OUTPUT", FormFilters(), tmp_path / "exports", "finance")

    events = repository.list_audit_events("FORM-0001")
    assert [event.event_type for event in events] == ["IMPORT", "CONFIRM", "CORRECT", "EXPORT"]
    assert all(event.actor_id and event.timestamp for event in events)
    assert events[0].after and events[0].evidence_ids == (evidence.file_id,)
    assert events[1].before is None and events[1].after == {"total_quantity": 10}
    assert events[2].before == {"total_quantity": 10}
    assert events[2].after == {"total_quantity": 11}
    assert events[2].reason == "correction"
    assert events[3].after and events[3].after["export_batch_id"]
