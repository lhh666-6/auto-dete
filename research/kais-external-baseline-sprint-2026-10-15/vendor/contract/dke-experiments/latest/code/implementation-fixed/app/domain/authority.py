"""Authority contract primitives: certificates, transitions, and provenance.

Round-2 phase-one prototype. Machine-derived values remain candidates;
eligibility for a human fact transition is an explicit, executable
precondition set. Validation is fail-closed: malformed confidence, empty
identity fields, unknown calibration identifiers, future timestamps, and
content-address mismatches all reject. Facts move through real
`FactTransition` objects and reverse traces are built and traversed rather
than assumed.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from hashlib import sha256
from typing import Any


class SourceKind(StrEnum):
    RECOGNITION = "RECOGNITION"
    RETRIEVAL = "RETRIEVAL"
    AI_SUGGESTION = "AI_SUGGESTION"
    MANUAL_ENTRY = "MANUAL_ENTRY"


class SelectionState(StrEnum):
    SELECTED = "SELECTED"
    ABSTAINED = "ABSTAINED"


class IntegrityKind(StrEnum):
    EVIDENCE = "EVIDENCE"
    IDENTITY = "IDENTITY"
    PROVENANCE = "PROVENANCE"
    FRESHNESS = "FRESHNESS"


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, StrEnum):
        return str(value)
    if isinstance(value, tuple):
        return list(value)
    return str(value)


def canonical_json(value: Any) -> str:
    """Deterministic JSON serialization used for payloads and content addresses."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=_json_default)


def canonical_values_equal(left: Any, right: Any) -> bool:
    """Value equality under the contract's canonical JSON semantics.

    Python equality treats ``2 == 2.0`` and ``1 == True`` as true, whereas the
    admission contract, reverse-trace validation, independent oracle, and
    formal projection all compare canonical JSON payloads.  Every boundary that
    decides whether a field changed must use this single relation; otherwise a
    successful admission can commit a new value while reusing the old source
    and then be reported immediately as an incomplete trace.
    """
    return canonical_json(left) == canonical_json(right)


# Non-predictive sentinel: manual entry has no model confidence score; the
# fixed value is documented and never interpreted as a prediction.
MANUAL_ENTRY_CONFIDENCE = 0.0


def is_aware_timestamp(value: datetime) -> bool:
    """Strict timezone-awareness: tzinfo present AND utcoffset() not None.

    Python treats a datetime with a tzinfo whose utcoffset() returns None as
    naive, and comparing it against a true aware datetime raises TypeError.
    Every timestamp check in the contract goes through this helper so such
    inputs are rejected (fail-closed) instead of crashing.
    """
    return value.tzinfo is not None and value.utcoffset() is not None


@dataclass(frozen=True, slots=True)
class CertificateFailure:
    """One deterministic rejection with a stable code and integrity family."""

    code: str
    integrity: IntegrityKind
    message: str


@dataclass(frozen=True, slots=True)
class HumanDecision:
    """Attributable human decision bound to one candidate and field."""

    decision_id: str
    reviewer_id: str
    candidate_id: str
    field_key: str
    reason: str
    decided_at: datetime
    manual_resolution: bool = False


