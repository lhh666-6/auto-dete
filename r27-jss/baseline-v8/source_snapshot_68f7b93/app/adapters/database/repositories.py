"""SQLAlchemy repository implementations."""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Engine, event, func, insert, select, text, update
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.adapters.database.models import (
    AIReviewRow,
    AuditEventRow,
    AuthorityMetaRow,
    CandidateCertificateRow,
    EvidenceFileRow,
    ExportBatchRow,
    FactTransitionRow,
    FormFieldRow,
    FormRow,
    HumanDecisionRow,
    RecognitionAttemptRow,
    RecordVersionRow,
)
from app.domain.authority import (
    CandidateCertificate,
    FactTransition,
    HumanDecision,
    SelectionState,
    SourceKind,
)
from app.domain.models import (
    AIReviewRecord,
    AIStatus,
    AuditEvent,
    EvidenceFile,
    EvidenceType,
    ExportBatch,
    ExportStatus,
    Form,
    FormField,
    RecognitionAttempt,
    RecordStatus,
    RecordVersion,
    ReviewStatus,
    ValueSource,
    utc_now,
)

SCHEMA_VERSION = 3


def install_sqlite_pragmas(engine: Engine) -> None:
    """Enable foreign keys and a busy timeout on every SQLite connection."""

    @event.listens_for(engine, "connect")
    def _set_pragmas(dbapi_connection: Any, connection_record: Any) -> None:
        del connection_record
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()


def check_schema_version(engine: Engine) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text("PRAGMA user_version")).scalar_one())


def stamp_schema_version(engine: Engine) -> None:
    """Refuse unknown future schemas; stamp the current version.

    Must be called only after all tables and indexes were created
    successfully (the caller runs create_all first).

    The certificate-era start is recorded here (idempotently): the moment
    the certificate system became active on this database. For a database
    that already carries fact transitions the era starts at the earliest
    transition; otherwise at stamping time. Versions created strictly before
    the era are legacy (pre-certificate); versions at or after it must carry
    a complete transition set.
    """
    version = check_schema_version(engine)
    if version > SCHEMA_VERSION:
        raise RuntimeError(
            f"database schema version {version} exceeds supported "
            f"version {SCHEMA_VERSION}"
        )
    with engine.begin() as connection:
        existing = connection.execute(
            select(AuthorityMetaRow.value).where(
                AuthorityMetaRow.key == "certificate_era_started_at"
            )
        ).scalar_one_or_none()
        if existing is None:
            earliest = connection.execute(
                select(func.min(FactTransitionRow.created_at))
            ).scalar_one_or_none()
            era = earliest if earliest is not None else utc_now()
            connection.execute(
                insert(AuthorityMetaRow).values(
                    key="certificate_era_started_at",
                    value=era.isoformat(),
                )
            )
        if version < SCHEMA_VERSION:
            connection.execute(text(f"PRAGMA user_version={SCHEMA_VERSION}"))


class SqlAlchemyFormRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def add_form(self, form: Form) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(
                FormRow(
                    form_id=form.form_id,
                    template_id=form.template_id,
                    template_version=form.template_version,
                    coordinate_version=form.coordinate_version,
                    review_status=form.review_status.value,
                    export_status=form.export_status.value,
                    current_record_version=form.current_record_version,
                    created_at=form.created_at,
                )
            )

    def get_form(self, form_id: str) -> Form | None:
        with Session(self._engine) as session:
            row = session.get(FormRow, form_id)
            if row is None:
                return None
            return Form(
                form_id=row.form_id,
                template_id=row.template_id,
                template_version=row.template_version,
                coordinate_version=row.coordinate_version,
                review_status=ReviewStatus(row.review_status),
                export_status=ExportStatus(row.export_status),
                current_record_version=row.current_record_version,
                created_at=row.created_at,
            )

    def list_record_versions(self, form_id: str) -> list[RecordVersion]:
        statement = (
            select(RecordVersionRow)
            .where(RecordVersionRow.form_id == form_id)
            .order_by(RecordVersionRow.version)
        )
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [
                RecordVersion(
                    record_id=row.record_id,
                    form_id=row.form_id,
                    version=row.version,
                    previous_version=row.previous_version,
                    status=RecordStatus(row.status),
                    values=row.values,
                    change_reason=row.change_reason,
                    confirmed_by=row.confirmed_by,
                    created_at=row.created_at,
                )
                for row in rows
            ]

    def set_review_status(self, form_id: str, status: ReviewStatus) -> None:
        with Session(self._engine) as session, session.begin():
            form = session.get(FormRow, form_id)
            if form is None:
                raise KeyError(f"Unknown form: {form_id}")
            form.review_status = status.value

    def set_template(
        self, form_id: str, template_id: str, template_version: str, status: ReviewStatus
    ) -> None:
        with Session(self._engine) as session, session.begin():
            form = session.get(FormRow, form_id)
            if form is None:
                raise KeyError(f"Unknown form: {form_id}")
            form.template_id = template_id
            form.template_version = template_version
            form.review_status = status.value

    def set_export_status(self, form_id: str, status: ExportStatus) -> None:
        with Session(self._engine) as session, session.begin():
            form = session.get(FormRow, form_id)
            if form is None:
                raise KeyError(f"Unknown form: {form_id}")
            form.export_status = status.value

    def add_evidence(self, evidence: EvidenceFile) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(
                EvidenceFileRow(
                    file_id=evidence.file_id,
                    form_id=evidence.form_id,
                    related_field_id=evidence.related_field_id,
                    type=evidence.type.value,
                    uri=evidence.uri,
                    sha256=evidence.sha256,
                    immutable=evidence.immutable,
                    created_at=evidence.created_at,
                )
            )

    def add_form_field(self, field: FormField) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(
                FormFieldRow(
                    field_id=field.field_id,
                    form_id=field.form_id,
                    field_name=field.field_name,
                    source_region=field.source_region,
                    current_value=field.current_value,
                    current_value_source=(
                        field.current_value_source.value if field.current_value_source else None
                    ),
                    current_record_version=field.current_record_version,
                )
            )

    def get_form_field(self, field_id: str) -> FormField | None:
        with Session(self._engine) as session:
            row = session.get(FormFieldRow, field_id)
            if row is None:
                return None
            return FormField(
                field_id=row.field_id,
                form_id=row.form_id,
                field_name=row.field_name,
                source_region=row.source_region,
                current_value=row.current_value,
                current_value_source=(
                    ValueSource(row.current_value_source)
                    if row.current_value_source is not None
                    else None
                ),
                current_record_version=row.current_record_version,
            )

    def add_recognition_attempt(self, attempt: RecognitionAttempt) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(
                RecognitionAttemptRow(
                    attempt_id=attempt.attempt_id,
                    field_id=attempt.field_id,
                    engine=attempt.engine,
                    model_version=attempt.model_version,
                    candidate_value=attempt.candidate_value,
                    confidence=attempt.confidence,
                    created_at=attempt.created_at,
                    crop_file_id=attempt.crop_file_id,
                )
            )

    def list_recognition_attempts(self, field_id: str) -> list[RecognitionAttempt]:
        statement = (
            select(RecognitionAttemptRow)
            .where(RecognitionAttemptRow.field_id == field_id)
            .order_by(RecognitionAttemptRow.created_at, RecognitionAttemptRow.attempt_id)
        )
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [
                RecognitionAttempt(
                    attempt_id=row.attempt_id,
                    field_id=row.field_id,
                    engine=row.engine,
                    model_version=row.model_version,
                    candidate_value=row.candidate_value,
                    confidence=row.confidence,
                    created_at=row.created_at,
                    crop_file_id=row.crop_file_id,
                )
                for row in rows
            ]

    def list_recognition_attempts_for_form(self, form_id: str) -> list[RecognitionAttempt]:
        statement = (
            select(RecognitionAttemptRow)
            .join(FormFieldRow, FormFieldRow.field_id == RecognitionAttemptRow.field_id)
            .where(FormFieldRow.form_id == form_id)
            .order_by(RecognitionAttemptRow.created_at, RecognitionAttemptRow.attempt_id)
        )
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [
                RecognitionAttempt(
                    attempt_id=row.attempt_id,
                    field_id=row.field_id,
                    engine=row.engine,
                    model_version=row.model_version,
                    candidate_value=row.candidate_value,
                    confidence=row.confidence,
                    created_at=row.created_at,
                    crop_file_id=row.crop_file_id,
                )
                for row in rows
            ]

    def get_evidence(self, file_id: str) -> EvidenceFile | None:
        with Session(self._engine) as session:
            row = session.get(EvidenceFileRow, file_id)
            if row is None:
                return None
            return EvidenceFile(
                file_id=row.file_id,
                form_id=row.form_id,
                related_field_id=row.related_field_id,
                type=EvidenceType(row.type),
                uri=row.uri,
                sha256=row.sha256,
                immutable=row.immutable,
                created_at=row.created_at,
            )

    def get_certificate_evidence_file_id(self, certificate_id: str) -> str | None:
        statement = select(CandidateCertificateRow.evidence_file_id).where(
            CandidateCertificateRow.certificate_id == certificate_id
        )
        with Session(self._engine) as session:
            return session.scalar(statement)

    def find_by_sha256(self, sha256: str) -> EvidenceFile | None:
        statement = select(EvidenceFileRow).where(EvidenceFileRow.sha256 == sha256)
        with Session(self._engine) as session:
            row = session.scalar(statement)
            if row is None:
                return None
            return EvidenceFile(
                file_id=row.file_id,
                form_id=row.form_id,
                related_field_id=row.related_field_id,
                type=EvidenceType(row.type),
                uri=row.uri,
                sha256=row.sha256,
                immutable=row.immutable,
                created_at=row.created_at,
            )

    def add_audit_event(self, event: AuditEvent) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(
                AuditEventRow(
                    event_id=event.event_id,
                    form_id=event.form_id,
                    event_type=event.event_type,
                    actor_id=event.actor_id,
                    timestamp=event.timestamp,
                    before=event.before,
                    after=event.after,
                    reason=event.reason,
                    evidence_ids=list(event.evidence_ids),
                )
            )

    def list_audit_events(self, form_id: str) -> list[AuditEvent]:
        statement = (
            select(AuditEventRow)
            .where(AuditEventRow.form_id == form_id)
            .order_by(AuditEventRow.timestamp, AuditEventRow.event_id)
        )
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [
                AuditEvent(
                    event_id=row.event_id,
                    form_id=row.form_id,
                    event_type=row.event_type,
                    actor_id=row.actor_id,
                    timestamp=row.timestamp,
                    before=row.before,
                    after=row.after,
                    reason=row.reason,
                    evidence_ids=tuple(row.evidence_ids),
                )
                for row in rows
            ]

    def list_evidence(self, form_id: str) -> list[EvidenceFile]:
        statement = (
            select(EvidenceFileRow)
            .where(EvidenceFileRow.form_id == form_id)
            .order_by(EvidenceFileRow.created_at, EvidenceFileRow.file_id)
        )
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [
                EvidenceFile(
                    file_id=row.file_id,
                    form_id=row.form_id,
                    related_field_id=row.related_field_id,
                    type=EvidenceType(row.type),
                    uri=row.uri,
                    sha256=row.sha256,
                    immutable=row.immutable,
                    created_at=row.created_at,
                )
                for row in rows
            ]

    def search_current(
        self,
        *,
        form_id: str | None = None,
        employee_id: str | None = None,
        work_order_id: str | None = None,
        review_status: ReviewStatus | None = None,
        export_status: ExportStatus | None = None,
    ) -> list[tuple[Form, RecordVersion]]:
        statement = select(FormRow, RecordVersionRow).join(
            RecordVersionRow,
            (RecordVersionRow.form_id == FormRow.form_id)
            & (RecordVersionRow.version == FormRow.current_record_version),
        )
        if form_id is not None:
            statement = statement.where(FormRow.form_id == form_id)
        if employee_id is not None:
            statement = statement.where(
                func.json_extract(RecordVersionRow.values, "$.employee_id") == employee_id
            )
        if work_order_id is not None:
            statement = statement.where(
                func.json_extract(RecordVersionRow.values, "$.work_order_id") == work_order_id
            )
        if review_status is not None:
            statement = statement.where(FormRow.review_status == review_status.value)
        if export_status is not None:
            statement = statement.where(FormRow.export_status == export_status.value)
        statement = statement.order_by(FormRow.form_id)
        with Session(self._engine) as session:
            rows = session.execute(statement).all()
            return [(self._to_form(form), self._to_record(record)) for form, record in rows]

    def add_export_batch(self, batch: ExportBatch) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(
                ExportBatchRow(
                    export_batch_id=batch.export_batch_id,
                    export_type=batch.export_type,
                    filters=batch.filters,
                    included_records=[list(item) for item in batch.included_records],
                    file_path=batch.file_path,
                    file_sha256=batch.file_sha256,
                    exported_by=batch.exported_by,
                    exported_at=batch.exported_at,
                    supersedes_batch_id=batch.supersedes_batch_id,
                )
            )

    def list_export_batches(self) -> list[ExportBatch]:
        statement = select(ExportBatchRow).order_by(ExportBatchRow.exported_at)
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [
                ExportBatch(
                    export_batch_id=row.export_batch_id,
                    export_type=row.export_type,
                    filters=row.filters,
                    included_records=tuple(
                        (str(form_id), int(version)) for form_id, version in row.included_records
                    ),
                    file_path=row.file_path,
                    file_sha256=row.file_sha256,
                    exported_by=row.exported_by,
                    exported_at=row.exported_at,
                    supersedes_batch_id=row.supersedes_batch_id,
                )
                for row in rows
            ]

    def add_ai_review(self, review: AIReviewRecord) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(
                AIReviewRow(
                    review_id=review.review_id,
                    form_id=review.form_id,
                    status=review.status.value,
                    payload=review.payload,
                    created_at=review.created_at,
                )
            )

    def list_ai_reviews(self, form_id: str) -> list[AIReviewRecord]:
        statement = (
            select(AIReviewRow)
            .where(AIReviewRow.form_id == form_id)
            .order_by(AIReviewRow.created_at, AIReviewRow.review_id)
        )
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [
                AIReviewRecord(
                    review_id=row.review_id,
                    form_id=row.form_id,
                    status=AIStatus(row.status),
                    payload=row.payload,
                    created_at=row.created_at,
                )
                for row in rows
            ]

    @staticmethod
    def _to_form(row: FormRow) -> Form:
        return Form(
            form_id=row.form_id,
            template_id=row.template_id,
            template_version=row.template_version,
            coordinate_version=row.coordinate_version,
            review_status=ReviewStatus(row.review_status),
            export_status=ExportStatus(row.export_status),
            current_record_version=row.current_record_version,
            created_at=row.created_at,
        )

    @staticmethod
    def _to_record(row: RecordVersionRow) -> RecordVersion:
        return RecordVersion(
            record_id=row.record_id,
            form_id=row.form_id,
            version=row.version,
            previous_version=row.previous_version,
            status=RecordStatus(row.status),
            values=row.values,
            change_reason=row.change_reason,
            confirmed_by=row.confirmed_by,
            created_at=row.created_at,
        )

    # ------------------------------------------------------------------
    # Authority layer (candidate certificates, decisions, transitions)
    # ------------------------------------------------------------------

    def add_certificate(
        self,
        certificate: CandidateCertificate,
        *,
        field_id: str | None,
        evidence_file_id: str,
        recognition_attempt_id: str | None,
    ) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(
                CandidateCertificateRow(
                    certificate_id=certificate.certificate_id,
                    candidate_id=certificate.candidate_id,
                    field_key=certificate.field_key,
                    form_id=certificate.target_record_id,
                    field_id=field_id,
                    evidence_file_id=evidence_file_id,
                    recognition_attempt_id=recognition_attempt_id,
                    value_payload=certificate.value_payload,
                    evidence_hash=certificate.evidence_hash,
                    evidence_locator=certificate.evidence_locator,
                    template_id=certificate.template_id,
                    template_version=certificate.template_version,
                    source_kind=certificate.source_kind.value,
                    producer_id=certificate.producer_id,
                    producer_version=certificate.producer_version,
                    selection_artifact_id=certificate.selection_artifact_id,
                    confidence=certificate.confidence,
                    selection_state=certificate.selection_state.value,
                    lineage_parent_ids=list(certificate.lineage_parent_ids),
                    target_record_id=certificate.target_record_id,
                    expected_fact_version=certificate.expected_fact_version,
                    created_at=certificate.created_at,
                )
            )

    def get_certificate(self, certificate_id: str) -> CandidateCertificate | None:
        with Session(self._engine) as session:
            row = session.get(CandidateCertificateRow, certificate_id)
            return self._to_certificate(row) if row is not None else None

    def list_certificates_for_form(self, form_id: str) -> list[CandidateCertificate]:
        statement = (
            select(CandidateCertificateRow)
            .where(CandidateCertificateRow.form_id == form_id)
            .order_by(CandidateCertificateRow.created_at, CandidateCertificateRow.certificate_id)
        )
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [self._to_certificate(row) for row in rows]

    def list_certificates_for_field(
        self, form_id: str, field_key: str, expected_fact_version: int
    ) -> list[CandidateCertificate]:
        """Certificates eligible for one field at one expected fact version."""
        statement = (
            select(CandidateCertificateRow)
            .where(CandidateCertificateRow.form_id == form_id)
            .where(CandidateCertificateRow.field_key == field_key)
            .where(
                CandidateCertificateRow.expected_fact_version == expected_fact_version
            )
            .order_by(
                CandidateCertificateRow.created_at.desc(),
                CandidateCertificateRow.certificate_id,
            )
        )
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [self._to_certificate(row) for row in rows]

    def get_certificate_era_start(self) -> datetime | None:
        statement = select(AuthorityMetaRow.value).where(
            AuthorityMetaRow.key == "certificate_era_started_at"
        )
        with Session(self._engine) as session:
            raw = session.scalar(statement)
            if raw is None:
                return None
            parsed = datetime.fromisoformat(raw)
            return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)

    def add_decision(self, decision: HumanDecision, *, form_id: str) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(
                HumanDecisionRow(
                    decision_id=decision.decision_id,
                    form_id=form_id,
                    candidate_id=decision.candidate_id,
                    field_key=decision.field_key,
                    reviewer_id=decision.reviewer_id,
                    reason=decision.reason,
                    manual_resolution=decision.manual_resolution,
                    decided_at=decision.decided_at,
                )
            )

    def list_decisions_for_form(self, form_id: str) -> list[HumanDecision]:
        statement = (
            select(HumanDecisionRow)
            .where(HumanDecisionRow.form_id == form_id)
            .order_by(HumanDecisionRow.decided_at, HumanDecisionRow.decision_id)
        )
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [
                HumanDecision(
                    decision_id=row.decision_id,
                    reviewer_id=row.reviewer_id,
                    candidate_id=row.candidate_id,
                    field_key=row.field_key,
                    reason=row.reason,
                    decided_at=row.decided_at,
                    manual_resolution=bool(row.manual_resolution),
                )
                for row in rows
            ]

    def add_transition(self, transition: FactTransition, *, record_version_id: str) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(
                FactTransitionRow(
                    transition_id=transition.transition_id,
                    form_id=transition.record_id,
                    created_version=transition.created_version,
                    field_key=transition.field_key,
                    record_id=transition.record_id,
                    record_version_id=record_version_id,
                    decision_id=transition.decision_id,
                    certificate_id=transition.certificate_id,
                    evidence_hash=transition.evidence_sha256,
                    evidence_locator=transition.evidence_locator,
                    producer_id=transition.producer_id,
                    producer_version=transition.producer_version,
                    template_id=transition.template_id,
                    template_version=transition.template_version,
                    source_kind=transition.source_kind.value,
                    created_at=transition.created_at,
                )
            )

    def list_transitions_for_version(
        self, form_id: str, created_version: int
    ) -> list[FactTransition]:
        statement = (
            select(FactTransitionRow)
            .where(FactTransitionRow.form_id == form_id)
            .where(FactTransitionRow.created_version == created_version)
            .order_by(FactTransitionRow.field_key, FactTransitionRow.transition_id)
        )
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [self._to_transition(row) for row in rows]

    def append_candidate_unit(
        self,
        *,
        evidence: EvidenceFile,
        attempt: RecognitionAttempt,
        certificate: CandidateCertificate,
        audit: AuditEvent,
        field_id: str | None = None,
    ) -> None:
        """Persist evidence + attempt + certificate + audit atomically.

        The field (when given) must belong to the certificate's form (R3);
        a single-column FK cannot express that invariant, so it is checked
        here inside the transaction.
        """
        with self._engine.connect() as connection, connection.begin():
            if field_id is not None:
                field_form_id = connection.execute(
                    select(FormFieldRow.form_id).where(
                        FormFieldRow.field_id == field_id
                    )
                ).scalar_one_or_none()
                if field_form_id is None:
                    raise ValueError(f"unknown field: {field_id}")
                if field_form_id != certificate.target_record_id:
                    raise ValueError(
                        f"field {field_id} belongs to form {field_form_id}, "
                        f"not {certificate.target_record_id}"
                    )
            connection.execute(
                insert(EvidenceFileRow).values(
                    file_id=evidence.file_id,
                    form_id=evidence.form_id,
                    related_field_id=evidence.related_field_id,
                    type=evidence.type.value,
                    uri=evidence.uri,
                    sha256=evidence.sha256,
                    immutable=evidence.immutable,
                    created_at=evidence.created_at,
                )
            )
            connection.execute(
                insert(RecognitionAttemptRow).values(
                    attempt_id=attempt.attempt_id,
                    field_id=attempt.field_id,
                    engine=attempt.engine,
                    model_version=attempt.model_version,
                    candidate_value=attempt.candidate_value,
                    confidence=attempt.confidence,
                    created_at=attempt.created_at,
                    crop_file_id=attempt.crop_file_id,
                )
            )
            connection.execute(
                insert(CandidateCertificateRow).values(
                    certificate_id=certificate.certificate_id,
                    candidate_id=certificate.candidate_id,
                    field_key=certificate.field_key,
                    form_id=certificate.target_record_id,
                    field_id=field_id,
                    evidence_file_id=evidence.file_id,
                    recognition_attempt_id=attempt.attempt_id,
                    value_payload=certificate.value_payload,
                    evidence_hash=certificate.evidence_hash,
                    evidence_locator=certificate.evidence_locator,
                    template_id=certificate.template_id,
                    template_version=certificate.template_version,
                    source_kind=certificate.source_kind.value,
                    producer_id=certificate.producer_id,
                    producer_version=certificate.producer_version,
                    selection_artifact_id=certificate.selection_artifact_id,
                    confidence=certificate.confidence,
                    selection_state=certificate.selection_state.value,
                    lineage_parent_ids=list(certificate.lineage_parent_ids),
                    target_record_id=certificate.target_record_id,
                    expected_fact_version=certificate.expected_fact_version,
                    created_at=certificate.created_at,
                )
            )
            connection.execute(
                insert(AuditEventRow).values(
                    event_id=audit.event_id,
                    form_id=audit.form_id,
                    event_type=audit.event_type,
                    actor_id=audit.actor_id,
                    timestamp=audit.timestamp,
                    before=audit.before,
                    after=audit.after,
                    reason=audit.reason,
                    evidence_ids=list(audit.evidence_ids),
                )
            )

    def append_fact_transition(
        self,
        *,
        form_id: str,
        expected_version: int,
        record: RecordVersion,
        decisions: Sequence[HumanDecision],
        transitions: Sequence[FactTransition],
        derived_certificates: Sequence[tuple[CandidateCertificate, str]],
        audit: AuditEvent,
        review_status: ReviewStatus,
        export_status: ExportStatus | None,
    ) -> bool:
        """Atomic CAS-protected fact transition; returns a conflict result.

        The version CAS is the first write of the transaction. On a
        database-is-locked error the failed transaction is rolled back and
        the complete unit is re-run once in a fresh transaction; a persistent
        lock returns False. The repository never raises application
        exceptions (R2).
        """
        first = self._run_cas_unit(
            form_id=form_id,
            expected_version=expected_version,
            record=record,
            decisions=decisions,
            transitions=transitions,
            derived_certificates=derived_certificates,
            audit=audit,
            review_status=review_status,
            export_status=export_status,
        )
        if first is not None:
            return first
        second = self._run_cas_unit(
            form_id=form_id,
            expected_version=expected_version,
            record=record,
            decisions=decisions,
            transitions=transitions,
            derived_certificates=derived_certificates,
            audit=audit,
            review_status=review_status,
            export_status=export_status,
        )
        return False if second is None else second

    def _run_cas_unit(
        self,
        *,
        form_id: str,
        expected_version: int,
        record: RecordVersion,
        decisions: Sequence[HumanDecision],
        transitions: Sequence[FactTransition],
        derived_certificates: Sequence[tuple[CandidateCertificate, str]],
        audit: AuditEvent,
        review_status: ReviewStatus,
        export_status: ExportStatus | None,
    ) -> bool | None:
        """One transaction; None means database-is-locked (caller retries).

        The engine-level begin() context manager closes the connection on
        every path: success, conflict (early return), and OperationalError.
        """
        try:
            with self._engine.begin() as connection:
                result = connection.execute(
                    update(FormRow)
                    .where(FormRow.form_id == form_id)
                    .where(FormRow.current_record_version == expected_version)
                    .values(current_record_version=expected_version + 1)
                )
                if result.rowcount != 1:
                    return False
                current_export = connection.execute(
                    select(FormRow.export_status).where(
                        FormRow.form_id == form_id
                    )
                ).scalar_one()
                next_export = (
                    export_status
                    if export_status is not None
                    else ExportStatus(current_export)
                )
                connection.execute(
                    insert(RecordVersionRow).values(
                        record_id=record.record_id,
                        form_id=record.form_id,
                        version=record.version,
                        previous_version=record.previous_version,
                        status=record.status.value,
                        values=record.values,
                        change_reason=record.change_reason,
                        confirmed_by=record.confirmed_by,
                        created_at=record.created_at,
                    )
                )
                for certificate, evidence_file_id in derived_certificates:
                    connection.execute(
                        insert(CandidateCertificateRow).values(
                            certificate_id=certificate.certificate_id,
                            candidate_id=certificate.candidate_id,
                            field_key=certificate.field_key,
                            form_id=certificate.target_record_id,
                            field_id=None,
                            evidence_file_id=evidence_file_id,
                            recognition_attempt_id=None,
                            value_payload=certificate.value_payload,
                            evidence_hash=certificate.evidence_hash,
                            evidence_locator=certificate.evidence_locator,
                            template_id=certificate.template_id,
                            template_version=certificate.template_version,
                            source_kind=certificate.source_kind.value,
                            producer_id=certificate.producer_id,
                            producer_version=certificate.producer_version,
                            selection_artifact_id=certificate.selection_artifact_id,
                            confidence=certificate.confidence,
                            selection_state=certificate.selection_state.value,
                            lineage_parent_ids=list(certificate.lineage_parent_ids),
                            target_record_id=certificate.target_record_id,
                            expected_fact_version=certificate.expected_fact_version,
                            created_at=certificate.created_at,
                        )
                    )
                for decision in decisions:
                    connection.execute(
                        insert(HumanDecisionRow).values(
                            decision_id=decision.decision_id,
                            form_id=form_id,
                            candidate_id=decision.candidate_id,
                            field_key=decision.field_key,
                            reviewer_id=decision.reviewer_id,
                            reason=decision.reason,
                            manual_resolution=decision.manual_resolution,
                            decided_at=decision.decided_at,
                        )
                    )
                for transition in transitions:
                    connection.execute(
                        insert(FactTransitionRow).values(
                            transition_id=transition.transition_id,
                            form_id=form_id,
                            created_version=transition.created_version,
                            field_key=transition.field_key,
                            record_id=transition.record_id,
                            record_version_id=record.record_id,
                            decision_id=transition.decision_id,
                            certificate_id=transition.certificate_id,
                            evidence_hash=transition.evidence_sha256,
                            evidence_locator=transition.evidence_locator,
                            producer_id=transition.producer_id,
                            producer_version=transition.producer_version,
                            template_id=transition.template_id,
                            template_version=transition.template_version,
                            source_kind=transition.source_kind.value,
                            created_at=transition.created_at,
                        )
                    )
                connection.execute(
                    insert(AuditEventRow).values(
                        event_id=audit.event_id,
                        form_id=audit.form_id,
                        event_type=audit.event_type,
                        actor_id=audit.actor_id,
                        timestamp=audit.timestamp,
                        before=audit.before,
                        after=audit.after,
                        reason=audit.reason,
                        evidence_ids=list(audit.evidence_ids),
                    )
                )
                connection.execute(
                    update(FormRow)
                    .where(FormRow.form_id == form_id)
                    .values(
                        review_status=review_status.value,
                        export_status=next_export.value,
                    )
                )
            return True
        except OperationalError as error:
            if "database is locked" in str(error):
                return None
            raise

    @staticmethod
    def _to_certificate(row: CandidateCertificateRow) -> CandidateCertificate:
        return CandidateCertificate.from_persisted(
            stored_certificate_id=row.certificate_id,
            candidate_id=row.candidate_id,
            field_key=row.field_key,
            value_payload=row.value_payload,
            evidence_hash=row.evidence_hash,
            evidence_locator=row.evidence_locator,
            template_id=row.template_id,
            template_version=row.template_version,
            source_kind=SourceKind(row.source_kind),
            producer_id=row.producer_id,
            producer_version=row.producer_version,
            selection_artifact_id=row.selection_artifact_id,
            confidence=row.confidence,
            selection_state=SelectionState(row.selection_state),
            lineage_parent_ids=tuple(row.lineage_parent_ids),
            target_record_id=row.target_record_id,
            expected_fact_version=row.expected_fact_version,
            created_at=row.created_at,
        )

    @staticmethod
    def _to_transition(row: FactTransitionRow) -> FactTransition:
        return FactTransition(
            transition_id=row.transition_id,
            record_id=row.record_id,
            field_key=row.field_key,
            created_version=row.created_version,
            record_version_id=row.record_version_id,
            decision_id=row.decision_id,
            certificate_id=row.certificate_id,
            evidence_sha256=row.evidence_hash,
            evidence_locator=row.evidence_locator,
            producer_id=row.producer_id,
            producer_version=row.producer_version,
            source_kind=SourceKind(row.source_kind),
            template_id=row.template_id,
            template_version=row.template_version,
            created_at=row.created_at,
        )
