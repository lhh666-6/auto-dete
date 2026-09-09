"""SQLAlchemy repository implementations."""

from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Engine, event, func, insert, select, update
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.adapters.database.migrations import (
    migrate_schema,
    schema_version,
)
from app.adapters.database.models import (
    AIReviewRow,
    AuditEventRow,
    AuthorityMetaRow,
    AuthorizationBindingRow,
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
from app.domain.admission import derive_admission_plan
from app.domain.authority import (
    AuthorizationBinding,
    CandidateCertificate,
    FactTransition,
    HumanDecision,
    SelectionState,
    SourceKind,
    canonical_json,
)
from app.domain.evidence_identity import canonical_evidence_locator
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
)
from app.domain.principal import (
    FACT_ADMISSION_ROLE,
    PrincipalRolePolicy,
    prototype_principal_policy,
)


def install_sqlite_pragmas(engine: Engine) -> None:
    """Enable foreign keys and a busy timeout on every SQLite connection."""

    @event.listens_for(engine, "connect")
    def _set_pragmas(dbapi_connection: Any, connection_record: Any) -> None:
        del connection_record
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


def check_schema_version(engine: Engine) -> int:
    return schema_version(engine)


def stamp_schema_version(engine: Engine) -> None:
    """Compatibility wrapper around the canonical migration chain."""

    migrate_schema(engine)