@dataclass(frozen=True, slots=True)
class CandidateCertificate:
    """Immutable, content-addressed record of one machine-derived candidate.

    The candidate value is frozen at construction into a canonical JSON
    payload, so the certificate is strictly immutable even when the caller
    keeps mutating the original value object. `certificate_id` is computed
    once at construction over the full canonical field set and frozen;
    `verify_content_address()` re-derives it, which callers (and the
    transition policy) must do at authorization time.
    """

    candidate_id: str
    field_key: str
    value_payload: str
    evidence_hash: str
    evidence_locator: str
    template_id: str
    template_version: str
    source_kind: SourceKind
    producer_id: str
    producer_version: str
    selection_artifact_id: str | None
    confidence: float
    selection_state: SelectionState
    lineage_parent_ids: tuple[str, ...]
    target_record_id: str
    expected_fact_version: int
    created_at: datetime
    certificate_id: str = field(init=False, default="")

    def __post_init__(self) -> None:
        if not isinstance(self.value_payload, str) or not self.value_payload:
            raise ValueError("value_payload must be a non-empty canonical JSON string")
        json.loads(self.value_payload)  # must be parseable at construction
        object.__setattr__(self, "certificate_id", self._content_address())

    @classmethod
    def from_value(
        cls,
        *,
        candidate_id: str,
        field_key: str,
        value: Any,
        evidence_hash: str,
        evidence_locator: str,
        template_id: str,
        template_version: str,
        source_kind: SourceKind,
        producer_id: str,
        producer_version: str,
        selection_artifact_id: str | None,
        confidence: float,
        selection_state: SelectionState,
        lineage_parent_ids: tuple[str, ...],
        target_record_id: str,
        expected_fact_version: int,
        created_at: datetime,
    ) -> CandidateCertificate:
        """Build a certificate, freezing `value` into a canonical payload."""
        return cls(
            candidate_id=candidate_id,
            field_key=field_key,
            value_payload=canonical_json(value),
            evidence_hash=evidence_hash,
            evidence_locator=evidence_locator,
            template_id=template_id,
            template_version=template_version,
            source_kind=source_kind,
            producer_id=producer_id,
            producer_version=producer_version,
            selection_artifact_id=selection_artifact_id,
            confidence=confidence,
            selection_state=selection_state,
            lineage_parent_ids=lineage_parent_ids,
            target_record_id=target_record_id,
            expected_fact_version=expected_fact_version,
            created_at=created_at,
        )

    @classmethod
    def from_manual_entry(
        cls,
        *,
        candidate_id: str,
        field_key: str,
        value: Any,
        form_id: str,
        evidence_hash: str,
        evidence_locator: str,
        template_id: str,
        template_version: str,
        target_record_id: str,
        expected_fact_version: int,
        created_at: datetime,
        lineage_parent_ids: tuple[str, ...] = (),
        confidence: float = MANUAL_ENTRY_CONFIDENCE,
        producer_id: str = "human-reviewer",
        producer_version: str = "manual-entry-v1",
    ) -> CandidateCertificate:
        """Build a manual-entry certificate (explicit human path).

        Manual entry is not predictive selection: no selection artifact, no
        model confidence (fixed non-predictive constant). Human-modified
        machine values pass the original certificate id in lineage_parent_ids.
        """
        return cls(
            candidate_id=candidate_id,
            field_key=field_key,
            value_payload=canonical_json(value),
            evidence_hash=evidence_hash,
            evidence_locator=evidence_locator,
            template_id=template_id,
            template_version=template_version,
            source_kind=SourceKind.MANUAL_ENTRY,
            producer_id=producer_id,
            producer_version=producer_version,
            selection_artifact_id=None,
            confidence=confidence,
            selection_state=SelectionState.SELECTED,
            lineage_parent_ids=lineage_parent_ids,
            target_record_id=target_record_id,
            expected_fact_version=expected_fact_version,
            created_at=created_at,
        )

    @classmethod
    def from_persisted(cls, *, stored_certificate_id: str, **fields: Any) -> CandidateCertificate:
        """Rebuild a certificate keeping the stored content address.

        The stored id is preserved so that verify_content_address() detects
        any row whose fields diverged from what the id was computed over.
        """
        certificate = cls(**fields)
        object.__setattr__(certificate, "certificate_id", stored_certificate_id)
        return certificate

    @property
    def value(self) -> Any:
        """The candidate value as parsed from the frozen payload."""
        return json.loads(self.value_payload)

    def _content(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "field_key": self.field_key,
            "value_payload": self.value_payload,
            "evidence_hash": self.evidence_hash,
            "evidence_locator": self.evidence_locator,
            "template_id": self.template_id,
            "template_version": self.template_version,
            "source_kind": self.source_kind,
            "producer_id": self.producer_id,
            "producer_version": self.producer_version,
            "selection_artifact_id": self.selection_artifact_id,
            "confidence": self.confidence,
            "selection_state": self.selection_state,
            "lineage_parent_ids": self.lineage_parent_ids,
            "target_record_id": self.target_record_id,
            "expected_fact_version": self.expected_fact_version,
            "created_at": self.created_at,
        }

    def _content_address(self) -> str:
        return sha256(canonical_json(self._content()).encode("utf-8")).hexdigest()

    def recompute_id(self) -> str:
        """Re-derive the content address from the current fields."""
        return self._content_address()

    def verify_content_address(self) -> bool:
        """True when the frozen id still matches the re-derived address."""
        return self.recompute_id() == self.certificate_id


