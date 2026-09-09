"""Evidence-bound fact transition and authority-preserving review routing.

Round-2 prototype: a fact transition is eligible only when an attributable
human decision, a valid certificate, and the current fact version are all
present. Successful authorization returns a real `FactTransition` object
whose certificate binding is verified at authorization time. Routing only
changes the review level or requests reacquisition; no route creates or
modifies an authoritative fact.
"""

from dataclasses import dataclass
from enum import StrEnum

from app.domain.authority import (
    AuthorityContext,
    CandidateCertificate,
    CertificateFailure,
    FactTransition,
    HumanDecision,
    IntegrityKind,
    SelectionState,
    is_aware_timestamp,
    validate_certificate,
)


class ReviewRoute(StrEnum):
    STANDARD_REVIEW = "STANDARD_REVIEW"
    ENHANCED_REVIEW = "ENHANCED_REVIEW"
    REJECT_REACQUIRE = "REJECT_REACQUIRE"


@dataclass(frozen=True, slots=True)
class RoutingConfig:
    """Fixed policy weights — configuration, never tuned on evaluation splits.

    The risk score follows the design: r(c) = f(u, 1-i, 1-p, 1-v, d) with
    weights fixed here. For certificates that pass the hard checks the
    integrity, provenance, and freshness terms are zero by construction; the
    remaining terms are exactly what this configuration declares.
    """

    confidence_threshold: float = 0.6
    weight_uncertainty: float = 0.5
    weight_integrity: float = 0.2
    weight_provenance: float = 0.1
    weight_freshness: float = 0.1
    weight_disagreement: float = 0.1


@dataclass(frozen=True, slots=True)
class RoutingDecision:
    route: ReviewRoute
    failures: tuple[CertificateFailure, ...]
    risk_score: float | None = None


@dataclass(frozen=True, slots=True)
class FactTransitionResult:
    allowed: bool
    failures: tuple[CertificateFailure, ...]
    transition: FactTransition | None = None

    @property
    def created_version(self) -> int | None:
        return self.transition.created_version if self.transition is not None else None


