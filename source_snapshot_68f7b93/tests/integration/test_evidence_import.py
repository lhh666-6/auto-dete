from pathlib import Path

import pytest
from sqlalchemy import create_engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.import_forms import (
    AudioTrigger,
    DuplicateEvidenceError,
    ImportForms,
    InvalidAudioBindingError,
)


def make_service(tmp_path: Path) -> tuple[ImportForms, SqlAlchemyFormRepository]:
    engine = create_engine(f"sqlite:///{tmp_path / 'demo.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    storage = LocalEvidenceStorage(tmp_path / "evidence")
    return ImportForms(repository, repository, repository, storage), repository


def test_image_import_is_content_addressed_audited_and_immutable(tmp_path: Path) -> None:
    source = tmp_path / "scan.png"
    source.write_bytes(b"synthetic-image")
    service, repository = make_service(tmp_path)

    evidence = service.import_image(source, "FORM-0001", "T1", "1", "operator-a")

    stored_path = tmp_path / "evidence" / Path(evidence.uri)
    assert source.read_bytes() == b"synthetic-image"
    assert stored_path.read_bytes() == b"synthetic-image"
    assert evidence.sha256 == "6f252e1d85c9df6308cbb574aa764fcb8d35d477e9cca0adfa6257617f1fffd7"
    assert evidence.immutable is True
    assert repository.get_form("FORM-0001") is not None
    assert [event.event_type for event in repository.list_audit_events("FORM-0001")] == ["IMPORT"]


def test_duplicate_file_is_rejected_without_overwriting_evidence(tmp_path: Path) -> None:
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    first.write_bytes(b"same-content")
    second.write_bytes(b"same-content")
    service, _ = make_service(tmp_path)
    imported = service.import_image(first, "FORM-0001", "T1", "1", "operator-a")
    stored_path = tmp_path / "evidence" / Path(imported.uri)

    with pytest.raises(DuplicateEvidenceError):
        service.import_image(second, "FORM-0002", "T1", "1", "operator-a")

    assert stored_path.read_bytes() == b"same-content"
    assert second.read_bytes() == b"same-content"


def test_audio_requires_an_explicit_business_trigger(tmp_path: Path) -> None:
    image = tmp_path / "scan.png"
    audio = tmp_path / "note.wav"
    image.write_bytes(b"image")
    audio.write_bytes(b"audio")
    service, _ = make_service(tmp_path)
    service.import_image(image, "FORM-0001", "T1", "1", "operator-a")

    with pytest.raises(InvalidAudioBindingError):
        service.import_audio(audio, "FORM-0001", "operator-a", AudioTrigger())

    evidence = service.import_audio(
        audio,
        "FORM-0001",
        "operator-a",
        AudioTrigger(exception_code="E99"),
    )
    assert evidence.form_id == "FORM-0001"
