"""Exact SQLite-backed form search and trace use cases."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from app.domain.authority import (
    CandidateCertificate,
    FactTransition,
    HumanDecision,
    TraceHop,
    build_provenance_trace,
)
from app.domain.models import (
    AuditEvent,
    EvidenceFile,
    ExportStatus,
    Form,
    RecognitionAttempt,
    RecordVersion,
    ReviewStatus,
)


@dataclass(frozen=True, slots=True)
class FormFilters:
    form_id: str | None = None
    employee_id: str | None = None
    work_order_id: str | None = None
    review_status: ReviewStatus | None = None
    export_status: ExportStatus | None = None


@dataclass(frozen=True, slots=True)
class SearchResult:
    form: Form
    current_record: RecordVersion


@dataclass(frozen=True, slots=True)
class FieldTraceEntry:
    """Authority trace of one fact field (F -> H -> C -> E).

    hops are the verified chain references produced by the domain trace
    builder (empty when the chain could not be rebuilt, e.g. a missing
    decision or certificate row).
    """

    field_key: str
    status: str  # complete | incomplete
    created_version: int
    decision_id: str | None
    certificate_id: str | None
    evidence_file_id: str | None
    producer_id: str | None
    producer_version: str | None
    template_id: str | None
    template_version: str | None
    source_kind: str | None
    evidence_locator: str | None
    failures: tuple[str, ...]
    hops: tuple[TraceHop, ...] = ()


@dataclass(frozen=True, slots=True)
class FormTrace:
    """Reverse trace of one form; authority status per selected version."""

    form: Form
    versions: tuple[RecordVersion, ...]
    evidence: tuple[EvidenceFile, ...]
    audits: tuple[AuditEvent, ...]
    attempts: tuple[RecognitionAttempt, ...]
    fields: tuple[FieldTraceEntry, ...] = ()
    status: str = "pre-certificate"  # complete | incomplete | pre-certificate


class QueryRepository(Protocol):
    def get_form(self, form_id: str) -> Form | None: ...
    def list_record_versions(self, form_id: str) -> list[RecordVersion]: ...
    def list_evidence(self, form_id: str) -> list[EvidenceFile]: ...
    def list_audit_events(self, form_id: str) -> list[AuditEvent]: ...
    def list_recognition_attempts_for_form(self, form_id: str) -> list[RecognitionAttempt]: ...
    def search_current(
        self,
        *,
        form_id: str | None = None,
        employee_id: str | None = None,
        work_order_id: str | None = None,
        review_status: ReviewStatus | None = None,
        export_status: ExportStatus | None = None,
    ) -> list[tuple[Form, RecordVersion]]: ...
    def list_transitions_for_version(
        self, form_id: str, created_version: int
    ) -> list[FactTransition]: ...
    def list_decisions_for_form(self, form_id: str) -> list[HumanDecision]: ...
    def get_certificate(self, certificate_id: str) -> CandidateCertificate | None: ...
    def get_certificate_evidence_file_id(self, certificate_id: str) -> str | None: ...
    def get_evidence(self, file_id: str) -> EvidenceFile | None: ...
    def get_certificate_era_start(self) -> datetime | None: ...


class QueryForms:
    def __init__(self, repository: QueryRepository) -> None:
        self._repository = repository

    def search(self, filters: FormFilters) -> list[SearchResult]:
        rows = self._repository.search_current(
            form_id=filters.form_id,
            employee_id=filters.employee_id,
            work_order_id=filters.work_order_id,
            review_status=filters.review_status,
            export_status=filters.export_status,
        )
        return [SearchResult(form, record) for form, record in rows]

    def trace(self, form_id: str, created_version: int | None = None) -> FormTrace:
        """Rebuild the reverse trace; authority status per selected version.

        Single-argument calls stay compatible: without created_version the
        latest version is evaluated. Every field chain is rebuilt through the
        domain trace builder (F -> H -> C -> E) with all duplicated bindings
        re-verified from the database.

        pre-certificate is reserved for genuine legacy versions — record rows
        created strictly before the certificate era — and for versions that do
        not exist yet (nothing to trace). A certificate-era record version
        must satisfy the exact field-set equality (transition field keys ==
        record value keys); missing, extra, blank, or duplicate fields make
        the version incomplete with explicit per-field failures.
        """
        form = self._repository.get_form(form_id)
        if form is None:
            raise KeyError(f"Unknown form: {form_id}")
        versions = tuple(self._repository.list_record_versions(form_id))
        selected = (
            created_version if created_version is not None else form.current_record_version
        )
        if created_version is not None and not any(
            version.version == created_version for version in versions
        ):
            raise KeyError(f"Unknown version {created_version} for form {form_id}")
        selected_version = next(
            (version for version in versions if version.version == selected), None
        )
        transitions = tuple(
            self._repository.list_transitions_for_version(form_id, selected)
        )
        if selected_version is None or not transitions:
            # Nothing to trace. Distinguish the genuine legacy bucket (record
            # row created before the certificate era) from certificate-era
            # corruption (a record row whose transitions were deleted).
            era_start = self._repository.get_certificate_era_start()
            created_at = selected_version.created_at if selected_version is not None else None
            if created_at is not None and created_at.tzinfo is None:
                # record_versions.created_at uses DateTime(timezone=True),
                # which reads back naive UTC; normalize before comparing.
                created_at = created_at.replace(tzinfo=UTC)
            if selected_version is None or (
                era_start is not None and created_at is not None and created_at < era_start
            ):
                return self._trace_result(
                    form, versions, fields=(), status="pre-certificate"
                )
            corrupt_entries = tuple(
                FieldTraceEntry(
                    field_key=field_key,
                    status="incomplete",
                    created_version=selected,
                    decision_id=None,
                    certificate_id=None,
                    evidence_file_id=None,
                    producer_id=None,
                    producer_version=None,
                    template_id=None,
                    template_version=None,
                    source_kind=None,
                    evidence_locator=None,
                    failures=(f"missing transition for field {field_key}",),
                )
                for field_key in sorted(selected_version.values)
            )
            return self._trace_result(
                form, versions, fields=corrupt_entries, status="incomplete"
            )
        value_keys = set(selected_version.values)
        transition_keys = {transition.field_key for transition in transitions}
        missing_fields = sorted(value_keys - transition_keys)
        extra_fields = sorted(transition_keys - value_keys)
        decisions = {
            decision.decision_id: decision
            for decision in self._repository.list_decisions_for_form(form_id)
        }
        entries: list[FieldTraceEntry] = []
        for transition in transitions:
            failures: list[str] = []
            hops: tuple[TraceHop, ...] = ()
            decision = decisions.get(transition.decision_id)
            certificate = self._repository.get_certificate(
                transition.certificate_id
            )
            evidence_file_id = self._repository.get_certificate_evidence_file_id(
                transition.certificate_id
            )
            if decision is None:
                failures.append("missing decision")
            if certificate is None:
                failures.append("missing certificate")
            evidence: EvidenceFile | None = None
            if evidence_file_id is None:
                failures.append("missing evidence binding")
            else:
                evidence = self._repository.get_evidence(evidence_file_id)
                if evidence is None:
                    failures.append("missing evidence row")
            if not any(
                version.version == transition.created_version for version in versions
            ):
                failures.append("record version row missing")
            # The FK proves only that SOME record-version row exists; the
            # transition must point at the exact row of this (form, version).
            if transition.record_version_id != selected_version.record_id:
                failures.append("transition record-version row mismatch")
            if transition.field_key in extra_fields:
                failures.append("transition field not present in record values")
            if (
                decision is not None
                and certificate is not None
                and evidence is not None
            ):
                built = build_provenance_trace(
                    transition, decision, certificate, evidence.sha256
                )
                failures.extend(built.failures)
                hops = built.hops
            entries.append(
                FieldTraceEntry(
                    field_key=transition.field_key,
                    status="complete" if not failures else "incomplete",
                    created_version=transition.created_version,
                    decision_id=transition.decision_id,
                    certificate_id=transition.certificate_id,
                    evidence_file_id=evidence_file_id,
                    producer_id=transition.producer_id,
                    producer_version=transition.producer_version,
                    template_id=transition.template_id,
                    template_version=transition.template_version,
                    source_kind=transition.source_kind.value,
                    evidence_locator=transition.evidence_locator,
                    failures=tuple(failures),
                    hops=hops,
                )
            )
        for field_key in missing_fields:
            entries.append(
                FieldTraceEntry(
                    field_key=field_key,
                    status="incomplete",
                    created_version=selected,
                    decision_id=None,
                    certificate_id=None,
                    evidence_file_id=None,
                    producer_id=None,
                    producer_version=None,
                    template_id=None,
                    template_version=None,
                    source_kind=None,
                    evidence_locator=None,
                    failures=(f"missing transition for field {field_key}",),
                )
            )
        fields = tuple(entries)
        status = "complete" if all(
            entry.status == "complete" for entry in fields
        ) else "incomplete"
        return self._trace_result(form, versions, fields=fields, status=status)

    def _trace_result(
        self,
        form: Form,
        versions: tuple[RecordVersion, ...],
        *,
        fields: tuple[FieldTraceEntry, ...],
        status: str,
    ) -> FormTrace:
        return FormTrace(
            form=form,
            versions=versions,
            evidence=tuple(self._repository.list_evidence(form.form_id)),
            audits=tuple(self._repository.list_audit_events(form.form_id)),
            attempts=tuple(
                self._repository.list_recognition_attempts_for_form(form.form_id)
            ),
            fields=fields,
            status=status,
        )
