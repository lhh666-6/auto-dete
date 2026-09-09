from pathlib import Path

import cv2
import numpy as np
from sqlalchemy import create_engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.recognition.candidate import RecognitionCandidate
from app.adapters.recognition.opencv import OpenCvImagePipeline
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.import_forms import ImportForms
from app.application.query_forms import QueryForms
from app.application.recognize_forms import RecognizeForms
from app.application.review_forms import ReviewForms
from app.domain.models import FormField, ReviewStatus


def build(tmp_path: Path):  # type: ignore[no-untyped-def]
    engine = create_engine(f"sqlite:///{tmp_path / 'demo.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    storage = LocalEvidenceStorage(tmp_path / "evidence")
    imports = ImportForms(repository, repository, repository, storage)
    recognizer = RecognizeForms(
        repository,
        repository,
        repository,
        storage,
        OpenCvImagePipeline(),
        candidate_writer=repository,
    )
    return imports, recognizer, repository


def test_recognition_attempts_append_and_never_change_confirmed_values(tmp_path: Path) -> None:
    imports, recognizer, repository = build(tmp_path)
    image = tmp_path / "scan.png"
    image.write_bytes(b"image")
    evidence = imports.import_image(image, "FORM-0001", "T1", "1", "operator")
    repository.add_form_field(
        FormField(
            "FIELD-1", "FORM-0001", "total_quantity", {"x": 0, "y": 0, "width": 48, "height": 64}
        )
    )
    ReviewForms(
        repository,
        repository,
        authority_read=repository,
        admission=repository,
        known_producers=frozenset({("human-reviewer", "manual-entry-v1")}),
        known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
    ).confirm(
        "FORM-0001",
        0,
        {"total_quantity": 8},
        "reviewer",
        "confirmed",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": evidence.file_id},
    )
    before_version = repository.get_form("FORM-0001").current_record_version  # type: ignore[union-attr]
    crop = np.full((64, 48), 255, dtype=np.uint8)
    cv2.putText(crop, "7", (6, 53), cv2.FONT_HERSHEY_SIMPLEX, 1.8, 0, 3, cv2.LINE_AA)
    candidate = RecognitionCandidate("7", 0.95, "test-engine", "v1", "OK")

    recognizer.record_candidate("FORM-0001", "FIELD-1", crop, candidate, "recognizer")
    recognizer.record_candidate("FORM-0001", "FIELD-1", crop.copy(), candidate, "recognizer")

    attempts = repository.list_recognition_attempts("FIELD-1")
    assert len(attempts) == 2
    assert attempts[0].candidate_value == "7"
    assert attempts[0].crop_file_id != attempts[1].crop_file_id
    assert repository.get_form("FORM-0001").current_record_version == before_version  # type: ignore[union-attr]
    assert repository.list_record_versions("FORM-0001")[-1].values == {"total_quantity": 8}
    trace = QueryForms(repository).trace("FORM-0001")
    assert len(trace.attempts) == 2
    assert len([item for item in trace.evidence if item.related_field_id == "FIELD-1"]) == 2


def test_missing_qr_requires_classification_and_manual_choice_is_audited(tmp_path: Path) -> None:
    imports, recognizer, repository = build(tmp_path)
    image = tmp_path / "scan.png"
    image.write_bytes(b"image")
    imports.import_image(image, "FORM-0001", "UNKNOWN", "1", "operator")

    result = recognizer.classify_image("FORM-0001", np.full((200, 200), 255, dtype=np.uint8))
    assert result.template_reference is None
    assert repository.get_form("FORM-0001").review_status is ReviewStatus.NEEDS_CLASSIFICATION  # type: ignore[union-attr]

    recognizer.manual_reclassify("FORM-0001", "T2", "3", "reviewer", "QR damaged")

    restored = repository.get_form("FORM-0001")
    assert restored is not None
    assert (restored.template_id, restored.template_version) == ("T2", "3")
    assert restored.review_status is ReviewStatus.CLASSIFIED
    assert repository.list_audit_events("FORM-0001")[-1].event_type == "RECLASSIFY"