@dataclass(frozen=True, slots=True)
class AuthorityContext:
    """Deterministic validation inputs: registries, evidence, and fact state."""

    evidence_sha256: str
    current_fact_version: int
    known_sources: frozenset[SourceKind]
    known_producers: frozenset[tuple[str, str]]
    known_selection_artifacts: frozenset[str] = frozenset()
    parent_certificates: Mapping[str, CandidateCertificate] = field(default_factory=dict)
    evidence_sha256_by_certificate: Mapping[str, str] = field(default_factory=dict)
    max_certificate_age: timedelta | None = None
    now: datetime | None = None

    @property
    def reference_time(self) -> datetime:
        return self.now if self.now is not None else datetime.now(UTC)


def validate_certificate(
    certificate: CandidateCertificate, context: AuthorityContext
) -> tuple[CertificateFailure, ...]:
    """Fail-closed hard evidence, identity, provenance, and freshness checks.

    Returns every failure found; an empty tuple means the certificate is
    valid. Malformed or out-of-range confidence, empty identity fields,
    unknown calibration identifiers (including under an empty registry), and
    future timestamps reject. Checks never consult model confidence to
    compensate for broken evidence, missing provenance, or stale state.
    """
    return _validate(certificate, context, frozenset())


def _validate(
    certificate: CandidateCertificate,
    context: AuthorityContext,
    visited: frozenset[str],
) -> tuple[CertificateFailure, ...]:
    if certificate.candidate_id in visited:
        return (
            CertificateFailure(
                "LINEAGE_CYCLE", IntegrityKind.PROVENANCE, "lineage parent cycle detected"
            ),
        )
    visited = visited.union((certificate.candidate_id,))
    failures: list[CertificateFailure] = []

    # Identity fields must be present and non-empty.
    if not certificate.candidate_id or not certificate.candidate_id.strip():
        failures.append(
            CertificateFailure(
                "EMPTY_CANDIDATE_ID", IntegrityKind.IDENTITY, "candidate id is empty"
            )
        )
    if not certificate.template_id or not certificate.template_id.strip():
        failures.append(
            CertificateFailure("EMPTY_TEMPLATE", IntegrityKind.IDENTITY, "template id is empty")
        )
    if not certificate.template_version or not certificate.template_version.strip():
        failures.append(
            CertificateFailure(
                "EMPTY_TEMPLATE", IntegrityKind.IDENTITY, "template version is empty"
            )
        )
    if not certificate.target_record_id or not certificate.target_record_id.strip():
        failures.append(
            CertificateFailure(
                "EMPTY_TARGET_RECORD", IntegrityKind.IDENTITY, "target record id is empty"
            )
        )

    # Confidence must be a finite value in [0, 1].
    if not math.isfinite(certificate.confidence) or not (0.0 <= certificate.confidence <= 1.0):
        failures.append(
            CertificateFailure(
                "INVALID_CONFIDENCE",
                IntegrityKind.IDENTITY,
                "confidence must be a finite value in [0, 1]",
            )
        )

    # Evidence integrity.
    if not certificate.evidence_hash:
        failures.append(
            CertificateFailure(
                "MISSING_EVIDENCE_HASH",
                IntegrityKind.EVIDENCE,
                "candidate carries no evidence hash",
            )
        )
    elif certificate.evidence_hash != context.evidence_sha256_by_certificate.get(
        certificate.certificate_id, context.evidence_sha256
    ):
        failures.append(
            CertificateFailure(
                "EVIDENCE_HASH_MISMATCH",
                IntegrityKind.EVIDENCE,
                "candidate evidence does not match the presented evidence",
            )
        )

    # Identity.
    if certificate.source_kind not in context.known_sources:
        failures.append(
            CertificateFailure(
                "UNKNOWN_SOURCE",
                IntegrityKind.IDENTITY,
                f"source {certificate.source_kind} is not registered",
            )
        )
    if not certificate.producer_id or not certificate.producer_version:
        failures.append(
            CertificateFailure(
                "UNKNOWN_PRODUCER", IntegrityKind.IDENTITY, "producer identity is incomplete"
            )
        )
    elif (certificate.producer_id, certificate.producer_version) not in context.known_producers:
        failures.append(
            CertificateFailure(
                "UNKNOWN_PRODUCER",
                IntegrityKind.IDENTITY,
                f"producer {certificate.producer_id}/{certificate.producer_version} "
                "is not registered",
            )
        )

    # Provenance.
    if not certificate.evidence_locator or not certificate.evidence_locator.strip():
        failures.append(
            CertificateFailure(
                "MISSING_EVIDENCE_LOCATOR",
                IntegrityKind.PROVENANCE,
                "evidence locator (page/region/field) is required",
            )
        )
    if certificate.source_kind is SourceKind.AI_SUGGESTION and not certificate.lineage_parent_ids:
        failures.append(
            CertificateFailure(
                "INCOMPLETE_LINEAGE",
                IntegrityKind.PROVENANCE,
                "AI suggestions must declare parent lineage",
            )
        )
    for parent_id in certificate.lineage_parent_ids:
        parent = context.parent_certificates.get(parent_id)
        if parent is None:
            failures.append(
                CertificateFailure(
                    "INCOMPLETE_LINEAGE",
                    IntegrityKind.PROVENANCE,
                    f"parent certificate {parent_id} is missing",
                )
            )
        else:
            parent_failures = _validate(parent, context, visited)
            if parent_failures:
                failures.append(
                    CertificateFailure(
                        "INCOMPLETE_LINEAGE",
                        IntegrityKind.PROVENANCE,
                        f"parent certificate {parent_id} is invalid",
                    )
                )

    # Machine predictive selection must reference a registered selection
    # artifact (a threshold policy identifier, not a statistical calibration
    # claim). Manual entry is not predictive selection and needs none.
    # Fail-closed: an empty registry admits no artifact ids.
    if (
        certificate.selection_state is SelectionState.SELECTED
        and certificate.source_kind is not SourceKind.MANUAL_ENTRY
        and certificate.selection_artifact_id is None
    ):
        failures.append(
            CertificateFailure(
                "MISSING_SELECTION_ARTIFACT",
                IntegrityKind.IDENTITY,
                "machine-selected candidates must carry a selection artifact id",
            )
        )
    if certificate.selection_artifact_id is not None:
        if certificate.selection_artifact_id not in context.known_selection_artifacts:
            failures.append(
                CertificateFailure(
                    "UNKNOWN_SELECTION_ARTIFACT",
                    IntegrityKind.IDENTITY,
                    f"selection artifact {certificate.selection_artifact_id} is not registered",
                )
            )

    # Freshness: timezone-aware timestamps, age expiry, and no future
    # timestamps. Naive timestamps are rejected before any comparison, so a
    # malformed clock can never raise TypeError instead of a controlled
    # rejection.
    if not is_aware_timestamp(certificate.created_at):
        failures.append(
            CertificateFailure(
                "NAIVE_TIMESTAMP",
                IntegrityKind.FRESHNESS,
                "certificate timestamp is not timezone-aware",
            )
        )
    reference_time = context.reference_time
    if not is_aware_timestamp(reference_time):
        failures.append(
            CertificateFailure(
                "NAIVE_TIMESTAMP",
                IntegrityKind.FRESHNESS,
                "context reference time is not timezone-aware",
            )
        )
    if is_aware_timestamp(certificate.created_at) and is_aware_timestamp(reference_time):
        if certificate.created_at > reference_time:
            failures.append(
                CertificateFailure(
                    "FUTURE_CREATED_AT",
                    IntegrityKind.FRESHNESS,
                    "certificate timestamp lies in the future",
                )
            )
        if context.max_certificate_age is not None:
            age = reference_time - certificate.created_at
            if age > context.max_certificate_age:
                failures.append(
                    CertificateFailure(
                        "EXPIRED_CERTIFICATE",
                        IntegrityKind.FRESHNESS,
                        "certificate is older than the maximum allowed age",
                    )
                )

    return tuple(failures)


