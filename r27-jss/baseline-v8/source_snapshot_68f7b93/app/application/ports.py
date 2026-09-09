"""Interfaces implemented by infrastructure adapters."""

from collections.abc import Sequence
from pathlib import Path
from typing import BinaryIO, Protocol

from app.domain.authority import CandidateCertificate, FactTransition, HumanDecision
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


class AuthorityRepository(Protocol):
    """Certificate/decision/transition persistence and the atomic units.

    Repository methods return result values (bool conflicts); application
    exceptions are mapped by the application layer (R2).
    """

    def add_certificate(
        self,
        certificate: CandidateCertificate,
        *,
        field_id: str | None,
        evidence_file_id: str,
        recognition_attempt_id: str | None,
    ) -> None: ...
    def get_certificate(self, certificate_id: str) -> CandidateCertificate | None: ...
    def get_certificate_evidence_file_id(self, certificate_id: str) -> str | None: ...
    def get_evidence(self, file_id: str) -> EvidenceFile | None: ...
    def list_certificates_for_form(self, form_id: str) -> list[CandidateCertificate]: ...
    def list_certificates_for_field(
        self, form_id: str, field_key: str, expected_fact_version: int
    ) -> list[CandidateCertificate]: ...
    def add_decision(self, decision: HumanDecision, *, form_id: str) -> None: ...
    def list_decisions_for_form(self, form_id: str) -> list[HumanDecision]: ...
    def add_transition(
        self, transition: FactTransition, *, record_version_id: str
    ) -> None: ...
    def list_transitions_for_version(
        self, form_id: str, created_version: int
    ) -> list[FactTransition]: ...
    def append_candidate_unit(
        self,
        *,
        evidence: EvidenceFile,
        attempt: RecognitionAttempt,
        certificate: CandidateCertificate,
        audit: AuditEvent,
        field_id: str | None = None,
    ) -> None: ...
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
    ) -> bool: ...
