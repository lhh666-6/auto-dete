"""SQLAlchemy persistence schema."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Dialect,
    ForeignKey,
    Index,
    Integer,
    String,
    TypeDecorator,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class UTCDateTime(TypeDecorator[datetime]):
    """Stores naive UTC in the database; always returns aware UTC.

    SQLite's DateTime(timezone=True) round-trips naive datetimes, so the
    authority tables use this type instead and reject naive input at bind
    time (fail-closed, never a silent TypeError later).
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        del dialect
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timezone-aware datetime required")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        del dialect
        return value.replace(tzinfo=UTC) if value is not None else None


class Base(DeclarativeBase):
    pass


class FormRow(Base):
    __tablename__ = "forms"

    form_id: Mapped[str] = mapped_column(String, primary_key=True)
    template_id: Mapped[str] = mapped_column(String, nullable=False)
    template_version: Mapped[str] = mapped_column(String, nullable=False)
    coordinate_version: Mapped[str] = mapped_column(String, nullable=False)
    review_status: Mapped[str] = mapped_column(String, nullable=False)
    export_status: Mapped[str] = mapped_column(String, nullable=False)
    current_record_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RecordVersionRow(Base):
    __tablename__ = "record_versions"
    __table_args__ = (UniqueConstraint("form_id", "version"),)

    record_id: Mapped[str] = mapped_column(String, primary_key=True)
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.form_id"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_version: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, nullable=False)
    values: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    fact_sources: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)
    change_reason: Mapped[str] = mapped_column(String, nullable=False, default="")
    confirmed_by: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FormFieldRow(Base):
    __tablename__ = "form_fields"

    field_id: Mapped[str] = mapped_column(String, primary_key=True)
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.form_id"), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String, nullable=False)
    source_region: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False)
    current_value: Mapped[Any | None] = mapped_column(JSON)
    current_value_source: Mapped[str | None] = mapped_column(String)
    current_record_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class RecognitionAttemptRow(Base):
    __tablename__ = "recognition_attempts"

    attempt_id: Mapped[str] = mapped_column(String, primary_key=True)
    field_id: Mapped[str] = mapped_column(
        ForeignKey("form_fields.field_id"), nullable=False, index=True
    )
    engine: Mapped[str] = mapped_column(String, nullable=False)
    model_version: Mapped[str] = mapped_column(String, nullable=False)
    candidate_value: Mapped[Any | None] = mapped_column(JSON)
    confidence: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    crop_file_id: Mapped[str] = mapped_column(ForeignKey("evidence_files.file_id"), nullable=False)


class EvidenceFileRow(Base):
    __tablename__ = "evidence_files"

    file_id: Mapped[str] = mapped_column(String, primary_key=True)
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.form_id"), nullable=False, index=True)
    related_field_id: Mapped[str | None] = mapped_column(String)
    type: Mapped[str] = mapped_column(String, nullable=False)
    uri: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # Content hashes identify immutable bytes, but are not row identities: two
    # independently recorded field crops may legitimately contain identical
    # pixels. Original-file duplicate rejection remains an ImportForms policy.
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    immutable: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AuditEventRow(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.form_id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    actor_id: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    before: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    after: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    reason: Mapped[str | None] = mapped_column(String)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class ExportBatchRow(Base):
    __tablename__ = "export_batches"

    export_batch_id: Mapped[str] = mapped_column(String, primary_key=True)
    export_type: Mapped[str] = mapped_column(String, nullable=False)
    filters: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    included_records: Mapped[list[list[Any]]] = mapped_column(JSON, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    file_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    exported_by: Mapped[str] = mapped_column(String, nullable=False)
    exported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    supersedes_batch_id: Mapped[str | None] = mapped_column(String)


class AIReviewRow(Base):
    __tablename__ = "ai_reviews"

    review_id: Mapped[str] = mapped_column(String, primary_key=True)
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.form_id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CandidateCertificateRow(Base):
    """One immutable candidate certificate (content-addressed)."""

    __tablename__ = "candidate_certificates"

    certificate_id: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    field_key: Mapped[str] = mapped_column(String, nullable=False)
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.form_id"), nullable=False, index=True)
    field_id: Mapped[str | None] = mapped_column(ForeignKey("form_fields.field_id"))
    evidence_file_id: Mapped[str] = mapped_column(
        ForeignKey("evidence_files.file_id"), nullable=False
    )
    recognition_attempt_id: Mapped[str | None] = mapped_column(
        ForeignKey("recognition_attempts.attempt_id"), unique=True
    )
    value_payload: Mapped[str] = mapped_column(String, nullable=False)
    evidence_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_locator: Mapped[str] = mapped_column(String, nullable=False)
    template_id: Mapped[str] = mapped_column(String, nullable=False)
    template_version: Mapped[str] = mapped_column(String, nullable=False)
    source_kind: Mapped[str] = mapped_column(String, nullable=False)
    producer_id: Mapped[str] = mapped_column(String, nullable=False)
    producer_version: Mapped[str] = mapped_column(String, nullable=False)
    selection_artifact_id: Mapped[str | None] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(nullable=False)
    selection_state: Mapped[str] = mapped_column(String, nullable=False)
    lineage_parent_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    target_record_id: Mapped[str] = mapped_column(String, nullable=False)
    expected_fact_version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)


class HumanDecisionRow(Base):
    """One attributable human decision (one decision per candidate/field)."""

    __tablename__ = "human_decisions"

    decision_id: Mapped[str] = mapped_column(String, primary_key=True)
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.form_id"), nullable=False, index=True)
    candidate_id: Mapped[str] = mapped_column(String, nullable=False)
    field_key: Mapped[str] = mapped_column(String, nullable=False)
    reviewer_id: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    manual_resolution: Mapped[bool] = mapped_column(nullable=False, default=False)
    decided_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)


