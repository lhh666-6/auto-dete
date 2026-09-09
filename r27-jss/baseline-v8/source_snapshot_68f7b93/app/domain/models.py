"""Framework-independent business entities."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


def utc_now() -> datetime:
    return datetime.now(UTC)


class ReviewStatus(StrEnum):
    IMPORTED = "IMPORTED"
    RECAPTURE_REQUIRED = "RECAPTURE_REQUIRED"
    CLASSIFIED = "CLASSIFIED"
    NEEDS_CLASSIFICATION = "NEEDS_CLASSIFICATION"
    RECOGNIZED = "RECOGNIZED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    AUTO_APPROVED = "AUTO_APPROVED"
    CONFIRMED = "CONFIRMED"
    CORRECTED = "CORRECTED"
    SUPERSEDED = "SUPERSEDED"
    VOIDED = "VOIDED"


class ExportStatus(StrEnum):
    NOT_EXPORTED = "NOT_EXPORTED"
    EXPORTED = "EXPORTED"
    REEXPORT_REQUIRED = "REEXPORT_REQUIRED"


class RecordStatus(StrEnum):
    DRAFT = "DRAFT"
    AUTO_APPROVED = "AUTO_APPROVED"
    CONFIRMED = "CONFIRMED"
    CORRECTED = "CORRECTED"
    SUPERSEDED = "SUPERSEDED"
    VOIDED = "VOIDED"


class AIStatus(StrEnum):
    NOT_RUN = "NOT_RUN"
    SUGGESTED = "SUGGESTED"
    UNAVAILABLE = "UNAVAILABLE"
    ADOPTED = "ADOPTED"
    REJECTED = "REJECTED"


class EvidenceType(StrEnum):
    ORIGINAL_IMAGE = "ORIGINAL_IMAGE"
    AUDIO = "AUDIO"
    FIELD_CROP = "FIELD_CROP"
    CORRECTED_IMAGE = "CORRECTED_IMAGE"


class ValueSource(StrEnum):
    HUMAN_CONFIRMED = "HUMAN_CONFIRMED"
    AUTO_APPROVED = "AUTO_APPROVED"


@dataclass(slots=True)
class Form:
    form_id: str
    template_id: str
    template_version: str
    coordinate_version: str = "1"
    review_status: ReviewStatus = ReviewStatus.IMPORTED
    export_status: ExportStatus = ExportStatus.NOT_EXPORTED
    current_record_version: int = 0
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class FormField:
    field_id: str
    form_id: str
    field_name: str
    source_region: dict[str, int]
    current_value: Any = None
    current_value_source: ValueSource | None = None
    current_record_version: int = 0


@dataclass(slots=True)
class RecognitionAttempt:
    attempt_id: str
    field_id: str
    engine: str
    model_version: str
    candidate_value: Any
    confidence: float
    crop_file_id: str
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class EvidenceFile:
    file_id: str
    form_id: str
    type: EvidenceType
    uri: str
    sha256: str
    related_field_id: str | None = None
    immutable: bool = True
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class RecordVersion:
    record_id: str
    form_id: str
    version: int
    status: RecordStatus
    values: dict[str, Any]
    previous_version: int | None = None
    change_reason: str = ""
    confirmed_by: str | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class AuditEvent:
    event_id: str
    form_id: str
    event_type: str
    actor_id: str
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    reason: str | None = None
    evidence_ids: tuple[str, ...] = ()
    timestamp: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class ExportBatch:
    export_batch_id: str
    export_type: str
    filters: dict[str, Any]
    included_records: tuple[tuple[str, int], ...]
    file_path: str
    file_sha256: str
    exported_by: str
    exported_at: datetime = field(default_factory=utc_now)
    supersedes_batch_id: str | None = None


@dataclass(slots=True)
class AIReviewRecord:
    review_id: str
    form_id: str
    status: AIStatus
    payload: dict[str, Any]
    created_at: datetime = field(default_factory=utc_now)