@dataclass(frozen=True, slots=True)
class AuthorizationBinding:
    """Immutable binding from one human decision to one reviewed certificate.

    The bound certificate and the exact human-authorized final value are
    both frozen at transaction time.
    """

    binding_id: str
    decision_id: str
    certificate_id: str
    authorized_value_payload: str
    bound_at: datetime

    @property
    def value(self) -> Any:
        return json.loads(self.authorized_value_payload)


@dataclass(frozen=True, slots=True)
class FactTransition:
    """One authorized fact version, created only through the human decision.

    record_version_id is the exact record_versions.record_id of the fact row
    this transition created. The trace path requires it to equal the
    selected RecordVersion.record_id; a single-column FK alone cannot prove
    that the row belongs to this (form, created_version).
    """

    transition_id: str
    record_id: str
    field_key: str
    created_version: int
    record_version_id: str
    decision_id: str
    certificate_id: str
    evidence_sha256: str
    evidence_locator: str
    producer_id: str
    producer_version: str
    source_kind: SourceKind
    template_id: str
    template_version: str
    created_at: datetime
    value_payload: str | None = None

    @property
    def value(self) -> Any:
        return json.loads(self.value_payload) if self.value_payload is not None else None


@dataclass(frozen=True, slots=True)
class TraceHop:
    hop: str
    reference: str


