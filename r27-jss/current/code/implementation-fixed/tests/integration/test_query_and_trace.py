from pathlib import Path

from sqlalchemy import create_engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.import_forms import ImportForms
from app.application.query_forms import FormFilters, QueryForms
from app.application.review_forms import ReviewForms
from app.domain.models import FormField


def seed(tmp_path: Path) -> QueryForms:
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
    for number, employee, work_order in [(1, "E001", "WO-1"), (2, "E002", "WO-2")]:
        image = tmp_path / f"scan-{number}.png"
        image.write_bytes(f"image-{number}".encode())
        evidence = imports.import_image(image, f"FORM-{number:04d}", "T1", "1", "operator")
        values = {
            "employee_id": employee,
            "work_order_id": work_order,
            "total_quantity": number * 10,
            "qualified_quantity": number * 9,
        }
        for index, field_name in enumerate(values, start=1):
            repository.add_form_field(
                FormField(
                    f"FIELD-{number}-{index}",
                    f"FORM-{number:04d}",
                    field_name,
                    {"x": 0, "y": 0, "w": 8, "h": 8},
                )
            )
        reviews.confirm(
            f"FORM-{number:04d}",
            0,
            values,
            "reviewer",
            "confirmed",
            certificate_ids_by_field={field: None for field in values},
            manual_evidence_ids_by_field={field: evidence.file_id for field in values},
        )
    return QueryForms(repository)


def test_combined_exact_filters_use_and_semantics(tmp_path: Path) -> None:
    queries = seed(tmp_path)

    matches = queries.search(FormFilters(employee_id="E001", work_order_id="WO-1"))
    no_matches = queries.search(FormFilters(employee_id="E001", work_order_id="WO-2"))

    assert [match.form.form_id for match in matches] == ["FORM-0001"]
    assert no_matches == []


def test_trace_returns_versions_evidence_and_audit_events(tmp_path: Path) -> None:
    queries = seed(tmp_path)

    trace = queries.trace("FORM-0001")

    assert trace.form.form_id == "FORM-0001"
    assert len(trace.versions) == 1
    assert len(trace.evidence) == 1
    assert [event.event_type for event in trace.audits] == ["IMPORT", "CONFIRM"]
