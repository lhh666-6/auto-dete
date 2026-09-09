"""R5 conformance: validate the complete source history, not only the tip."""

from pathlib import Path

from sqlalchemy import create_engine, text

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.application.query_forms import QueryForms
from app.application.review_forms import ReviewForms
from app.domain.models import EvidenceFile, EvidenceType, Form, FormField


def _four_version_history(tmp_path: Path):
    engine = create_engine(f"sqlite:///{tmp_path / 'history.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    repository.add_form(Form("FORM-1", "T1", "1"))
    repository.add_form_field(FormField("FIELD-A", "FORM-1", "a", {"x": 0, "y": 0, "w": 8, "h": 8}))
    repository.add_form_field(FormField("FIELD-B", "FORM-1", "b", {"x": 0, "y": 0, "w": 8, "h": 8}))
    repository.add_evidence(
        EvidenceFile(
            file_id="EVID-1",
            form_id="FORM-1",
            type=EvidenceType.ORIGINAL_IMAGE,
            uri="manual/source.png",
            sha256="ab" * 32,
        )
    )
    reviews = ReviewForms(
        repository,
        repository,
        authority_read=repository,
        admission=repository,
        known_producers=frozenset({("human-reviewer", "manual-entry-v1")}),
        known_selection_artifacts=frozenset(),
    )

    def confirm(expected_version: int, values: dict[str, int]) -> None:
        reviews.confirm(
            "FORM-1",
            expected_version,
            values,
            "reviewer-1",
            "r5",
            certificate_ids_by_field={field: None for field in values},
            manual_evidence_ids_by_field={field: "EVID-1" for field in values},
        )

    confirm(0, {"a": 1, "b": 10})
    confirm(1, {"a": 2})
    confirm(2, {"a": 1})
    confirm(3, {"b": 11})
    return engine, repository


def test_legal_multi_hop_copy_forward_history_is_complete(tmp_path: Path) -> None:
    _, repository = _four_version_history(tmp_path)

    trace = QueryForms(repository).trace("FORM-1", 4)

    assert trace.status == "complete"
    assert all(field.failures == () for field in trace.fields)


def test_same_value_older_source_replacement_is_detected(tmp_path: Path) -> None:
    engine, repository = _four_version_history(tmp_path)
    versions = repository.list_record_versions("FORM-1")
    old_same_value_source = versions[0].fact_sources["a"]
    assert versions[2].values["a"] == versions[3].values["a"] == 1
    assert versions[2].fact_sources["a"] == versions[3].fact_sources["a"]
    assert old_same_value_source != versions[3].fact_sources["a"]

    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE record_versions "
                "SET fact_sources=json_set(fact_sources, '$.a', :source) "
                "WHERE form_id='FORM-1' AND version=4"
            ),
            {"source": old_same_value_source},
        )

    trace = QueryForms(repository).trace("FORM-1", 4)

    assert trace.status == "incomplete"
    field = next(item for item in trace.fields if item.field_key == "a")
    assert "version 4 unchanged field source changed" in field.failures


def test_corrupt_initial_source_domain_taints_later_trace(tmp_path: Path) -> None:
    engine, repository = _four_version_history(tmp_path)
    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE record_versions "
                "SET fact_sources=json_remove(fact_sources, '$.b') "
                "WHERE form_id='FORM-1' AND version=1"
            )
        )

    trace = QueryForms(repository).trace("FORM-1", 4)

    assert trace.status == "incomplete"
    field = next(item for item in trace.fields if item.field_key == "b")
    assert "version 1 missing source for declared field" in field.failures


def test_overwritten_historical_transition_value_is_still_checked(
    tmp_path: Path,
) -> None:
    engine, repository = _four_version_history(tmp_path)
    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE fact_transitions SET value_payload='999' "
                "WHERE form_id='FORM-1' AND created_version=1 AND field_key='a'"
            )
        )

    trace = QueryForms(repository).trace("FORM-1", 4)

    assert trace.status == "incomplete"
    field = next(item for item in trace.fields if item.field_key == "a")
    assert "version 1 source value does not match committed value" in field.failures
