"""AI suggestions are persisted as candidates, never as facts."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import (
    SqlAlchemyFormRepository,
    install_sqlite_pragmas,
)
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.ai_suggestion_forms import AISuggestionForms
from app.domain.authority import CandidateCertificate
from app.domain.models import EvidenceFile, EvidenceType, Form, FormField

NOW = datetime(2026, 8, 27, 8, 0, tzinfo=UTC)


def _repository(tmp_path: Path) -> SqlAlchemyFormRepository:
    engine = create_engine(f"sqlite:///{tmp_path / 'authority.db'}")
    install_sqlite_pragmas(engine)
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    repository.add_form(Form("FORM-1", "T1", "1"))
    repository.add_form_field(
        FormField("FIELD-1", "FORM-1", "total_quantity", {"x": 0, "y": 0, "w": 8, "h": 8})
    )
    repository.add_evidence(
        EvidenceFile(
            file_id="EVID-PARENT",
            form_id="FORM-1",
            type=EvidenceType.FIELD_CROP,
            uri="field-crops/parent.png",
            sha256="ab" * 32,
            related_field_id="FIELD-1",
        )
    )
    parent = CandidateCertificate.from_manual_entry(
        candidate_id="parent-candidate",
        field_key="total_quantity",
        value=7,
        form_id="FORM-1",
        evidence_hash="ab" * 32,
        evidence_locator="FORM-1/field/total_quantity",
        template_id="T1",
        template_version="1",
        target_record_id="FORM-1",
        expected_fact_version=0,
        created_at=NOW,
    )
    repository.add_certificate(
        parent,
        field_id="FIELD-1",
        evidence_file_id="EVID-PARENT",
        recognition_attempt_id=None,
    )
    return repository


def _service(tmp_path: Path, repository: SqlAlchemyFormRepository) -> AISuggestionForms:
    return AISuggestionForms(
        forms=repository,
        authority=repository,
        candidate_writer=repository,
        storage=LocalEvidenceStorage(tmp_path / "evidence"),
        clock=lambda: NOW,
    )


def test_propose_persists_parent_linked_candidate_without_fact_transition(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    parent = repository.list_certificates_for_field("FORM-1", "total_quantity", 0)[0]

    result = _service(tmp_path, repository).propose(
        form_id="FORM-1",
        field_id="FIELD-1",
        parent_certificate_id=parent.certificate_id,
        value=8,
        confidence=0.73,
        producer_id="deepseek-harness",
        producer_version="dsh-v0.1.1-rc.2+b150a551b",
        selection_artifact_id="DSH-EXEC-1",
        session_id="DSH-SESSION-1",
        execution_id="DSH-EXEC-1",
    )

    stored = repository.get_certificate(result.certificate_id)
    assert stored is not None
    assert stored.value == 8
    assert stored.lineage_parent_ids == (parent.certificate_id,)
    assert stored.expected_fact_version == 0
    assert repository.get_form("FORM-1").current_record_version == 0  # type: ignore[union-attr]
    assert repository.list_record_versions("FORM-1") == []
    assert len(repository.list_evidence("FORM-1")) == 2
    assert repository.get_evidence(result.evidence_file_id).type is EvidenceType.AI_OUTPUT  # type: ignore[union-attr]
    assert (tmp_path / "evidence" / result.evidence_uri).exists()


@pytest.mark.parametrize(
    ("field_id", "parent_id", "message"),
    [
        ("FIELD-1", "missing", "unknown parent certificate"),
        ("missing", "PARENT", "unknown field"),
    ],
)
def test_propose_rejects_unknown_context_without_writes(
    tmp_path: Path, field_id: str, parent_id: str, message: str
) -> None:
    repository = _repository(tmp_path)
    parent = repository.list_certificates_for_field("FORM-1", "total_quantity", 0)[0]
    if parent_id == "PARENT":
        parent_id = parent.certificate_id
    evidence_before = len(repository.list_evidence("FORM-1"))

    with pytest.raises(ValueError, match=message):
        _service(tmp_path, repository).propose(
            form_id="FORM-1",
            field_id=field_id,
            parent_certificate_id=parent_id,
            value=8,
            confidence=0.73,
            producer_id="deepseek-harness",
            producer_version="dsh-v0.1.1-rc.2+b150a551b",
            selection_artifact_id="DSH-EXEC-1",
            session_id="DSH-SESSION-1",
            execution_id="DSH-EXEC-1",
        )

    assert len(repository.list_evidence("FORM-1")) == evidence_before
    assert [path for path in (tmp_path / "evidence").rglob("*") if path.is_file()] == []


def test_propose_discards_file_when_atomic_database_append_fails(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    parent = repository.list_certificates_for_field("FORM-1", "total_quantity", 0)[0]

    class FailingWriter:
        def append_candidate_certificate(self, **kwargs: object) -> None:
            raise RuntimeError("database unavailable")

    service = AISuggestionForms(
        forms=repository,
        authority=repository,
        candidate_writer=FailingWriter(),
        storage=LocalEvidenceStorage(tmp_path / "evidence"),
        clock=lambda: NOW,
    )

    with pytest.raises(RuntimeError, match="database unavailable"):
        service.propose(
            form_id="FORM-1",
            field_id="FIELD-1",
            parent_certificate_id=parent.certificate_id,
            value=8,
            confidence=0.73,
            producer_id="deepseek-harness",
            producer_version="dsh-v0.1.1-rc.2+b150a551b",
            selection_artifact_id="DSH-EXEC-1",
            session_id="DSH-SESSION-1",
            execution_id="DSH-EXEC-1",
        )

    assert [path for path in (tmp_path / "evidence").rglob("*") if path.is_file()] == []
