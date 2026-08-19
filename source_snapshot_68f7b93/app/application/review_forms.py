"""Evidence-bound human confirmation and correction use cases.

confirm() is the only fact-writing path: a fact version exists only when an
attributable human decision, a valid DB-loaded certificate per field, and the
current fact version are all present. Everything (record version, per-field
decisions and transitions, derived manual-entry certificates, audit) commits
in one CAS-protected transaction or not at all.
"""

from collections.abc import Mapping, Sequence
from datetime import timedelta
from uuid import uuid4

from app.application.ports import (
    AuditRepository,
    AuthorityRepository,
    FormRepository,
)
from app.domain.authority import (
    AuthorityContext,
    CandidateCertificate,
    CertificateFailure,
    FactTransition,
    HumanDecision,
    IntegrityKind,
    SelectionState,
    SourceKind,
    TransitionAttempt,
    canonical_json,
    validate_certificate,
    verify_transition_authorization,
)
from app.domain.models import (
    AuditEvent,
    ExportStatus,
    RecordStatus,
    RecordVersion,
    ReviewStatus,
    utc_now,
)

# Every candidate source is supported by the application.
KNOWN_SOURCES = frozenset(
    {
        SourceKind.RECOGNITION,
        SourceKind.RETRIEVAL,
        SourceKind.AI_SUGGESTION,
        SourceKind.MANUAL_ENTRY,
    }
)
# Certificate freshness policy: older candidates require reacquisition.
MAX_CERTIFICATE_AGE = timedelta(hours=1)


class ConcurrentReviewError(RuntimeError):
    pass


class AuthorityRejectionError(ValueError):
    """A confirm attempt failed the authority contract; nothing was persisted."""

    def __init__(self, failures: Sequence[CertificateFailure]) -> None:
        self.failures = tuple(failures)
        codes = ", ".join(failure.code for failure in failures)
        super().__init__(f"authority rejection: {codes}")


def _rejection(code: str, message: str) -> CertificateFailure:
    return CertificateFailure(code, IntegrityKind.IDENTITY, message)


