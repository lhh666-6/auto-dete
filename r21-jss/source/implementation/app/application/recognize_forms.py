"""Classification and append-only recognition orchestration."""

from dataclasses import dataclass
from typing import Any, Protocol
from uuid import uuid4

import cv2
from numpy.typing import NDArray

from app.adapters.recognition.candidate import RecognitionCandidate
from app.adapters.recognition.opencv import OpenCvImagePipeline, QualityAssessment
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.ports import (
    AuditRepository,
    CandidateWritePort,
    EvidenceRepository,
    FormRepository,
)
from app.domain.authority import (
    CandidateCertificate,
    SelectionState,
    SourceKind,
)
from app.domain.evidence_identity import locator_from_evidence
from app.domain.models import (
    AuditEvent,
    EvidenceFile,
    EvidenceType,
    Form,
    RecognitionAttempt,
    ReviewStatus,
    utc_now,
)

# Selection-rule artifact identifier for the recognition engine's acceptance
# threshold policy. It identifies the selection rule applied, not a
# statistical calibration claim (design D1(c)).
RECOGNITION_SELECTION_ARTIFACT = "recognition-threshold-v1"


class RecognitionRepository(Protocol):
    def add_recognition_attempt(self, attempt: RecognitionAttempt) -> None: ...
    def set_template(
        self, form_id: str, template_id: str, template_version: str, status: ReviewStatus
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    template_reference: str | None
    source: str
    confidence: float


class RecognizeForms:
    def __init__(
        self,
        forms: FormRepository,
        evidence: EvidenceRepository,
        audits: AuditRepository,
        storage: LocalEvidenceStorage,
        pipeline: OpenCvImagePipeline,
        *,
        candidate_writer: CandidateWritePort,
    ) -> None:
        self._forms = forms
        self._evidence = evidence
        self._audits = audits
        self._candidate_writer = candidate_writer
        self._recognition: RecognitionRepository = forms  # type: ignore[assignment]
        self._storage = storage
        self._pipeline = pipeline

    def assess_quality(self, image: NDArray[Any]) -> QualityAssessment:
        return self._pipeline.assess_quality(image)

    def classify_image(self, form_id: str, image: NDArray[Any]) -> ClassificationResult:
        form = self._require_form(form_id)
        reference = self._pipeline.read_template_qr(image)
        if reference:
            template_id, separator, version = reference.partition(":")
            self._recognition.set_template(
                form_id,
                template_id,
                version if separator else "1",
                ReviewStatus.CLASSIFIED,
            )
            self._audit_classification(form, template_id, version if separator else "1", "QR")
            return ClassificationResult(reference, "QR", 1.0)
        self._forms.set_review_status(form_id, ReviewStatus.NEEDS_CLASSIFICATION)
        return ClassificationResult(None, "NONE", 0.0)

    def manual_reclassify(
        self,
        form_id: str,
        template_id: str,
        template_version: str,
        actor_id: str,
        reason: str,
    ) -> None:
        form = self._require_form(form_id)
        self._recognition.set_template(
            form_id, template_id, template_version, ReviewStatus.CLASSIFIED
        )
        self._audits.add_audit_event(
            AuditEvent(
                event_id=f"EVENT-{uuid4().hex}",
                form_id=form_id,
                event_type="RECLASSIFY",
                actor_id=actor_id,
                before={
                    "template_id": form.template_id,
                    "template_version": form.template_version,
                },
                after={"template_id": template_id, "template_version": template_version},
                reason=reason,
            )
        )

    def record_candidate(
        self,
        form_id: str,
        field_id: str,
        crop: NDArray[Any],
        candidate: RecognitionCandidate[Any],
        actor_id: str,
    ) -> RecognitionAttempt:
        """Record one machine candidate atomically with its certificate.

        The crop file is written to storage first; then evidence row,
        recognition attempt, candidate certificate, and the RECOGNIZE audit
        event persist in one transaction. On any database failure the file
        is discarded best-effort and nothing remains referenceable: an
        orphan file has no certificate row, so it can never be confirmed.
        The machine still has no path to a fact.
        """
        form = self._require_form(form_id)
        field = self._forms.get_form_field(field_id)
        if field is None:
            raise ValueError(f"Unknown field: {field_id}")
        if field.form_id != form_id:
            raise ValueError(f"field {field_id} belongs to form {field.form_id}, not {form_id}")
        encoded, buffer = cv2.imencode(".png", crop)
        if not encoded:
            raise ValueError("Field crop could not be encoded")
        stored = self._storage.store_bytes(buffer.tobytes(), ".png", "field-crops")
        attempt_id = f"ATTEMPT-{uuid4().hex}"
        try:
            crop_evidence = EvidenceFile(
                file_id=stored.file_id,
                form_id=form_id,
                related_field_id=field_id,
                type=EvidenceType.FIELD_CROP,
                uri=stored.uri,
                sha256=stored.sha256,
            )
            attempt = RecognitionAttempt(
                attempt_id=attempt_id,
                field_id=field_id,
                engine=candidate.engine,
                model_version=candidate.model_version,
                candidate_value=candidate.value,
                confidence=candidate.confidence,
                crop_file_id=crop_evidence.file_id,
            )
            certificate = CandidateCertificate.from_value(
                candidate_id=attempt_id,
                field_key=field.field_name,
                value=candidate.value,
                evidence_hash=stored.sha256,
                evidence_locator=locator_from_evidence(crop_evidence),
                template_id=form.template_id,
                template_version=form.template_version,
                source_kind=SourceKind.RECOGNITION,
                producer_id=candidate.engine,
                producer_version=candidate.model_version,
                selection_artifact_id=RECOGNITION_SELECTION_ARTIFACT,
                confidence=candidate.confidence,
                selection_state=(
                    SelectionState.SELECTED if candidate.accepted else SelectionState.ABSTAINED
                ),
                lineage_parent_ids=(),
                target_record_id=form_id,
                expected_fact_version=form.current_record_version,
                created_at=utc_now(),
            )
            audit = AuditEvent(
                event_id=f"EVENT-{uuid4().hex}",
                form_id=form_id,
                event_type="RECOGNIZE",
                actor_id=actor_id,
                after={
                    "attempt_id": attempt.attempt_id,
                    "field_id": field_id,
                    "candidate": candidate.value,
                    "confidence": candidate.confidence,
                },
                evidence_ids=(crop_evidence.file_id,),
            )
            self._candidate_writer.append_candidate_unit(
                evidence=crop_evidence,
                attempt=attempt,
                certificate=certificate,
                audit=audit,
                field_id=field_id,
            )
        except Exception:
            self._storage.discard(stored.uri)
            raise
        return attempt

    def _require_form(self, form_id: str) -> Form:
        form = self._forms.get_form(form_id)
        if form is None:
            raise KeyError(f"Unknown form: {form_id}")
        return form

    def _audit_classification(
        self, before: Form, template_id: str, template_version: str, source: str
    ) -> None:
        self._audits.add_audit_event(
            AuditEvent(
                event_id=f"EVENT-{uuid4().hex}",
                form_id=before.form_id,
                event_type="CLASSIFY",
                actor_id="system",
                before={
                    "template_id": before.template_id,
                    "template_version": before.template_version,
                },
                after={
                    "template_id": template_id,
                    "template_version": template_version,
                    "source": source,
                },
            )
        )