class SqlAlchemyFormRepository:
    def __init__(
        self,
        engine: Engine,
        *,
        principal_policy: PrincipalRolePolicy | None = None,
        admission_failpoint: Callable[[str], None] | None = None,
    ) -> None:
        self._engine = engine
        self._principal_policy = principal_policy or prototype_principal_policy()
        self._admission_failpoint = admission_failpoint

    def _hit_admission_failpoint(self, name: str) -> None:
        if self._admission_failpoint is not None:
            self._admission_failpoint(name)

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
                    fact_sources=dict(row.fact_sources or {}),
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

    def list_form_fields(self, form_id: str) -> list[FormField]:
        statement = (
            select(FormFieldRow)
            .where(FormFieldRow.form_id == form_id)
            .order_by(FormFieldRow.field_name, FormFieldRow.field_id)
        )
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [
                FormField(
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
                for row in rows
            ]

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
            fact_sources=dict(row.fact_sources or {}),
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

    def list_certificate_evidence_bindings_for_form(self, form_id: str) -> dict[str, str]:
        """Load certificate-to-evidence bindings for one trace snapshot."""
        statement = (
            select(
                CandidateCertificateRow.certificate_id,
                CandidateCertificateRow.evidence_file_id,
            )
            .where(CandidateCertificateRow.form_id == form_id)
            .order_by(CandidateCertificateRow.certificate_id)
        )
        with Session(self._engine) as session:
            return {
                certificate_id: evidence_id
                for certificate_id, evidence_id in session.execute(statement)
            }

    def list_certificates_for_field(
        self, form_id: str, field_key: str, expected_fact_version: int
    ) -> list[CandidateCertificate]:
        """Certificates eligible for one field at one expected fact version."""
        statement = (
            select(CandidateCertificateRow)
            .where(CandidateCertificateRow.form_id == form_id)
            .where(CandidateCertificateRow.field_key == field_key)
            .where(CandidateCertificateRow.expected_fact_version == expected_fact_version)
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

    def add_authorization_binding(self, binding: AuthorizationBinding, *, form_id: str) -> None:
        with Session(self._engine) as session, session.begin():
            session.add(
                AuthorizationBindingRow(
                    binding_id=binding.binding_id,
                    decision_id=binding.decision_id,
                    certificate_id=binding.certificate_id,
                    authorized_value_payload=binding.authorized_value_payload,
                    bound_at=binding.bound_at,
                )
            )

    def list_authorization_bindings_for_form(self, form_id: str) -> list[AuthorizationBinding]:
        statement = (
            select(AuthorizationBindingRow)
            .join(
                HumanDecisionRow,
                HumanDecisionRow.decision_id == AuthorizationBindingRow.decision_id,
            )
            .where(HumanDecisionRow.form_id == form_id)
            .order_by(
                AuthorizationBindingRow.bound_at,
                AuthorizationBindingRow.binding_id,
            )
        )
        with Session(self._engine) as session:
            rows = session.scalars(statement).all()
            return [
                AuthorizationBinding(
                    binding_id=row.binding_id,
                    decision_id=row.decision_id,
                    certificate_id=row.certificate_id,
                    authorized_value_payload=row.authorized_value_payload,
                    bound_at=row.bound_at,
                )
                for row in rows
            ]

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
                    value_payload=transition.value_payload,
                )
            )

    def get_fact_transition(self, transition_id: str) -> FactTransition | None:
        """Load one fact transition by id (used by source-anchored traces)."""
        with Session(self._engine) as session:
            row = session.get(FactTransitionRow, transition_id)
            return self._to_transition(row) if row is not None else None

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

    def list_transitions_for_form(self, form_id: str) -> list[FactTransition]:
        """Load all form transitions once for reverse-trace indexing."""
        statement = (
            select(FactTransitionRow)
            .where(FactTransitionRow.form_id == form_id)
            .order_by(
                FactTransitionRow.created_version,
                FactTransitionRow.field_key,
                FactTransitionRow.transition_id,
            )
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
                    select(FormFieldRow.form_id).where(FormFieldRow.field_id == field_id)
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

    def append_candidate_certificate(
        self,
        *,
        evidence: EvidenceFile,
        certificate: CandidateCertificate,
        audit: AuditEvent,
        field_id: str | None = None,
    ) -> None:
        """Persist non-recognition evidence + candidate certificate + audit atomically."""
        with self._engine.connect() as connection, connection.begin():
            if evidence.form_id != certificate.target_record_id:
                raise ValueError("evidence and certificate belong to different forms")
            if evidence.sha256 != certificate.evidence_hash:
                raise ValueError("evidence hash does not match certificate")
            if field_id is not None:
                field = connection.execute(
                    select(FormFieldRow.form_id, FormFieldRow.field_name).where(
                        FormFieldRow.field_id == field_id
                    )
                ).one_or_none()
                if field is None:
                    raise ValueError(f"unknown field: {field_id}")
                if field.form_id != certificate.target_record_id:
                    raise ValueError(
                        f"field {field_id} belongs to form {field.form_id}, "
                        f"not {certificate.target_record_id}"
                    )
                if field.field_name != certificate.field_key:
                    raise ValueError(
                        f"field {field_id} is {field.field_name}, not {certificate.field_key}"
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
                insert(CandidateCertificateRow).values(
                    certificate_id=certificate.certificate_id,
                    candidate_id=certificate.candidate_id,
                    field_key=certificate.field_key,
                    form_id=certificate.target_record_id,
                    field_id=field_id,
                    evidence_file_id=evidence.file_id,
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

    @staticmethod
    def _validate_fact_admission_bundle(
        *,
        form_id: str,
        expected_version: int,
        record: RecordVersion,
        decisions: Sequence[HumanDecision],
        transitions: Sequence[FactTransition],
        authorization_bindings: Sequence[AuthorizationBinding],
    ) -> None:
        """Fail closed on incomplete or inconsistent trusted admission bundles.

        A low-level caller must not be able to commit an authoritative fact
        transition without one immutable AuthorizationBinding per decision,
        with certificate identity and authorized-value payload aligned to the
        transition.  This is the executable counterpart of the formal
        C-record/C-fresh/C-auth-cert/C-auth-value admission contract.
        """
        errors: list[str] = []
        if not transitions:
            errors.append("at least one fact transition is required")
        if not authorization_bindings:
            errors.append("authorization_bindings must not be empty")
        transition_ids = [t.transition_id for t in transitions]
        if len(transition_ids) != len(set(transition_ids)):
            errors.append("transition ids must be unique")
        decision_ids = [d.decision_id for d in decisions]
        if len(decision_ids) != len(set(decision_ids)):
            errors.append("decision ids must be unique")
        transition_decision_ids = [t.decision_id for t in transitions]
        binding_decision_ids = [b.decision_id for b in authorization_bindings]
        if set(transition_decision_ids) != set(decision_ids):
            errors.append("transition/decision sets must match one-to-one")
        if set(binding_decision_ids) != set(decision_ids):
            errors.append("binding/decision sets must match one-to-one")
        if len(binding_decision_ids) != len(set(binding_decision_ids)):
            errors.append("more than one binding per decision is not allowed")
        bindings_by_decision = {b.decision_id: b for b in authorization_bindings}
        for transition in transitions:
            if transition.record_id != form_id:
                errors.append(f"transition {transition.transition_id} record mismatch")
            if transition.created_version != expected_version + 1:
                errors.append(f"transition {transition.transition_id} version mismatch")
            if transition.record_version_id != record.record_id:
                errors.append(f"transition {transition.transition_id} record_version_id mismatch")
            if transition.field_key not in record.values:
                errors.append(
                    f"transition {transition.transition_id} field not in committed snapshot"
                )
            if transition.value_payload is None:
                errors.append(f"transition {transition.transition_id} has no value payload")
            binding = bindings_by_decision.get(transition.decision_id)
            if binding is None:
                errors.append(f"transition {transition.transition_id} has no authorization binding")
                continue
            if binding.certificate_id != transition.certificate_id:
                errors.append(
                    f"binding/transition certificate mismatch for {transition.transition_id}"
                )
            if binding.authorized_value_payload != transition.value_payload:
                errors.append(
                    f"binding/transition authorized value mismatch for {transition.transition_id}"
                )
        if errors:
            raise ValueError("invalid fact admission bundle: " + "; ".join(errors))

    def append_fact_transition(
        self,
        *,
        form_id: str,
        expected_version: int,
        record: RecordVersion,
        decisions: Sequence[HumanDecision],
        transitions: Sequence[FactTransition],
        derived_certificates: Sequence[tuple[CandidateCertificate, str]],
        authorization_bindings: Sequence[AuthorizationBinding],
        audit: AuditEvent,
        review_status: ReviewStatus,
        export_status: ExportStatus | None,
    ) -> bool:
        """Atomic CAS-protected fact transition; returns a conflict result.

        The version CAS is the first write of the transaction. A database lock
        is reported as a failed admission without an implicit retry; callers
        may choose an explicit retry policy outside the authority boundary.
        """
        self._validate_fact_admission_bundle(
            form_id=form_id,
            expected_version=expected_version,
            record=record,
            decisions=decisions,
            transitions=transitions,
            authorization_bindings=authorization_bindings,
        )
        outcome = self._run_cas_unit(
            form_id=form_id,
            expected_version=expected_version,
            record=record,
            decisions=decisions,
            transitions=transitions,
            derived_certificates=derived_certificates,
            authorization_bindings=authorization_bindings,
            audit=audit,
            review_status=review_status,
            export_status=export_status,
        )
        return False if outcome is None else outcome

    @staticmethod
    def _validate_persisted_admission_shape(
        connection: Any,
        *,
        form_id: str,
        expected_version: int,
        record: RecordVersion,
        decisions: Sequence[HumanDecision],
        transitions: Sequence[FactTransition],
        derived_certificates: Sequence[tuple[CandidateCertificate, str]],
    ) -> None:
        """Re-derive the admission field set from trusted persisted state."""

        if record.form_id != form_id:
            raise ValueError("record form does not match admission form")
        if record.version != expected_version + 1:
            raise ValueError("record version is not the attempted successor")
        expected_previous = expected_version or None
        if record.previous_version != expected_previous:
            raise ValueError("record previous_version does not match expected version")

        declared_rows = (
            connection.execute(
                select(FormFieldRow.field_name).where(FormFieldRow.form_id == form_id)
            )
            .scalars()
            .all()
        )
        declared_fields = frozenset(declared_rows)
        if len(declared_rows) != len(declared_fields):
            raise ValueError("declared field names must be unique per form")

        previous_values: dict[str, Any] = {}
        previous_sources: dict[str, str] = {}
        if expected_version > 0:
            previous = connection.execute(
                select(RecordVersionRow.values, RecordVersionRow.fact_sources).where(
                    RecordVersionRow.form_id == form_id,
                    RecordVersionRow.version == expected_version,
                )
            ).one_or_none()
            if previous is None:
                raise ValueError("expected persisted predecessor is missing")
            previous_values = dict(previous.values)
            previous_sources = dict(previous.fact_sources or {})

        plan = derive_admission_plan(
            declared_fields=declared_fields,
            previous_values=previous_values,
            previous_fact_sources=previous_sources,
            proposed_values=record.values,
        )
        if plan.complete_values != record.values:
            raise ValueError("record is not the exact derived complete snapshot")

        transition_fields = [transition.field_key for transition in transitions]
        if len(transition_fields) != len(set(transition_fields)):
            raise ValueError("more than one transition per admitted field")
        if frozenset(transition_fields) != plan.admission_fields:
            raise ValueError("transition fields do not equal the exact changed/initial field set")
        decision_by_id = {decision.decision_id: decision for decision in decisions}
        derived_by_id = {
            certificate.certificate_id: certificate for certificate, _ in derived_certificates
        }
        derived_evidence_by_id = {
            certificate.certificate_id: evidence_id
            for certificate, evidence_id in derived_certificates
        }
        for transition in transitions:
            if transition.value_payload != canonical_json(record.values[transition.field_key]):
                raise ValueError(
                    f"transition {transition.transition_id} value does not equal "
                    "the committed value"
                )
            decision = decision_by_id[transition.decision_id]
            if decision.field_key != transition.field_key:
                raise ValueError(f"decision field mismatch for {transition.transition_id}")
            if decision.reviewer_id != record.confirmed_by:
                raise ValueError(f"decision principal mismatch for {transition.transition_id}")
            certificate = derived_by_id.get(transition.certificate_id)
            if certificate is None:
                persisted_certificate = (
                    connection.execute(
                        select(
                            CandidateCertificateRow.candidate_id,
                            CandidateCertificateRow.field_key,
                            CandidateCertificateRow.target_record_id,
                            CandidateCertificateRow.expected_fact_version,
                            CandidateCertificateRow.evidence_file_id,
                            CandidateCertificateRow.evidence_hash,
                            CandidateCertificateRow.evidence_locator,
                            CandidateCertificateRow.producer_id,
                            CandidateCertificateRow.producer_version,
                            CandidateCertificateRow.template_id,
                            CandidateCertificateRow.template_version,
                            CandidateCertificateRow.source_kind,
                        ).where(CandidateCertificateRow.certificate_id == transition.certificate_id)
                    )
                    .mappings()
                    .one_or_none()
                )
                if persisted_certificate is None:
                    raise ValueError(f"missing certificate for {transition.transition_id}")
                candidate_id = persisted_certificate["candidate_id"]
                certificate_field = persisted_certificate["field_key"]
                certificate_record = persisted_certificate["target_record_id"]
                certificate_version = persisted_certificate["expected_fact_version"]
                evidence_file_id = persisted_certificate["evidence_file_id"]
                certificate_evidence_hash = persisted_certificate["evidence_hash"]
                certificate_locator = persisted_certificate["evidence_locator"]
                certificate_producer_id = persisted_certificate["producer_id"]
                certificate_producer_version = persisted_certificate["producer_version"]
                certificate_template_id = persisted_certificate["template_id"]
                certificate_template_version = persisted_certificate["template_version"]
                certificate_source_kind = persisted_certificate["source_kind"]
            else:
                candidate_id = certificate.candidate_id
                certificate_field = certificate.field_key
                certificate_record = certificate.target_record_id
                certificate_version = certificate.expected_fact_version
                evidence_file_id = derived_evidence_by_id[certificate.certificate_id]
                certificate_evidence_hash = certificate.evidence_hash
                certificate_locator = certificate.evidence_locator
                certificate_producer_id = certificate.producer_id
                certificate_producer_version = certificate.producer_version
                certificate_template_id = certificate.template_id
                certificate_template_version = certificate.template_version
                certificate_source_kind = certificate.source_kind.value
            if decision.candidate_id != candidate_id:
                raise ValueError(f"decision candidate mismatch for {transition.transition_id}")
            if certificate_field != transition.field_key:
                raise ValueError(f"certificate field mismatch for {transition.transition_id}")
            if certificate_record != form_id:
                raise ValueError(f"certificate record mismatch for {transition.transition_id}")
            if certificate_version != expected_version:
                raise ValueError(f"certificate version mismatch for {transition.transition_id}")
            evidence = (
                connection.execute(
                    select(
                        EvidenceFileRow.form_id,
                        EvidenceFileRow.related_field_id,
                        EvidenceFileRow.uri,
                        EvidenceFileRow.sha256,
                    ).where(EvidenceFileRow.file_id == evidence_file_id)
                )
                .mappings()
                .one_or_none()
            )
            if evidence is None:
                raise ValueError(f"missing evidence for {transition.transition_id}")
            persisted_locator = canonical_evidence_locator(
                form_id=evidence["form_id"],
                related_field_id=evidence["related_field_id"],
                uri=evidence["uri"],
            )
            if evidence["form_id"] != form_id:
                raise ValueError(f"evidence record mismatch for {transition.transition_id}")
            if evidence["sha256"] != certificate_evidence_hash:
                raise ValueError(
                    f"certificate evidence hash mismatch for {transition.transition_id}"
                )
            if certificate_locator != persisted_locator:
                raise ValueError(
                    f"certificate evidence locator mismatch for {transition.transition_id}"
                )
            if transition.evidence_sha256 != evidence["sha256"]:
                raise ValueError(
                    f"transition evidence hash mismatch for {transition.transition_id}"
                )
            if transition.evidence_locator != persisted_locator:
                raise ValueError(
                    f"transition evidence locator mismatch for {transition.transition_id}"
                )
            if transition.producer_id != certificate_producer_id:
                raise ValueError(f"transition producer mismatch for {transition.transition_id}")
            if transition.producer_version != certificate_producer_version:
                raise ValueError(
                    f"transition producer version mismatch for {transition.transition_id}"
                )
            if transition.template_id != certificate_template_id:
                raise ValueError(f"transition template mismatch for {transition.transition_id}")
            if transition.template_version != certificate_template_version:
                raise ValueError(
                    f"transition template version mismatch for {transition.transition_id}"
                )
            if transition.source_kind.value != certificate_source_kind:
                raise ValueError(f"transition source kind mismatch for {transition.transition_id}")

    def _run_cas_unit(
        self,
        *,
        form_id: str,
        expected_version: int,
        record: RecordVersion,
        decisions: Sequence[HumanDecision],
        transitions: Sequence[FactTransition],
        derived_certificates: Sequence[tuple[CandidateCertificate, str]],
        authorization_bindings: Sequence[AuthorizationBinding],
        audit: AuditEvent,
        review_status: ReviewStatus,
        export_status: ExportStatus | None,
    ) -> bool | None:
        """One transaction; None means database-is-locked (no implicit retry).

        The engine-level begin() context manager closes the connection on
        every path: success, conflict (early return), and OperationalError.
        """
        self._validate_fact_admission_bundle(
            form_id=form_id,
            expected_version=expected_version,
            record=record,
            decisions=decisions,
            transitions=transitions,
            authorization_bindings=authorization_bindings,
        )
        try:
            with self._engine.begin() as connection:
                # Host authentication is external, but the authoritative
                # adapter independently rechecks the configured role inside
                # this transaction before the CAS or any other write.
                self._principal_policy.require(record.confirmed_by, FACT_ADMISSION_ROLE)
                self._hit_admission_failpoint("before_cas")
                result = connection.execute(
                    update(FormRow)
                    .where(FormRow.form_id == form_id)
                    .where(FormRow.current_record_version == expected_version)
                    .values(current_record_version=expected_version + 1)
                )
                if result.rowcount != 1:
                    return False
                self._hit_admission_failpoint("after_cas")
                self._validate_persisted_admission_shape(
                    connection,
                    form_id=form_id,
                    expected_version=expected_version,
                    record=record,
                    decisions=decisions,
                    transitions=transitions,
                    derived_certificates=derived_certificates,
                )
                current_export = connection.execute(
                    select(FormRow.export_status).where(FormRow.form_id == form_id)
                ).scalar_one()
                next_export = (
                    export_status if export_status is not None else ExportStatus(current_export)
                )
                previous_fact_sources: dict[str, str] = {}
                if expected_version > 0:
                    previous_row = connection.execute(
                        select(RecordVersionRow.fact_sources).where(
                            RecordVersionRow.form_id == form_id,
                            RecordVersionRow.version == expected_version,
                        )
                    ).scalar_one_or_none()
                    if previous_row:
                        previous_fact_sources = dict(previous_row)
                fact_sources: dict[str, str] = dict(previous_fact_sources)
                for transition in transitions:
                    fact_sources[transition.field_key] = transition.transition_id
                if set(record.values) != set(fact_sources):
                    raise ValueError(
                        "committed values and fact_sources must have identical "
                        "field domains under alpha"
                    )
                self._hit_admission_failpoint("before_record_version")
                connection.execute(
                    insert(RecordVersionRow).values(
                        record_id=record.record_id,
                        form_id=record.form_id,
                        version=record.version,
                        previous_version=record.previous_version,
                        status=record.status.value,
                        values=record.values,
                        fact_sources=fact_sources,
                        change_reason=record.change_reason,
                        confirmed_by=record.confirmed_by,
                        created_at=record.created_at,
                    )
                )
                for certificate, evidence_file_id in derived_certificates:
                    self._hit_admission_failpoint("before_derived_certificate")
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
                    self._hit_admission_failpoint("before_decision")
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
                for binding in authorization_bindings:
                    self._hit_admission_failpoint("before_binding")
                    connection.execute(
                        insert(AuthorizationBindingRow).values(
                            binding_id=binding.binding_id,
                            decision_id=binding.decision_id,
                            certificate_id=binding.certificate_id,
                            authorized_value_payload=binding.authorized_value_payload,
                            bound_at=binding.bound_at,
                        )
                    )
                for transition in transitions:
                    self._hit_admission_failpoint("before_transition")
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
                            value_payload=transition.value_payload,
                        )
                    )
                self._hit_admission_failpoint("before_audit")
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
                self._hit_admission_failpoint("before_status")
                connection.execute(
                    update(FormRow)
                    .where(FormRow.form_id == form_id)
                    .values(
                        review_status=review_status.value,
                        export_status=next_export.value,
                    )
                )
                self._hit_admission_failpoint("before_commit")
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
            value_payload=row.value_payload,
            created_at=row.created_at,
        )