class TransitionPolicy:
    """Authority-preserving policy: hard checks always run before scoring."""

    def __init__(self, config: RoutingConfig | None = None) -> None:
        self._config = config if config is not None else RoutingConfig()

    def route(
        self,
        certificate: CandidateCertificate,
        context: AuthorityContext,
        *,
        disagreement: bool = False,
        weak_evidence: bool = False,
    ) -> RoutingDecision:
        """Route one candidate; never creates or modifies a fact."""
        failures = self._hard_failures(certificate, context)
        if failures:
            return RoutingDecision(ReviewRoute.REJECT_REACQUIRE, failures)
        route = self._soft_route(certificate, disagreement, weak_evidence)
        return RoutingDecision(route, (), self._risk_score(certificate, context, disagreement))

    def authorize(
        self,
        decision: HumanDecision,
        certificate: CandidateCertificate,
        context: AuthorityContext,
    ) -> FactTransitionResult:
        """Decide whether a reviewed candidate may become a fact version.

        A decision is necessary but not sufficient: the certificate must be
        valid, current, and content-address-verified, and the decision must
        be attributable and bound to this candidate. On success a real
        `FactTransition` is returned; rejection is explicit and leaves the
        fact unchanged.
        """
        failures = self._hard_failures(certificate, context)
        if not certificate.verify_content_address():
            failures = (
                *failures,
                CertificateFailure(
                    "CONTENT_ADDRESS_MISMATCH",
                    IntegrityKind.IDENTITY,
                    "certificate content address no longer matches its fields",
                ),
            )
        if not decision.reviewer_id.strip() or not decision.reason.strip():
            failures = (
                *failures,
                CertificateFailure(
                    "UNATTRIBUTED_DECISION",
                    IntegrityKind.IDENTITY,
                    "a transition requires an attributable human decision and reason",
                ),
            )
        if not decision.decision_id.strip():
            failures = (
                *failures,
                CertificateFailure(
                    "EMPTY_DECISION_ID",
                    IntegrityKind.IDENTITY,
                    "decision id is empty",
                ),
            )
        if not is_aware_timestamp(decision.decided_at):
            failures = (
                *failures,
                CertificateFailure(
                    "NAIVE_TIMESTAMP",
                    IntegrityKind.FRESHNESS,
                    "decision timestamp is not timezone-aware",
                ),
            )
        elif (
            is_aware_timestamp(certificate.created_at)
            and decision.decided_at < certificate.created_at
        ):
            failures = (
                *failures,
                CertificateFailure(
                    "DECISION_PREDATES_CERTIFICATE",
                    IntegrityKind.FRESHNESS,
                    "decision predates the certificate",
                ),
            )
        if (
            is_aware_timestamp(decision.decided_at)
            and is_aware_timestamp(context.reference_time)
            and decision.decided_at > context.reference_time
        ):
            failures = (
                *failures,
                CertificateFailure(
                    "DECISION_IN_FUTURE",
                    IntegrityKind.FRESHNESS,
                    "decision timestamp lies in the future",
                ),
            )
        if decision.candidate_id != certificate.candidate_id:
            failures = (
                *failures,
                CertificateFailure(
                    "DECISION_CANDIDATE_MISMATCH",
                    IntegrityKind.IDENTITY,
                    "the decision is bound to a different candidate",
                ),
            )
        if (
            certificate.selection_state is SelectionState.ABSTAINED
            and not decision.manual_resolution
        ):
            failures = (
                *failures,
                CertificateFailure(
                    "ABSTAINED_UNRESOLVED",
                    IntegrityKind.PROVENANCE,
                    "an abstained candidate requires explicit manual resolution",
                ),
            )
        if failures:
            return FactTransitionResult(False, failures, None)
        created_version = context.current_fact_version + 1
        transition = FactTransition(
            transition_id=f"{decision.decision_id}:{created_version}",
            record_id=certificate.target_record_id,
            field_key=certificate.field_key,
            created_version=created_version,
            # Prototype-only proposal: authorize() runs before any
            # RecordVersion row exists, so there is no persisted record id
            # yet. The production confirm path carries the real id.
            record_version_id="",
            decision_id=decision.decision_id,
            certificate_id=certificate.certificate_id,
            evidence_sha256=context.evidence_sha256,
            evidence_locator=certificate.evidence_locator,
            producer_id=certificate.producer_id,
            producer_version=certificate.producer_version,
            source_kind=certificate.source_kind,
            template_id=certificate.template_id,
            template_version=certificate.template_version,
            created_at=context.reference_time,
        )
        return FactTransitionResult(True, (), transition)

    def _hard_failures(
        self, certificate: CandidateCertificate, context: AuthorityContext
    ) -> tuple[CertificateFailure, ...]:
        failures = validate_certificate(certificate, context)
        if certificate.expected_fact_version != context.current_fact_version:
            failures = (
                *failures,
                CertificateFailure(
                    "STALE_FACT_VERSION",
                    IntegrityKind.FRESHNESS,
                    "decision is bound to an older fact version",
                ),
            )
        return failures

    def _soft_route(
        self,
        certificate: CandidateCertificate,
        disagreement: bool,
        weak_evidence: bool,
    ) -> ReviewRoute:
        if certificate.selection_state is SelectionState.ABSTAINED:
            return ReviewRoute.ENHANCED_REVIEW
        if certificate.confidence < self._config.confidence_threshold:
            return ReviewRoute.ENHANCED_REVIEW
        if disagreement or weak_evidence:
            return ReviewRoute.ENHANCED_REVIEW
        return ReviewRoute.STANDARD_REVIEW

    def _risk_score(
        self,
        certificate: CandidateCertificate,
        context: AuthorityContext,
        disagreement: bool,
    ) -> float:
        """Fault-escape surrogate score r(c) = f(u, 1-i, 1-p, 1-v, d).

        Computed only after hard checks pass. For a valid certificate the
        integrity, provenance, and freshness terms are zero, so the score
        reduces to the uncertainty and disagreement terms declared in
        `RoutingConfig`. The benchmark treats this as ordinary
        uncertainty-aware routing unless multi-seed experiments show
        otherwise.
        """
        uncertainty = 1.0 - min(max(certificate.confidence, 0.0), 1.0)
        failures = validate_certificate(certificate, context)
        integrity_valid = not any(
            failure.integrity is IntegrityKind.EVIDENCE for failure in failures
        )
        provenance_valid = not any(
            failure.integrity is IntegrityKind.PROVENANCE for failure in failures
        )
        fresh = certificate.expected_fact_version == context.current_fact_version and not any(
            failure.integrity is IntegrityKind.FRESHNESS for failure in failures
        )
        return (
            self._config.weight_uncertainty * uncertainty
            + self._config.weight_integrity * (0.0 if integrity_valid else 1.0)
            + self._config.weight_provenance * (0.0 if provenance_valid else 1.0)
            + self._config.weight_freshness * (0.0 if fresh else 1.0)
            + self._config.weight_disagreement * (1.0 if disagreement else 0.0)
        )