@dataclass(frozen=True, slots=True)
class ProvenanceTrace:
    """Reverse trace F -> H -> C -> E with explicit hop references."""

    complete: bool
    hops: tuple[TraceHop, ...]
    failures: tuple[str, ...]


def build_provenance_trace(
    transition: FactTransition,
    decision: HumanDecision,
    certificate: CandidateCertificate,
    evidence_sha256: str,
) -> ProvenanceTrace:
    """Traverse the fact -> decision -> certificate -> evidence chain.

    Every hop is bound by identity checks; an incomplete chain reports which
    bindings failed instead of merely flagging the record.
    """
    hops: list[TraceHop] = []
    failures: list[str] = []
    hops.append(TraceHop("F", f"{transition.record_id}#{transition.created_version}"))
    if not decision.decision_id.strip():
        failures.append("decision id is empty")
    if transition.decision_id != decision.decision_id:
        failures.append("transition is not bound to the decision")
    hops.append(TraceHop("H", decision.decision_id))
    if decision.candidate_id != certificate.candidate_id:
        failures.append("decision is not bound to the certificate")
    if decision.field_key != certificate.field_key:
        failures.append("decision field binding mismatch")
    if transition.field_key != certificate.field_key:
        failures.append("transition field binding mismatch")
    if transition.field_key != decision.field_key:
        failures.append("transition decision field mismatch")
    if transition.certificate_id != certificate.certificate_id:
        failures.append("transition is not bound to the certificate")
    if transition.record_id != certificate.target_record_id:
        failures.append("transition record binding mismatch")
    if transition.created_version != certificate.expected_fact_version + 1:
        failures.append("transition version mismatch")
    if transition.producer_id != certificate.producer_id:
        failures.append("transition producer binding mismatch")
    if transition.producer_version != certificate.producer_version:
        failures.append("transition producer version mismatch")
    if transition.template_id != certificate.template_id:
        failures.append("transition template binding mismatch")
    if transition.template_version != certificate.template_version:
        failures.append("transition template version mismatch")
    if transition.source_kind != certificate.source_kind:
        failures.append("transition source kind mismatch")
    hops.append(TraceHop("C", certificate.certificate_id))
    if certificate.evidence_hash != evidence_sha256:
        failures.append("certificate is not bound to the evidence")
    if transition.evidence_sha256 != evidence_sha256:
        failures.append("transition is not bound to the evidence")
    if not certificate.verify_content_address():
        failures.append("certificate content address mismatch")
    if certificate.evidence_locator != transition.evidence_locator:
        failures.append("transition evidence locator mismatch")
    hops.append(TraceHop("E", evidence_sha256))
    naive: list[str] = []
    if not is_aware_timestamp(certificate.created_at):
        naive.append("certificate")
    if not is_aware_timestamp(decision.decided_at):
        naive.append("decision")
    if not is_aware_timestamp(transition.created_at):
        naive.append("transition")
    if naive:
        failures.append(f"naive timestamp: {', '.join(naive)}")
    else:
        if certificate.created_at > decision.decided_at:
            failures.append("decision predates certificate")
        if decision.decided_at > transition.created_at:
            failures.append("transition predates decision")
    return ProvenanceTrace(complete=not failures, hops=tuple(hops), failures=tuple(failures))


@dataclass(frozen=True, slots=True)
class TransitionAttempt:
    """What an architecture actually produced for one fact transition."""

    fact_version: int
    record_id: str
    evidence_sha256: str
    decision: HumanDecision | None
    certificate: CandidateCertificate | None


