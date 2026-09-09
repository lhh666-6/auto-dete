"""Exact SQLite-backed form search and trace use cases."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from app.domain.authority import (
    AuthorizationBinding,
    CandidateCertificate,
    FactTransition,
    HumanDecision,
    TraceHop,
    build_provenance_trace,
    canonical_json,
)
from app.domain.evidence_identity import locator_from_evidence
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
    authorized_value_payload: str | None = None
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
    def list_form_fields(self, form_id: str) -> list[FormField]: ...
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
    def get_fact_transition(self, transition_id: str) -> FactTransition | None: ...
    def list_transitions_for_version(
        self, form_id: str, created_version: int
    ) -> list[FactTransition]: ...
    def list_transitions_for_form(self, form_id: str) -> list[FactTransition]: ...
    def list_decisions_for_form(self, form_id: str) -> list[HumanDecision]: ...
    def get_certificate(self, certificate_id: str) -> CandidateCertificate | None: ...
    def list_certificates_for_form(self, form_id: str) -> list[CandidateCertificate]: ...
    def get_certificate_evidence_file_id(self, certificate_id: str) -> str | None: ...
    def list_certificate_evidence_bindings_for_form(self, form_id: str) -> dict[str, str]: ...
    def get_evidence(self, file_id: str) -> EvidenceFile | None: ...
    def get_certificate_era_start(self) -> datetime | None: ...
    def list_authorization_bindings_for_form(self, form_id: str) -> list[AuthorizationBinding]: ...


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
        """Rebuild the reverse trace from immutable fact_sources.

        For a certificate-era record version, every committed field is traced
        through its fact_sources anchor, even when that anchor points to a
        transition created in an earlier version (copy-forward).  The verifier
        fails closed on:

        - value/source domain mismatches;
        - missing or newer source transitions;
        - missing decision/certificate/evidence/authorization rows;
        - binding certificate mismatch;
        - authorizedValue != transitionValue != committedValue;
        - any producer/evidence/version/timestamp chain failure.
        """
        form = self._repository.get_form(form_id)
        if form is None:
            raise KeyError(f"Unknown form: {form_id}")
        versions = tuple(self._repository.list_record_versions(form_id))
        evidence_rows = tuple(self._repository.list_evidence(form_id))
        evidence_by_id = {evidence.file_id: evidence for evidence in evidence_rows}
        audits = tuple(self._repository.list_audit_events(form_id))
        attempts = tuple(self._repository.list_recognition_attempts_for_form(form_id))
        selected = created_version if created_version is not None else form.current_record_version
        if created_version is not None and not any(
            version.version == created_version for version in versions
        ):
            raise KeyError(f"Unknown version {created_version} for form {form_id}")
        selected_version = next(
            (version for version in versions if version.version == selected), None
        )
        era_start = self._repository.get_certificate_era_start()
        if selected_version is None:
            return self._trace_result(
                form,
                versions,
                evidence=evidence_rows,
                audits=audits,
                attempts=attempts,
                fields=(),
                status="pre-certificate",
            )
        created_at = selected_version.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        if era_start is not None and created_at < era_start:
            return self._trace_result(
                form,
                versions,
                evidence=evidence_rows,
                audits=audits,
                attempts=attempts,
                fields=(),
                status="pre-certificate",
            )

        values = dict(selected_version.values)
        fact_sources = dict(selected_version.fact_sources or {})
        transitions = tuple(self._repository.list_transitions_for_form(form_id))
        transition_by_id = {transition.transition_id: transition for transition in transitions}
        transition_buckets: dict[int, list[FactTransition]] = {}
        for transition in transitions:
            transition_buckets.setdefault(transition.created_version, []).append(transition)
        transitions_by_version = {
            version.version: tuple(transition_buckets.get(version.version, ()))
            for version in versions
        }
        history_failures = self._source_history_failures(
            form_id,
            versions,
            selected_version.version,
            era_start,
            transition_by_id,
            transitions_by_version,
        )
        decisions = {
            decision.decision_id: decision
            for decision in self._repository.list_decisions_for_form(form_id)
        }
        bindings_by_decision: dict[str, AuthorizationBinding] = {}
        if hasattr(self._repository, "list_authorization_bindings_for_form"):
            bindings_by_decision = {
                binding.decision_id: binding
                for binding in self._repository.list_authorization_bindings_for_form(form_id)
            }
        certificates = {
            certificate.certificate_id: certificate
            for certificate in self._repository.list_certificates_for_form(form_id)
        }
        certificate_evidence = self._repository.list_certificate_evidence_bindings_for_form(
            form_id
        )
        entries: list[FieldTraceEntry] = []

        def incomplete(
            field_key: str,
            *,
            failures: tuple[str, ...],
            created_version: int | None = None,
        ) -> FieldTraceEntry:
            # A direct terminal failure is the most specific diagnosis.  Only
            # surface prefix-history failures when the terminal chain itself
            # is otherwise well formed.
            combined_failures = failures or history_failures.get(field_key, ())
            return FieldTraceEntry(
                field_key=field_key,
                status="incomplete",
                created_version=created_version or selected,
                decision_id=None,
                certificate_id=None,
                evidence_file_id=None,
                producer_id=None,
                producer_version=None,
                template_id=None,
                template_version=None,
                source_kind=None,
                evidence_locator=None,
                failures=combined_failures,
            )

        for field_key in sorted(set(values) | set(fact_sources) | set(history_failures)):
            # Domain equality under alpha: no source without a committed value
            # and no committed value without a source.
            if field_key not in values:
                if field_key not in fact_sources:
                    entries.append(
                        incomplete(
                            field_key,
                            failures=history_failures.get(field_key, ()),
                        )
                    )
                    continue
                entries.append(
                    incomplete(
                        field_key,
                        failures=("fact_sources has a field with no committed value",),
                    )
                )
                continue
            if field_key not in fact_sources:
                entries.append(
                    incomplete(
                        field_key,
                        failures=(f"missing anchored source for field {field_key}",),
                    )
                )
                continue

            source_id = fact_sources[field_key]
            source = transition_by_id.get(source_id)
            if source is None:
                entries.append(
                    incomplete(
                        field_key,
                        failures=(f"missing transition for field {field_key}",),
                    )
                )
                continue

            failures = list(history_failures.get(field_key, ()))
            hops: tuple[TraceHop, ...] = ()
            if source.created_version > selected_version.version:
                failures.append("source transition created after selected version")
                failures.append(f"missing transition for field {field_key}")
            if source.record_id != form_id:
                failures.append("source transition record mismatch")
            if source.field_key != field_key:
                failures.append("source transition field mismatch")
            # Verify against the exact record-version row the source created,
            # not the selected (possibly later) version.
            source_version_row = next(
                (version for version in versions if version.version == source.created_version),
                None,
            )
            if source_version_row is None:
                failures.append("record version row for source transition missing")
            elif source_version_row.record_id != source.record_version_id:
                failures.append("transition record-version row mismatch")

            decision = decisions.get(source.decision_id)
            certificate = certificates.get(source.certificate_id)
            evidence_file_id = certificate_evidence.get(source.certificate_id)
            binding = bindings_by_decision.get(source.decision_id)
            if decision is None:
                failures.append("missing decision")
            if certificate is None:
                failures.append("missing certificate")
            if binding is None:
                failures.append("missing authorization binding")
            elif binding.certificate_id != source.certificate_id:
                failures.append("authorization binding certificate mismatch")
            evidence: EvidenceFile | None = None
            if evidence_file_id is None:
                failures.append("missing evidence binding")
            else:
                evidence = evidence_by_id.get(evidence_file_id)
                if evidence is None:
                    failures.append("missing evidence row")

            # AuthorizedValue == TransitionValue == CommittedValue.
            if source.value_payload is None:
                failures.append("source transition value payload missing")
            else:
                if binding is not None and binding.authorized_value_payload != source.value_payload:
                    failures.append("authorization value and transition value mismatch")
                try:
                    committed_payload = canonical_json(values[field_key])
                except Exception:
                    committed_payload = None
                if committed_payload is not None and committed_payload != source.value_payload:
                    failures.append("transition value and committed value mismatch")

            if decision is not None and certificate is not None and evidence is not None:
                persisted_locator = locator_from_evidence(evidence)
                if certificate.evidence_locator != persisted_locator:
                    failures.append("certificate locator and persisted evidence locator mismatch")
                if source.evidence_locator != persisted_locator:
                    failures.append("transition locator and persisted evidence locator mismatch")
                built = build_provenance_trace(source, decision, certificate, evidence.sha256)
                failures.extend(built.failures)
                hops = built.hops
            entries.append(
                FieldTraceEntry(
                    field_key=field_key,
                    status="complete" if not failures else "incomplete",
                    created_version=source.created_version,
                    decision_id=source.decision_id,
                    certificate_id=source.certificate_id,
                    evidence_file_id=evidence_file_id,
                    producer_id=source.producer_id,
                    producer_version=source.producer_version,
                    template_id=source.template_id,
                    template_version=source.template_version,
                    source_kind=source.source_kind.value,
                    evidence_locator=source.evidence_locator,
                    failures=tuple(failures),
                    authorized_value_payload=(
                        binding.authorized_value_payload if binding is not None else None
                    ),
                    hops=hops,
                )
            )
        # An extra transition created in the selected version but not present
        # in the committed snapshot is corruption.  Historical transitions
        # from older versions are normal because fact_sources copy forward.
        selected_transitions = transitions_by_version.get(selected, ())
        for transition in selected_transitions:
            if transition.field_key not in values:
                entries.append(
                    incomplete(
                        transition.field_key,
                        failures=("transition field not present in record values",),
                    )
                )
        fields = tuple(entries)
        status = "complete" if all(entry.status == "complete" for entry in fields) else "incomplete"
        return self._trace_result(
            form,
            versions,
            evidence=evidence_rows,
            audits=audits,
            attempts=attempts,
            fields=fields,
            status=status,
        )

    def _source_history_failures(
        self,
        form_id: str,
        versions: tuple[RecordVersion, ...],
        selected_version: int,
        era_start: datetime | None,
        transition_by_id: dict[str, FactTransition],
        transitions_by_version: dict[int, tuple[FactTransition, ...]],
    ) -> dict[str, tuple[str, ...]]:
        """Validate exact source evolution for every certificate-era prefix row."""

        declared_rows = self._repository.list_form_fields(form_id)
        declared = {field.field_name for field in declared_rows}
        failures: dict[str, list[str]] = {}

        def fail(field_key: str, message: str) -> None:
            bucket = failures.setdefault(field_key, [])
            if message not in bucket:
                bucket.append(message)

        if len(declared_rows) != len(declared):
            fail("<schema>", "declared field names are not unique")
        if not declared:
            fail("<schema>", "form has no declared fields")

        history: list[RecordVersion] = []
        for version in sorted(versions, key=lambda item: item.version):
            if version.version > selected_version:
                continue
            created_at = version.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=UTC)
            if era_start is None or created_at >= era_start:
                history.append(version)
        if not history:
            return {key: tuple(value) for key, value in failures.items()}

        previous: RecordVersion | None = None
        for version in history:
            values = dict(version.values)
            sources = dict(version.fact_sources or {})
            value_fields = set(values)
            source_fields = set(sources)
            for field_key in declared - value_fields:
                fail(field_key, f"version {version.version} missing declared value")
            for field_key in value_fields - declared:
                fail(field_key, f"version {version.version} has undeclared value")
            for field_key in declared - source_fields:
                fail(
                    field_key,
                    f"version {version.version} missing source for declared field",
                )
            for field_key in source_fields - declared:
                fail(field_key, f"version {version.version} has undeclared source")

            if previous is None:
                changed_fields = set(declared)
            else:
                expected_previous = version.version - 1
                if version.previous_version != expected_previous:
                    fail(
                        "<history>",
                        f"version {version.version} previous_version is not contiguous",
                    )
                previous_values = dict(previous.values)
                changed_fields = {
                    field_key
                    for field_key in declared
                    if field_key in values
                    and field_key in previous_values
                    and values[field_key] != previous_values[field_key]
                }
                previous_sources = dict(previous.fact_sources or {})
                for field_key in declared & source_fields & set(previous_sources):
                    if field_key in changed_fields:
                        if sources[field_key] == previous_sources[field_key]:
                            fail(
                                field_key,
                                f"version {version.version} changed field source was reused",
                            )
                    elif sources[field_key] != previous_sources[field_key]:
                        fail(
                            field_key,
                            f"version {version.version} unchanged field source changed",
                        )

            transitions = transitions_by_version.get(version.version, ())
            transition_fields = [transition.field_key for transition in transitions]
            for field_key in set(transition_fields):
                if transition_fields.count(field_key) > 1:
                    fail(
                        field_key,
                        f"version {version.version} has duplicate field transitions",
                    )
            for field_key in changed_fields - set(transition_fields):
                fail(
                    field_key,
                    f"version {version.version} changed field transition missing",
                )
            for field_key in set(transition_fields) - changed_fields:
                fail(
                    field_key,
                    f"version {version.version} unchanged field has transition",
                )
                if field_key not in values:
                    fail(field_key, "transition field not present in record values")

            for field_key in declared & source_fields:
                source = transition_by_id.get(sources[field_key])
                if source is None:
                    fail(
                        field_key,
                        f"version {version.version} anchored source transition missing",
                    )
                    continue
                if source.record_id != form_id:
                    fail(field_key, f"version {version.version} source record mismatch")
                if source.field_key != field_key:
                    fail(field_key, f"version {version.version} source field mismatch")
                if field_key in values and source.value_payload != canonical_json(
                    values[field_key]
                ):
                    fail(
                        field_key,
                        f"version {version.version} source value does not match committed value",
                    )
                source_version_row = next(
                    (item for item in versions if item.version == source.created_version),
                    None,
                )
                if source_version_row is None:
                    fail(
                        field_key,
                        f"version {version.version} source record version is missing",
                    )
                elif source.record_version_id != source_version_row.record_id:
                    fail(
                        field_key,
                        f"version {version.version} source record-version mismatch",
                    )
                if field_key in changed_fields and source.created_version != version.version:
                    fail(
                        field_key,
                        f"version {version.version} changed field source is not new",
                    )
                if source.created_version > version.version:
                    fail(
                        field_key,
                        f"version {version.version} source comes from the future",
                    )

            previous = version

        return {key: tuple(value) for key, value in failures.items()}

    def _trace_result(
        self,
        form: Form,
        versions: tuple[RecordVersion, ...],
        *,
        evidence: tuple[EvidenceFile, ...],
        audits: tuple[AuditEvent, ...],
        attempts: tuple[RecognitionAttempt, ...],
        fields: tuple[FieldTraceEntry, ...],
        status: str,
    ) -> FormTrace:
        return FormTrace(
            form=form,
            versions=versions,
            evidence=evidence,
            audits=audits,
            attempts=attempts,
            fields=fields,
            status=status,
        )