class FactTransitionRow(Base):
    """One fact transition per (form, created_version, field)."""

    __tablename__ = "fact_transitions"
    __table_args__ = (
        UniqueConstraint("form_id", "created_version", "field_key"),
        Index("uq_fact_transitions_decision_id", "decision_id", unique=True),
        Index("uq_fact_transitions_certificate_id", "certificate_id", unique=True),
    )

    transition_id: Mapped[str] = mapped_column(String, primary_key=True)
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.form_id"), nullable=False, index=True)
    created_version: Mapped[int] = mapped_column(Integer, nullable=False)
    field_key: Mapped[str] = mapped_column(String, nullable=False)
    record_id: Mapped[str] = mapped_column(String, nullable=False)
    record_version_id: Mapped[str] = mapped_column(
        ForeignKey("record_versions.record_id"), nullable=False
    )
    decision_id: Mapped[str] = mapped_column(
        ForeignKey("human_decisions.decision_id"), nullable=False
    )
    certificate_id: Mapped[str] = mapped_column(
        ForeignKey("candidate_certificates.certificate_id"), nullable=False
    )
    evidence_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_locator: Mapped[str] = mapped_column(String, nullable=False)
    producer_id: Mapped[str] = mapped_column(String, nullable=False)
    producer_version: Mapped[str] = mapped_column(String, nullable=False)
    template_id: Mapped[str] = mapped_column(String, nullable=False)
    template_version: Mapped[str] = mapped_column(String, nullable=False)
    source_kind: Mapped[str] = mapped_column(String, nullable=False)
    value_payload: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)


class AuthorizationBindingRow(Base):
    """One immutable authorization decision binding.

    Each binding freezes: decision_id, the reviewed certificate_id, and the
    exact human-authorized final value payload, all inside the same trusted
    admission transaction.
    """

    __tablename__ = "authorization_bindings"
    __table_args__ = (
        Index("uq_authorization_bindings_decision_id", "decision_id", unique=True),
        Index("uq_authorization_bindings_certificate_id", "certificate_id", unique=True),
    )

    binding_id: Mapped[str] = mapped_column(String, primary_key=True)
    decision_id: Mapped[str] = mapped_column(
        ForeignKey("human_decisions.decision_id"), nullable=False, index=True
    )
    certificate_id: Mapped[str] = mapped_column(
        ForeignKey("candidate_certificates.certificate_id"), nullable=False, index=True
    )
    authorized_value_payload: Mapped[str] = mapped_column(String, nullable=False)
    bound_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)


class AuthorityMetaRow(Base):
    """Small key/value metadata for the authority layer.

    certificate_era_started_at marks the moment the certificate system
    became active (written by stamp_schema_version). Record versions created
    strictly before it have no transitions by definition (legacy); versions
    created at or after it must carry a complete transition set — a version
    without transitions in the certificate era is corruption, never
    pre-certificate.
    """

    __tablename__ = "authority_meta"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String, nullable=False)
