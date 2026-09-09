"""Narrow runtime facades for disjoint authority capabilities."""

from collections.abc import Sequence

from app.application.ports import (
    AuthorityReadPort,
    CandidateWritePort,
    FactAdmissionPort,
)
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
    RecognitionAttempt,
    RecordVersion,
    ReviewStatus,
)


class CandidateWriteFacade:
    """Expose only the atomic candidate append operation."""

    __slots__ = ("_target",)

    def __init__(self, target: CandidateWritePort) -> None:
        self._target = target

    def append_candidate_unit(
        self,
        *,
        evidence: EvidenceFile,
        attempt: RecognitionAttempt,
        certificate: CandidateCertificate,
        audit: AuditEvent,
        field_id: str | None = None,
    ) -> None:
        self._target.append_candidate_unit(
            evidence=evidence,
            attempt=attempt,
            certificate=certificate,
            audit=audit,
            field_id=field_id,
        )

    def append_candidate_certificate(
        self,
        *,
        evidence: EvidenceFile,
        certificate: CandidateCertificate,
        audit: AuditEvent,
        field_id: str | None = None,
    ) -> None:
        self._target.append_candidate_certificate(
            evidence=evidence,
            certificate=certificate,
            audit=audit,
            field_id=field_id,
        )


class AuthorityReadFacade:
    """Expose the reviewer's persisted authority reads and nothing else."""

    __slots__ = ("_target",)

    def __init__(self, target: AuthorityReadPort) -> None:
        self._target = target

    def get_certificate(self, certificate_id: str) -> CandidateCertificate | None:
        return self._target.get_certificate(certificate_id)

    def get_certificate_evidence_file_id(self, certificate_id: str) -> str | None:
        return self._target.get_certificate_evidence_file_id(certificate_id)

    def get_evidence(self, file_id: str) -> EvidenceFile | None:
        return self._target.get_evidence(file_id)

    def list_certificates_for_field(
        self, form_id: str, field_key: str, expected_fact_version: int
    ) -> list[CandidateCertificate]:
        return self._target.list_certificates_for_field(form_id, field_key, expected_fact_version)


class FactAdmissionFacade:
    """Expose one batch fact admission operation and no component writes."""

    __slots__ = ("_target",)

    def __init__(self, target: FactAdmissionPort) -> None:
        self._target = target

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
        return self._target.append_fact_transition(
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
