"""Interfaces implemented by infrastructure adapters."""

from collections.abc import Sequence
from pathlib import Path
from typing import BinaryIO, Protocol

from app.domain.authority import (
    AuthorizationBinding,
    CandidateCertificate,
    FactTransition,
    HumanDecision,
)
from app.domain.models import (
    AuditEvent,
    EvidenceFile,
    ExportStatus,
    Form,
    FormField,
    RecognitionAttempt,
    RecordVersion,
    ReviewStatus,
)


class FormRepository(Protocol):
    def add_form(self, form: Form) -> None: ...
    def get_form(self, form_id: str) -> Form | None: ...
    def list_record_versions(self, form_id: str) -> list[RecordVersion]: ...
    def list_form_fields(self, form_id: str) -> list[FormField]: ...
    def set_review_status(self, form_id: str, status: ReviewStatus) -> None: ...
    def set_export_status(self, form_id: str, status: ExportStatus) -> None: ...
    def get_form_field(self, field_id: str) -> FormField | None: ...


class EvidenceRepository(Protocol):
    def add_evidence(self, evidence: EvidenceFile) -> None: ...
    def find_by_sha256(self, sha256: str) -> EvidenceFile | None: ...


class AuditRepository(Protocol):
    def add_audit_event(self, event: AuditEvent) -> None: ...


class EvidenceStorage(Protocol):
    def store(self, source: BinaryIO, suffix: str, category: str) -> tuple[str, Path]: ...


class StoredObject(Protocol):
    @property
    def file_id(self) -> str: ...

    @property
    def uri(self) -> str: ...

    @property
    def sha256(self) -> str: ...


class ImmutableObjectStorage(Protocol):
    """Content-addressed byte storage with compensating deletion on DB failure."""

    def store_bytes(self, content: bytes, suffix: str, category: str) -> StoredObject: ...
    def discard(self, uri: str) -> None: ...


class CandidateWritePort(Protocol):
    """Append machine candidates; deliberately has no fact-write method."""

    def append_candidate_unit(
        self,
        *,
        evidence: EvidenceFile,
        attempt: RecognitionAttempt,
        certificate: CandidateCertificate,
        audit: AuditEvent,
        field_id: str | None = None,
    ) -> None: ...

    def append_candidate_certificate(
        self,
        *,
        evidence: EvidenceFile,
        certificate: CandidateCertificate,
        audit: AuditEvent,
        field_id: str | None = None,
    ) -> None: ...


class AuthorityReadPort(Protocol):
    """Read persisted authority context without any write capability."""

    def get_certificate(self, certificate_id: str) -> CandidateCertificate | None: ...
    def get_certificate_evidence_file_id(self, certificate_id: str) -> str | None: ...
    def get_evidence(self, file_id: str) -> EvidenceFile | None: ...
    def list_certificates_for_field(
        self, form_id: str, field_key: str, expected_fact_version: int
    ) -> list[CandidateCertificate]: ...


class FactAdmissionPort(Protocol):
    """Atomic authoritative commit; deliberately has no component inserts."""

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
    ) -> bool: ...