def verify_transition_authorization(
    attempt: TransitionAttempt, context: AuthorityContext
) -> tuple[CertificateFailure, ...]:
    """Re-verify an attempt against the contract independently.

    Used to measure unauthorized transitions: an attempt is unauthorized when
    it lacks a decision or certificate, when the certificate fails
    validation, or when the decision/evidence bindings are broken.
    """
    failures: list[CertificateFailure] = []
    if attempt.decision is None:
        failures.append(
            CertificateFailure(
                "MISSING_DECISION",
                IntegrityKind.IDENTITY,
                "no attributable human decision accompanies the transition",
            )
        )
    if attempt.certificate is None:
        failures.append(
            CertificateFailure(
                "MISSING_CERTIFICATE",
                IntegrityKind.IDENTITY,
                "no candidate certificate accompanies the transition",
            )
        )
    if attempt.decision is not None:
        if not attempt.decision.reviewer_id.strip() or not attempt.decision.reason.strip():
            failures.append(
                CertificateFailure(
                    "UNATTRIBUTED_DECISION",
                    IntegrityKind.IDENTITY,
                    "a transition requires an attributable human decision and reason",
                )
            )
        if not attempt.decision.decision_id.strip():
            failures.append(
                CertificateFailure(
                    "EMPTY_DECISION_ID",
                    IntegrityKind.IDENTITY,
                    "decision id is empty",
                )
            )
        if not is_aware_timestamp(attempt.decision.decided_at):
            failures.append(
                CertificateFailure(
                    "NAIVE_TIMESTAMP",
                    IntegrityKind.FRESHNESS,
                    "decision timestamp is not timezone-aware",
                )
            )
        if (
            is_aware_timestamp(attempt.decision.decided_at)
            and attempt.certificate is not None
            and is_aware_timestamp(attempt.certificate.created_at)
            and attempt.decision.decided_at < attempt.certificate.created_at
        ):
            failures.append(
                CertificateFailure(
                    "DECISION_PREDATES_CERTIFICATE",
                    IntegrityKind.FRESHNESS,
                    "decision predates the certificate",
                )
            )
        if (
            is_aware_timestamp(attempt.decision.decided_at)
            and is_aware_timestamp(context.reference_time)
            and attempt.decision.decided_at > context.reference_time
        ):
            failures.append(
                CertificateFailure(
                    "DECISION_IN_FUTURE",
                    IntegrityKind.FRESHNESS,
                    "decision timestamp lies in the future",
                )
            )
    if attempt.certificate is not None:
        failures.extend(validate_certificate(attempt.certificate, context))
        if attempt.certificate.expected_fact_version != context.current_fact_version:
            failures.append(
                CertificateFailure(
                    "STALE_FACT_VERSION",
                    IntegrityKind.FRESHNESS,
                    "decision is bound to an older fact version",
                )
            )
        if (
            attempt.certificate.selection_state is SelectionState.ABSTAINED
            and attempt.decision is not None
            and not attempt.decision.manual_resolution
        ):
            failures.append(
                CertificateFailure(
                    "ABSTAINED_UNRESOLVED",
                    IntegrityKind.PROVENANCE,
                    "an abstained candidate requires explicit manual resolution",
                )
            )
        if attempt.decision is not None and (
            attempt.decision.candidate_id != attempt.certificate.candidate_id
        ):
            failures.append(
                CertificateFailure(
                    "DECISION_CANDIDATE_MISMATCH",
                    IntegrityKind.IDENTITY,
                    "the decision is bound to a different candidate",
                )
            )
        if attempt.decision is not None and (
            attempt.decision.field_key != attempt.certificate.field_key
        ):
            failures.append(
                CertificateFailure(
                    "FIELD_KEY_BINDING_MISMATCH",
                    IntegrityKind.IDENTITY,
                    "the decision is bound to a different field than the certificate",
                )
            )
        if attempt.record_id != attempt.certificate.target_record_id:
            failures.append(
                CertificateFailure(
                    "RECORD_BINDING_MISMATCH",
                    IntegrityKind.IDENTITY,
                    "transition targets a different record than the certificate",
                )
            )
        if attempt.fact_version != context.current_fact_version + 1:
            failures.append(
                CertificateFailure(
                    "FACT_VERSION_MISMATCH",
                    IntegrityKind.FRESHNESS,
                    "transition version does not follow the current fact version",
                )
            )
        if attempt.certificate.evidence_hash != attempt.evidence_sha256:
            failures.append(
                CertificateFailure(
                    "EVIDENCE_HASH_MISMATCH",
                    IntegrityKind.EVIDENCE,
                    "transition evidence does not match the certificate",
                )
            )
        if attempt.evidence_sha256 != context.evidence_sha256:
            failures.append(
                CertificateFailure(
                    "EVIDENCE_HASH_MISMATCH",
                    IntegrityKind.EVIDENCE,
                    "transition evidence does not match the presented evidence",
                )
            )
        if not attempt.certificate.verify_content_address():
            failures.append(
                CertificateFailure(
                    "CONTENT_ADDRESS_MISMATCH",
                    IntegrityKind.IDENTITY,
                    "certificate content address no longer matches its fields",
                )
            )
    return tuple(failures)