class ReviewForms:
    def __init__(
        self,
        forms: FormRepository,
        audits: AuditRepository,
        *,
        known_producers: frozenset[tuple[str, str]],
        known_selection_artifacts: frozenset[str],
    ) -> None:
        self._forms = forms
        self._audits = audits
        self._authority: AuthorityRepository = forms  # type: ignore[assignment]
        self._known_producers = known_producers
        self._known_selection_artifacts = known_selection_artifacts

    def confirm(
        self,
        form_id: str,
        expected_version: int,
        values: Mapping[str, object],
        actor_id: str,
        reason: str,
        *,
        certificate_ids_by_field: Mapping[str, str | None],
        manual_evidence_ids_by_field: Mapping[str, str],
    ) -> RecordVersion:
        """Confirm one form version under the authority contract.

        Callers never construct certificates: certificate_ids_by_field
        references persisted certificates loaded from the database; None
        marks the explicit manual-entry path (evidence id required).
        """
        form = self._forms.get_form(form_id)
        if form is None:
            raise KeyError(f"Unknown form: {form_id}")
        self._check_input_invariants(
            values, certificate_ids_by_field, manual_evidence_ids_by_field
        )
        if form.current_record_version != expected_version:
            raise ConcurrentReviewError(
                f"Expected version {expected_version}, current is "
                f"{form.current_record_version}"
            )
        now = utc_now()

        evidence_hash_by_id = self._resolve_manual_evidence(
            form_id, set(manual_evidence_ids_by_field.values())
        )
        # The record row is created before the per-field loop so every
        # transition can be bound to the exact record_version_id it will
        # create (P0: the trace verifies that binding).
        record = RecordVersion(
            record_id=f"REC-{uuid4().hex}",
            form_id=form_id,
            version=expected_version + 1,
            previous_version=expected_version or None,
            status=RecordStatus.CONFIRMED if expected_version == 0 else RecordStatus.CORRECTED,
            values=dict(values),
            change_reason=reason,
            confirmed_by=actor_id,
            created_at=now,
        )
        decisions: list[HumanDecision] = []
        transitions: list[FactTransition] = []
        derived_certificates: list[tuple[CandidateCertificate, str]] = []
        final_evidence_file_ids: list[str] = []
        known_parents: dict[str, CandidateCertificate] = {}
        for field_key in sorted(values):
            cert_id = certificate_ids_by_field[field_key]
            manual_resolution = False
            if cert_id is None:
                evidence_id = manual_evidence_ids_by_field[field_key]
                certificate = CandidateCertificate.from_manual_entry(
                    candidate_id=f"manual-{uuid4().hex}",
                    field_key=field_key,
                    value=values[field_key],
                    form_id=form_id,
                    evidence_hash=evidence_hash_by_id[evidence_id],
                    evidence_locator=f"{form_id}/manual/{field_key}",
                    template_id=form.template_id,
                    template_version=form.template_version,
                    target_record_id=form_id,
                    expected_fact_version=expected_version,
                    created_at=now,
                )
                evidence_file_id = evidence_id
                # New certificates created at confirm time (manual entry or
                # derived from a modified machine value) persist with the
                # fact in the same transaction.
                derived_certificates.append((certificate, evidence_file_id))
            else:
                loaded = self._authority.get_certificate(cert_id)
                if loaded is None:
                    raise AuthorityRejectionError(
                        [_rejection("UNKNOWN_CERTIFICATE", f"unknown certificate {cert_id}")]
                    )
                if loaded.field_key != field_key:
                    # P0: a certificate is bound to exactly one field; a
                    # cross-field substitution must reject before any write.
                    raise AuthorityRejectionError(
                        [_rejection(
                            "FIELD_KEY_BINDING_MISMATCH",
                            f"certificate {cert_id} is bound to field "
                            f"{loaded.field_key}, not {field_key}",
                        )]
                    )
                certificate = loaded
                known_parents[certificate.certificate_id] = certificate
                resolved_evidence = self._authority.get_certificate_evidence_file_id(cert_id)
                if resolved_evidence is None:
                    raise AuthorityRejectionError(
                        [_rejection(
                            "UNKNOWN_CERTIFICATE",
                            f"certificate {cert_id} has no evidence",
                        )]
                    )
                # P0: the referenced evidence row is loaded independently and
                # must be owned by the target form and match the certificate
                # hash; the certificate's own hash is never trusted alone.
                evidence_row = self._authority.get_evidence(resolved_evidence)
                if evidence_row is None:
                    raise AuthorityRejectionError(
                        [_rejection(
                            "EVIDENCE_BINDING_MISSING",
                            f"certificate {cert_id} references missing evidence "
                            f"{resolved_evidence}",
                        )]
                    )
                if evidence_row.form_id != form_id:
                    raise AuthorityRejectionError(
                        [_rejection(
                            "EVIDENCE_FORM_MISMATCH",
                            f"evidence {resolved_evidence} belongs to form "
                            f"{evidence_row.form_id}, not {form_id}",
                        )]
                    )
                if evidence_row.sha256 != certificate.evidence_hash:
                    raise AuthorityRejectionError(
                        [_rejection(
                            "EVIDENCE_HASH_MISMATCH",
                            f"certificate {cert_id} evidence hash does not match "
                            f"the persisted evidence row {resolved_evidence}",
                        )]
                    )
                evidence_file_id = resolved_evidence
                if certificate.selection_state is SelectionState.ABSTAINED:
                    # The human's confirmation IS the explicit resolution: the
                    # decision is persisted with manual_resolution=True and the
                    # resolved value is bound through a derived MANUAL_ENTRY
                    # certificate whose lineage keeps the abstained machine
                    # certificate.
                    manual_resolution = True
                    derived = CandidateCertificate.from_manual_entry(
                        candidate_id=f"manual-{uuid4().hex}",
                        field_key=field_key,
                        value=values[field_key],
                        form_id=form_id,
                        evidence_hash=certificate.evidence_hash,
                        evidence_locator=f"{form_id}/manual/{field_key}",
                        template_id=form.template_id,
                        template_version=form.template_version,
                        target_record_id=form_id,
                        expected_fact_version=expected_version,
                        created_at=now,
                        lineage_parent_ids=(certificate.certificate_id,),
                    )
                    derived_certificates.append((derived, evidence_file_id))
                    certificate = derived
                elif canonical_json(certificate.value) != canonical_json(values[field_key]):
                    # The human modified the machine value: derive a
                    # MANUAL_ENTRY certificate that inherits the evidence
                    # binding and keeps the machine certificate as lineage.
                    derived = CandidateCertificate.from_manual_entry(
                        candidate_id=f"manual-{uuid4().hex}",
                        field_key=field_key,
                        value=values[field_key],
                        form_id=form_id,
                        evidence_hash=certificate.evidence_hash,
                        evidence_locator=f"{form_id}/manual/{field_key}",
                        template_id=form.template_id,
                        template_version=form.template_version,
                        target_record_id=form_id,
                        expected_fact_version=expected_version,
                        created_at=now,
                        lineage_parent_ids=(certificate.certificate_id,),
                    )
                    derived_certificates.append((derived, evidence_file_id))
                    certificate = derived

            # The transition field comes from the validated certificate
            # binding (== the mapping key by the checks above).
            bound_field_key = certificate.field_key
            decision = HumanDecision(
                decision_id=f"{form_id}:{expected_version + 1}:{bound_field_key}",
                reviewer_id=actor_id,
                candidate_id=certificate.candidate_id,
                field_key=bound_field_key,
                reason=reason,
                decided_at=now,
                manual_resolution=manual_resolution,
            )
            context = AuthorityContext(
                evidence_sha256=certificate.evidence_hash,
                current_fact_version=expected_version,
                known_sources=KNOWN_SOURCES,
                known_producers=self._known_producers,
                known_selection_artifacts=self._known_selection_artifacts,
                parent_certificates=known_parents,
                max_certificate_age=MAX_CERTIFICATE_AGE,
                now=now,
            )
            failures = list(validate_certificate(certificate, context))
            attempt = TransitionAttempt(
                fact_version=expected_version + 1,
                record_id=form_id,
                evidence_sha256=certificate.evidence_hash,
                decision=decision,
                certificate=certificate,
            )
            failures.extend(verify_transition_authorization(attempt, context))
            if failures:
                raise AuthorityRejectionError(failures)
            transitions.append(
                FactTransition(
                    transition_id=decision.decision_id,
                    record_id=form_id,
                    field_key=bound_field_key,
                    created_version=expected_version + 1,
                    record_version_id=record.record_id,
                    decision_id=decision.decision_id,
                    certificate_id=certificate.certificate_id,
                    evidence_sha256=certificate.evidence_hash,
                    evidence_locator=certificate.evidence_locator,
                    producer_id=certificate.producer_id,
                    producer_version=certificate.producer_version,
                    source_kind=certificate.source_kind,
                    template_id=certificate.template_id,
                    template_version=certificate.template_version,
                    created_at=now,
                )
            )
            decisions.append(decision)
            if evidence_file_id not in final_evidence_file_ids:
                final_evidence_file_ids.append(evidence_file_id)

        versions = self._forms.list_record_versions(form_id)
        before = versions[-1].values if versions else None
        audit = AuditEvent(
            event_id=f"EVENT-{uuid4().hex}",
            form_id=form_id,
            event_type="CONFIRM" if expected_version == 0 else "CORRECT",
            actor_id=actor_id,
            before=before,
            after=dict(values),
            reason=reason,
            evidence_ids=tuple(final_evidence_file_ids),
        )
        export_status = (
            ExportStatus.REEXPORT_REQUIRED
            if form.export_status is ExportStatus.EXPORTED
            else None
        )
        committed = self._authority.append_fact_transition(
            form_id=form_id,
            expected_version=expected_version,
            record=record,
            decisions=decisions,
            transitions=transitions,
            derived_certificates=derived_certificates,
            audit=audit,
            review_status=ReviewStatus.CONFIRMED,
            export_status=export_status,
        )
        if not committed:
            raise ConcurrentReviewError(
                f"Expected version {expected_version}, current is "
                f"{form.current_record_version}"
            )
        return record

    def _check_input_invariants(
        self,
        values: Mapping[str, object],
        certificate_ids_by_field: Mapping[str, str | None],
        manual_evidence_ids_by_field: Mapping[str, str],
    ) -> None:
        if not values:
            raise AuthorityRejectionError(
                [_rejection("EMPTY_VALUES", "values must not be empty")]
            )
        for key in values:
            if not key.strip():
                raise AuthorityRejectionError(
                    [_rejection("BLANK_FIELD_KEY", "field keys must be non-blank")]
                )
        if set(certificate_ids_by_field) != set(values):
            raise AuthorityRejectionError(
                [
                    _rejection(
                        "FIELD_SET_MISMATCH",
                        "certificate mapping keys must equal the values keys",
                    )
                ]
            )
        pure_manual = {
            field for field, cert_id in certificate_ids_by_field.items() if cert_id is None
        }
        if set(manual_evidence_ids_by_field) != pure_manual:
            raise AuthorityRejectionError(
                [
                    _rejection(
                        "FIELD_SET_MISMATCH",
                        "manual evidence mapping keys must equal the pure-manual fields",
                    )
                ]
            )

    def _resolve_manual_evidence(
        self, form_id: str, evidence_ids: set[str]
    ) -> dict[str, str]:
        """Resolve manual-entry evidence ids to hashes; ownership enforced.

        P0: evidence used for a form's confirmation must be owned by that
        form; evidence rows of other forms are rejected before any write.
        """
        resolved: dict[str, str] = {}
        for evidence_id in evidence_ids:
            evidence = self._authority.get_evidence(evidence_id)
            if evidence is None:
                raise AuthorityRejectionError(
                    [_rejection("UNKNOWN_EVIDENCE", f"unknown evidence {evidence_id}")]
                )
            if evidence.form_id != form_id:
                raise AuthorityRejectionError(
                    [_rejection(
                        "EVIDENCE_FORM_MISMATCH",
                        f"evidence {evidence_id} belongs to form "
                        f"{evidence.form_id}, not {form_id}",
                    )]
                )
            resolved[evidence_id] = evidence.sha256
        return resolved

    def eligible_certificates(
        self, form_id: str, expected_version: int, field_key: str
    ) -> list[CandidateCertificate]:
        """Persisted certificates eligible for one field at one version.

        Used by the UI to let the reviewer pick a machine certificate or the
        manual path; ids only are passed back to confirm().
        """
        return self._authority.list_certificates_for_field(
            form_id, field_key, expected_version
        )
