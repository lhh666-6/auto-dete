from app.domain.models import (
    EvidenceFile,
    EvidenceType,
    ExportStatus,
    Form,
    RecognitionAttempt,
    RecordStatus,
    RecordVersion,
    ReviewStatus,
)


def test_new_form_starts_imported_and_not_exported() -> None:
    form = Form(form_id="FORM-0001", template_id="T1", template_version="1")

    assert form.review_status is ReviewStatus.IMPORTED
    assert form.export_status is ExportStatus.NOT_EXPORTED
    assert form.current_record_version == 0


def test_evidence_attempt_and_record_are_separate_append_only_facts() -> None:
    evidence = EvidenceFile(
        file_id="FILE-1",
        form_id="FORM-0001",
        type=EvidenceType.ORIGINAL_IMAGE,
        uri="images/FILE-1.png",
        sha256="a" * 64,
    )
    attempt = RecognitionAttempt(
        attempt_id="ATTEMPT-1",
        field_id="FIELD-1",
        engine="manual-placeholder",
        model_version="disabled",
        candidate_value="8",
        confidence=0.0,
        crop_file_id="FILE-1",
    )
    record = RecordVersion(
        record_id="RECORD-1",
        form_id="FORM-0001",
        version=1,
        status=RecordStatus.CONFIRMED,
        values={"total_quantity": 8},
    )

    assert {evidence.file_id, attempt.attempt_id, record.record_id} == {
        "FILE-1",
        "ATTEMPT-1",
        "RECORD-1",
    }
    assert evidence.immutable is True
