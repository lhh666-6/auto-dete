"""Unit tests for the authority contract (round 2: fail-closed + real traces)."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, tzinfo

import pytest

from app.application.transition_policy import (
    FactTransitionResult,
    ReviewRoute,
    RoutingConfig,
    TransitionPolicy,
)
from app.domain.authority import (
    AuthorityContext,
    CandidateCertificate,
    FactTransition,
    HumanDecision,
    IntegrityKind,
    SelectionState,
    SourceKind,
    TransitionAttempt,
    build_provenance_trace,
    validate_certificate,
    verify_transition_authorization,
)

NOW = datetime(2026, 8, 16, 12, 0, tzinfo=UTC)
EVIDENCE_HASH = "ab" * 32


class _BrokenTzInfo(tzinfo):
    """tzinfo present, but utcoffset() returns None: pseudo-naive."""

    def utcoffset(self, dt: datetime | None) -> None:
        return None

    def dst(self, dt: datetime | None) -> None:
        return None

    def tzname(self, dt: datetime | None) -> str:
        return "broken"


PSEUDO_NAIVE = datetime(2026, 8, 16, 12, 0, tzinfo=_BrokenTzInfo())


def make_certificate(**overrides: object) -> CandidateCertificate:
    arguments: dict[str, object] = {
        "candidate_id": "c-1",
        "field_key": "total_quantity",
        "value": 7,
        "evidence_hash": EVIDENCE_HASH,
        "evidence_locator": "form-1/page-1/field:total_quantity",
        "template_id": "T1",
        "template_version": "1",
        "source_kind": SourceKind.RECOGNITION,
        "producer_id": "recognizer-a",
        "producer_version": "1.0",
        "selection_artifact_id": "cal-1",
        "confidence": 0.97,
        "selection_state": SelectionState.SELECTED,
        "lineage_parent_ids": (),
        "target_record_id": "REC-1",
        "expected_fact_version": 1,
        "created_at": NOW,
    }
    arguments.update(overrides)
    return CandidateCertificate.from_value(**arguments)  # type: ignore[arg-type]


def make_context(**overrides: object) -> AuthorityContext:
    arguments: dict[str, object] = {
        "evidence_sha256": EVIDENCE_HASH,
        "current_fact_version": 1,
        "known_sources": frozenset(
            {SourceKind.RECOGNITION, SourceKind.AI_SUGGESTION, SourceKind.MANUAL_ENTRY}
        ),
        "known_producers": frozenset(
            {
                ("recognizer-a", "1.0"),
                ("recognizer-b", "2.0"),
                ("human-reviewer", "manual-entry-v1"),
            }
        ),
        "known_selection_artifacts": frozenset({"cal-1", "cal-2"}),
        "parent_certificates": {},
        "max_certificate_age": timedelta(hours=1),
        "now": NOW,
    }
    arguments.update(overrides)
    return AuthorityContext(**arguments)  # type: ignore[arg-type]


def make_decision(**overrides: object) -> HumanDecision:
    arguments: dict[str, object] = {
        "decision_id": "d-1",
        "reviewer_id": "reviewer-1",
        "candidate_id": "c-1",
        "field_key": "total_quantity",
        "reason": "reviewed against evidence",
        "decided_at": NOW,
        "manual_resolution": False,
    }
    arguments.update(overrides)
    return HumanDecision(**arguments)  # type: ignore[arg-type]


def test_valid_certificate_passes_all_checks() -> None:
    assert validate_certificate(make_certificate(), make_context()) == ()


def test_certificate_is_immutable() -> None:
    certificate = make_certificate()
    with pytest.raises(FrozenInstanceError):
        certificate.value_payload = "999"  # type: ignore[misc]


def test_value_is_frozen_at_construction() -> None:
    mutable = {"nested": [1, 2]}
    certificate = make_certificate(value=mutable)
    certificate_id = certificate.certificate_id
    mutable["nested"].append(3)
    mutable["extra"] = "changed"
    assert certificate.value == {"nested": [1, 2]}
    assert certificate.certificate_id == certificate_id
    assert certificate.verify_content_address()


def test_content_address_changes_with_any_field() -> None:
    certificate = make_certificate()
    assert certificate.certificate_id == make_certificate().certificate_id
    assert certificate.certificate_id != make_certificate(value=8).certificate_id
    assert certificate.certificate_id != make_certificate(confidence=0.5).certificate_id
    assert certificate.certificate_id != make_certificate(producer_version="2.0").certificate_id


def test_content_address_verification_passes() -> None:
    assert make_certificate().verify_content_address() is True
    assert make_certificate().recompute_id() == make_certificate().certificate_id


@pytest.mark.parametrize(
    ("certificate", "context", "code"),
    [
        (
            make_certificate(evidence_hash="ff" * 32),
            make_context(),
            "EVIDENCE_HASH_MISMATCH",
        ),
        (make_certificate(evidence_hash=""), make_context(), "MISSING_EVIDENCE_HASH"),
        (
            make_certificate(evidence_locator=""),
            make_context(),
            "MISSING_EVIDENCE_LOCATOR",
        ),
        (
            make_certificate(source_kind=SourceKind.RETRIEVAL),
            make_context(known_sources=frozenset({SourceKind.RECOGNITION})),
            "UNKNOWN_SOURCE",
        ),
        (
            make_certificate(producer_id="mystery-engine", producer_version="9.9"),
            make_context(),
            "UNKNOWN_PRODUCER",
        ),
        (
            make_certificate(selection_artifact_id=None),
            make_context(),
            "MISSING_SELECTION_ARTIFACT",
        ),
        (
            make_certificate(selection_artifact_id="cal-none"),
            make_context(),
            "UNKNOWN_SELECTION_ARTIFACT",
        ),
        (
            make_certificate(
                source_kind=SourceKind.AI_SUGGESTION,
                lineage_parent_ids=("missing-parent",),
            ),
            make_context(),
            "INCOMPLETE_LINEAGE",
        ),
        (
            make_certificate(created_at=NOW - timedelta(hours=2)),
            make_context(),
            "EXPIRED_CERTIFICATE",
        ),
        (
            make_certificate(confidence=float("nan")),
            make_context(),
            "INVALID_CONFIDENCE",
        ),
        (
            make_certificate(confidence=2.0),
            make_context(),
            "INVALID_CONFIDENCE",
        ),
        (
            make_certificate(confidence=-0.1),
            make_context(),
            "INVALID_CONFIDENCE",
        ),
        (
            make_certificate(candidate_id=""),
            make_context(),
            "EMPTY_CANDIDATE_ID",
        ),
        (
            make_certificate(template_id=""),
            make_context(),
            "EMPTY_TEMPLATE",
        ),
        (
            make_certificate(template_version=""),
            make_context(),
            "EMPTY_TEMPLATE",
        ),
        (
            make_certificate(target_record_id=""),
            make_context(),
            "EMPTY_TARGET_RECORD",
        ),
        (
            make_certificate(created_at=NOW + timedelta(hours=2)),
            make_context(),
            "FUTURE_CREATED_AT",
        ),
    ],
)
def test_certificate_rejection_families(
    certificate: CandidateCertificate, context: AuthorityContext, code: str
) -> None:
    failures = validate_certificate(certificate, context)
    assert any(failure.code == code for failure in failures)
    assert all(failure.integrity is not None and failure.message for failure in failures)


def test_unknown_selection_artifact_rejected_under_empty_registry() -> None:
    # Fail-closed: an empty registry admits no selection artifact ids.
    certificate = make_certificate(selection_artifact_id="cal-1")
    context = make_context(known_selection_artifacts=frozenset())
    failures = validate_certificate(certificate, context)
    assert any(
        failure.code == "UNKNOWN_SELECTION_ARTIFACT" for failure in failures
    )


def test_abstained_without_artifact_valid_under_empty_registry() -> None:
    certificate = make_certificate(
        value=None,
        confidence=0.0,
        selection_state=SelectionState.ABSTAINED,
        selection_artifact_id=None,
    )
    context = make_context(known_selection_artifacts=frozenset())
    assert validate_certificate(certificate, context) == ()


def test_derived_candidate_with_valid_parent_lineage_accepted() -> None:
    parent = make_certificate(candidate_id="parent-1")
    context = make_context(parent_certificates={"parent-1": parent})
    derived = make_certificate(
        candidate_id="c-2",
        source_kind=SourceKind.AI_SUGGESTION,
        lineage_parent_ids=("parent-1",),
    )
    assert validate_certificate(derived, context) == ()


def test_derived_candidate_with_invalid_parent_rejected() -> None:
    parent = make_certificate(candidate_id="parent-1", evidence_hash="ff" * 32)
    context = make_context(parent_certificates={"parent-1": parent})
    derived = make_certificate(
        candidate_id="c-2",
        source_kind=SourceKind.AI_SUGGESTION,
        lineage_parent_ids=("parent-1",),
    )
    failures = validate_certificate(derived, context)
    assert any(failure.code == "INCOMPLETE_LINEAGE" for failure in failures)


def test_high_confidence_never_compensates_for_broken_integrity() -> None:
    certificate = make_certificate(confidence=0.99, evidence_hash="ff" * 32)
    decision = TransitionPolicy().route(certificate, make_context())
    assert decision.route is ReviewRoute.REJECT_REACQUIRE
    assert any(
        failure.code == "EVIDENCE_HASH_MISMATCH" for failure in decision.failures
    )


def test_nan_confidence_never_routes_to_standard() -> None:
    certificate = make_certificate(confidence=float("nan"))
    decision = TransitionPolicy().route(certificate, make_context())
    assert decision.route is ReviewRoute.REJECT_REACQUIRE
    assert any(failure.code == "INVALID_CONFIDENCE" for failure in decision.failures)


def test_routing_standard_for_low_risk_valid_certificate() -> None:
    decision = TransitionPolicy().route(make_certificate(), make_context())
    assert decision.route is ReviewRoute.STANDARD_REVIEW
    assert decision.failures == ()
    assert decision.risk_score is not None


def test_routing_enhanced_for_uncertain_candidate() -> None:
    certificate = make_certificate(confidence=0.52)
    assert (
        TransitionPolicy().route(certificate, make_context()).route
        is ReviewRoute.ENHANCED_REVIEW
    )


def test_routing_enhanced_for_disagreement() -> None:
    assert (
        TransitionPolicy().route(
            make_certificate(), make_context(), disagreement=True
        ).route
        is ReviewRoute.ENHANCED_REVIEW
    )


def test_routing_enhanced_for_weak_evidence() -> None:
    assert (
        TransitionPolicy().route(
            make_certificate(), make_context(), weak_evidence=True
        ).route
        is ReviewRoute.ENHANCED_REVIEW
    )


def test_routing_enhanced_for_abstained_candidate() -> None:
    certificate = make_certificate(
        value=None, confidence=0.0, selection_state=SelectionState.ABSTAINED
    )
    decision = TransitionPolicy().route(certificate, make_context())
    assert decision.route is ReviewRoute.ENHANCED_REVIEW


def test_routing_reject_reacquire_for_stale_version() -> None:
    certificate = make_certificate(expected_fact_version=1)
    context = make_context(current_fact_version=2)
    decision = TransitionPolicy().route(certificate, context)
    assert decision.route is ReviewRoute.REJECT_REACQUIRE
    assert any(
        failure.code == "STALE_FACT_VERSION" for failure in decision.failures
    )


def test_risk_score_follows_config_weights() -> None:
    policy = TransitionPolicy(
        RoutingConfig(
            confidence_threshold=0.6,
            weight_uncertainty=0.5,
            weight_integrity=0.2,
            weight_provenance=0.1,
            weight_freshness=0.1,
            weight_disagreement=0.1,
        )
    )
    certificate = make_certificate(confidence=0.97)
    plain = policy.route(certificate, make_context())
    assert plain.risk_score == pytest.approx(0.5 * 0.03)
    with_disagreement = policy.route(
        certificate, make_context(), disagreement=True
    )
    assert with_disagreement.risk_score == pytest.approx(0.5 * 0.03 + 0.1)


def test_authorize_creates_transition_when_all_terms_present() -> None:
    policy = TransitionPolicy()
    certificate = make_certificate()
    result = policy.authorize(make_decision(), certificate, make_context())
    assert result.allowed
    assert result.failures == ()
    assert result.transition is not None
    assert result.created_version == 2
    assert result.transition.certificate_id == certificate.certificate_id
    assert result.transition.decision_id == "d-1"
    assert result.transition.evidence_sha256 == EVIDENCE_HASH


def test_authorize_requires_attributable_decision() -> None:
    policy = TransitionPolicy()
    for overrides in ({"reviewer_id": ""}, {"reason": ""}):
        result = policy.authorize(
            make_decision(**overrides), make_certificate(), make_context()
        )
        assert not result.allowed
        assert result.transition is None
        assert any(
            failure.code == "UNATTRIBUTED_DECISION" for failure in result.failures
        )


def test_authorize_requires_decision_candidate_binding() -> None:
    result = TransitionPolicy().authorize(
        make_decision(candidate_id="other-candidate"),
        make_certificate(),
        make_context(),
    )
    assert not result.allowed
    assert any(
        failure.code == "DECISION_CANDIDATE_MISMATCH" for failure in result.failures
    )


def test_authorize_rejects_abstained_without_manual_resolution() -> None:
    certificate = make_certificate(
        value=None, confidence=0.0, selection_state=SelectionState.ABSTAINED
    )
    result = TransitionPolicy().authorize(
        make_decision(), certificate, make_context()
    )
    assert not result.allowed
    assert any(
        failure.code == "ABSTAINED_UNRESOLVED" for failure in result.failures
    )


def test_authorize_allows_abstained_with_manual_resolution() -> None:
    certificate = make_certificate(
        value=None, confidence=0.0, selection_state=SelectionState.ABSTAINED
    )
    result = TransitionPolicy().authorize(
        make_decision(manual_resolution=True), certificate, make_context()
    )
    assert result.allowed
    assert result.transition is not None
    assert result.transition.created_version == 2


def test_stale_decision_rejected_without_modifying_fact() -> None:
    certificate = make_certificate(expected_fact_version=1)
    context = make_context(current_fact_version=2)
    result: FactTransitionResult = TransitionPolicy().authorize(
        make_decision(), certificate, context
    )
    assert not result.allowed
    assert result.transition is None
    assert any(
        failure.code == "STALE_FACT_VERSION" for failure in result.failures
    )


def test_rejection_is_explicit_and_leaves_fact_unchanged() -> None:
    certificate = make_certificate(evidence_hash="ff" * 32)
    result = TransitionPolicy().authorize(
        make_decision(), certificate, make_context()
    )
    assert not result.allowed
    assert result.transition is None
    assert any(
        failure.integrity is IntegrityKind.EVIDENCE for failure in result.failures
    )


def test_no_machine_only_fact_transition_exists() -> None:
    policy = TransitionPolicy()
    certificate = make_certificate()
    context = make_context()
    routing = policy.route(certificate, context)
    assert routing.route is ReviewRoute.STANDARD_REVIEW
    with pytest.raises(TypeError):
        policy.authorize(certificate, context)  # type: ignore[call-arg]
    for obj in (policy, certificate):
        for method in ("add_record_version", "confirm", "correct", "write_fact", "apply"):
            assert not hasattr(obj, method)


def test_model_substitutability_preserves_contract() -> None:
    policy = TransitionPolicy()
    context = make_context()
    cert_a = make_certificate()
    cert_b = make_certificate(
        candidate_id="c-2",
        producer_id="recognizer-b",
        producer_version="2.0",
        selection_artifact_id="cal-2",
    )
    assert validate_certificate(cert_a, context) == ()
    assert validate_certificate(cert_b, context) == ()
    assert policy.route(cert_a, context).route is policy.route(cert_b, context).route
    result_a = policy.authorize(make_decision(), cert_a, context)
    result_b = policy.authorize(
        make_decision(decision_id="d-2", candidate_id="c-2"), cert_b, context
    )
    assert result_a.allowed and result_b.allowed
    assert result_a.transition is not None and result_b.transition is not None
    assert result_a.transition.created_version == result_b.transition.created_version == 2


def test_provenance_trace_complete_when_all_bindings_hold() -> None:
    policy = TransitionPolicy()
    certificate = make_certificate()
    decision = make_decision()
    context = make_context()
    result = policy.authorize(decision, certificate, context)
    assert result.transition is not None
    trace = build_provenance_trace(
        result.transition, decision, certificate, context.evidence_sha256
    )
    assert trace.complete
    assert [hop.hop for hop in trace.hops] == ["F", "H", "C", "E"]
    assert trace.failures == ()


def test_provenance_trace_detects_broken_bindings() -> None:
    certificate = make_certificate()
    decision = make_decision(candidate_id="other-candidate")
    forged = FactTransition(
        transition_id="forged:2",
        record_id="REC-1",
        field_key=certificate.field_key,
        created_version=2,
        record_version_id="REC-1",
        decision_id="d-1",
        certificate_id=certificate.certificate_id,
        evidence_sha256=EVIDENCE_HASH,
        evidence_locator=certificate.evidence_locator,
        producer_id=certificate.producer_id,
        producer_version=certificate.producer_version,
        source_kind=certificate.source_kind,
        template_id=certificate.template_id,
        template_version=certificate.template_version,
        created_at=NOW,
    )
    trace = build_provenance_trace(forged, decision, certificate, EVIDENCE_HASH)
    assert not trace.complete
    assert any("decision" in failure for failure in trace.failures)


def test_verify_transition_attempt_with_full_contract_passes() -> None:
    policy = TransitionPolicy()
    certificate = make_certificate()
    decision = make_decision()
    context = make_context()
    result = policy.authorize(decision, certificate, context)
    assert result.transition is not None
    attempt = TransitionAttempt(
        fact_version=result.transition.created_version,
        record_id=result.transition.record_id,
        evidence_sha256=context.evidence_sha256,
        decision=decision,
        certificate=certificate,
    )
    assert verify_transition_authorization(attempt, context) == ()


def test_verify_transition_attempt_missing_decision_and_certificate() -> None:
    attempt = TransitionAttempt(
        fact_version=2,
        record_id="REC-1",
        evidence_sha256=EVIDENCE_HASH,
        decision=None,
        certificate=None,
    )
    failures = verify_transition_authorization(attempt, make_context())
    codes = {failure.code for failure in failures}
    assert {"MISSING_DECISION", "MISSING_CERTIFICATE"}.issubset(codes)


def test_field_key_participates_in_content_address() -> None:
    # RED (Task A): field_key must be part of the certificate content address.
    a = make_certificate(field_key="total_quantity")
    b = make_certificate(field_key="qualified_quantity")
    assert a.certificate_id != b.certificate_id


def test_machine_selected_requires_selection_artifact() -> None:
    # RED (Task A): machine SELECTED without a registered artifact rejects.
    certificate = make_certificate(selection_artifact_id=None)
    failures = validate_certificate(certificate, make_context())
    assert any(
        failure.code == "MISSING_SELECTION_ARTIFACT" for failure in failures
    )


def test_manual_entry_certificate_valid_without_artifact() -> None:
    # RED (Task A): from_manual_entry factory; manual entry needs no artifact.
    certificate = CandidateCertificate.from_manual_entry(
        candidate_id="manual-1",
        field_key="total_quantity",
        value=7,
        form_id="FORM-1",
        evidence_hash=EVIDENCE_HASH,
        evidence_locator="FORM-1/manual/total_quantity",
        template_id="T1",
        template_version="1",
        target_record_id="FORM-1",
        expected_fact_version=1,
        created_at=NOW,
    )
    assert certificate.source_kind is SourceKind.MANUAL_ENTRY
    assert certificate.selection_state is SelectionState.SELECTED
    assert certificate.selection_artifact_id is None
    assert validate_certificate(certificate, make_context()) == ()


def test_from_persisted_preserves_stored_id() -> None:
    # RED (Task A): from_persisted keeps the stored certificate id so
    # verify_content_address() detects diverged rows.
    original = make_certificate()
    fields = {
        "candidate_id": original.candidate_id,
        "field_key": original.field_key,
        "value_payload": original.value_payload,
        "evidence_hash": original.evidence_hash,
        "evidence_locator": original.evidence_locator,
        "template_id": original.template_id,
        "template_version": original.template_version,
        "source_kind": original.source_kind,
        "producer_id": original.producer_id,
        "producer_version": original.producer_version,
        "selection_artifact_id": original.selection_artifact_id,
        "confidence": original.confidence,
        "selection_state": original.selection_state,
        "lineage_parent_ids": original.lineage_parent_ids,
        "target_record_id": original.target_record_id,
        "expected_fact_version": original.expected_fact_version,
        "created_at": original.created_at,
    }
    loaded = CandidateCertificate.from_persisted(
        stored_certificate_id=original.certificate_id, **fields
    )
    assert loaded.verify_content_address() is True
    tampered = CandidateCertificate.from_persisted(
        stored_certificate_id=original.certificate_id,
        **{**fields, "field_key": "other_field"},
    )
    assert tampered.verify_content_address() is False


def test_verify_transition_attempt_detects_unattributed_decision() -> None:
    certificate = make_certificate()
    decision = make_decision(reviewer_id="")
    attempt = TransitionAttempt(
        fact_version=2,
        record_id="REC-1",
        evidence_sha256=EVIDENCE_HASH,
        decision=decision,
        certificate=certificate,
    )
    failures = verify_transition_authorization(attempt, make_context())
    assert any(failure.code == "UNATTRIBUTED_DECISION" for failure in failures)


def test_verify_attempt_rejects_wrong_record_id() -> None:
    certificate = make_certificate()
    attempt = TransitionAttempt(
        fact_version=2,
        record_id="OTHER-RECORD",
        evidence_sha256=EVIDENCE_HASH,
        decision=make_decision(),
        certificate=certificate,
    )
    failures = verify_transition_authorization(attempt, make_context())
    assert any(failure.code == "RECORD_BINDING_MISMATCH" for failure in failures)


def test_verify_attempt_rejects_wrong_fact_version() -> None:
    certificate = make_certificate()
    attempt = TransitionAttempt(
        fact_version=999,
        record_id="REC-1",
        evidence_sha256=EVIDENCE_HASH,
        decision=make_decision(),
        certificate=certificate,
    )
    failures = verify_transition_authorization(attempt, make_context())
    assert any(failure.code == "FACT_VERSION_MISMATCH" for failure in failures)


def test_verify_attempt_rejects_empty_decision_id() -> None:
    certificate = make_certificate()
    attempt = TransitionAttempt(
        fact_version=2,
        record_id="REC-1",
        evidence_sha256=EVIDENCE_HASH,
        decision=make_decision(decision_id=""),
        certificate=certificate,
    )
    failures = verify_transition_authorization(attempt, make_context())
    assert any(failure.code == "EMPTY_DECISION_ID" for failure in failures)


def test_verify_attempt_rejects_naive_decision_timestamp() -> None:
    certificate = make_certificate()
    attempt = TransitionAttempt(
        fact_version=2,
        record_id="REC-1",
        evidence_sha256=EVIDENCE_HASH,
        decision=make_decision(decided_at=datetime(2026, 8, 16, 12, 0)),
        certificate=certificate,
    )
    failures = verify_transition_authorization(attempt, make_context())
    assert any(failure.code == "NAIVE_TIMESTAMP" for failure in failures)


def test_verify_attempt_rejects_decision_predating_certificate() -> None:
    certificate = make_certificate()
    attempt = TransitionAttempt(
        fact_version=2,
        record_id="REC-1",
        evidence_sha256=EVIDENCE_HASH,
        decision=make_decision(decided_at=NOW - timedelta(hours=1)),
        certificate=certificate,
    )
    failures = verify_transition_authorization(attempt, make_context())
    assert any(
        failure.code == "DECISION_PREDATES_CERTIFICATE" for failure in failures
    )


def test_verify_attempt_rejects_decision_in_future() -> None:
    certificate = make_certificate()
    attempt = TransitionAttempt(
        fact_version=2,
        record_id="REC-1",
        evidence_sha256=EVIDENCE_HASH,
        decision=make_decision(decided_at=NOW + timedelta(hours=1)),
        certificate=certificate,
    )
    failures = verify_transition_authorization(attempt, make_context())
    assert any(failure.code == "DECISION_IN_FUTURE" for failure in failures)


def test_is_aware_timestamp_helper() -> None:
    from app.domain.authority import is_aware_timestamp

    assert is_aware_timestamp(NOW) is True
    assert is_aware_timestamp(datetime(2026, 8, 16, 12, 0)) is False
    assert is_aware_timestamp(PSEUDO_NAIVE) is False


def test_pseudo_naive_certificate_timestamp_rejected() -> None:
    certificate = make_certificate(created_at=PSEUDO_NAIVE)
    failures = validate_certificate(certificate, make_context())
    assert any(failure.code == "NAIVE_TIMESTAMP" for failure in failures)


def test_pseudo_naive_context_reference_time_rejected() -> None:
    certificate = make_certificate()
    context = make_context(now=PSEUDO_NAIVE)
    failures = validate_certificate(certificate, context)
    assert any(failure.code == "NAIVE_TIMESTAMP" for failure in failures)


def test_authorize_rejects_pseudo_naive_decision_timestamp() -> None:
    result = TransitionPolicy().authorize(
        make_decision(decided_at=PSEUDO_NAIVE),
        make_certificate(),
        make_context(),
    )
    assert not result.allowed
    assert any(failure.code == "NAIVE_TIMESTAMP" for failure in result.failures)


def test_authorize_rejects_pseudo_naive_certificate_without_exception() -> None:
    result = TransitionPolicy().authorize(
        make_decision(),
        make_certificate(created_at=PSEUDO_NAIVE),
        make_context(),
    )
    assert not result.allowed
    assert any(failure.code == "NAIVE_TIMESTAMP" for failure in result.failures)


def test_verify_rejects_pseudo_naive_decision_timestamp() -> None:
    certificate = make_certificate()
    attempt = TransitionAttempt(
        fact_version=2,
        record_id="REC-1",
        evidence_sha256=EVIDENCE_HASH,
        decision=make_decision(decided_at=PSEUDO_NAIVE),
        certificate=certificate,
    )
    failures = verify_transition_authorization(attempt, make_context())
    assert any(failure.code == "NAIVE_TIMESTAMP" for failure in failures)


def test_trace_rejects_pseudo_naive_transition_timestamp() -> None:
    certificate = make_certificate()
    decision = make_decision()
    forged = FactTransition(
        transition_id="forged:2",
        record_id="REC-1",
        field_key=certificate.field_key,
        created_version=2,
        record_version_id="REC-1",
        decision_id="d-1",
        certificate_id=certificate.certificate_id,
        evidence_sha256=EVIDENCE_HASH,
        evidence_locator=certificate.evidence_locator,
        producer_id=certificate.producer_id,
        producer_version=certificate.producer_version,
        source_kind=certificate.source_kind,
        template_id=certificate.template_id,
        template_version=certificate.template_version,
        created_at=PSEUDO_NAIVE,
    )
    trace = build_provenance_trace(forged, decision, certificate, EVIDENCE_HASH)
    assert not trace.complete
    assert any("naive timestamp" in failure for failure in trace.failures)


def test_naive_certificate_timestamp_rejected() -> None:
    certificate = make_certificate(created_at=datetime(2026, 8, 16, 12, 0))
    failures = validate_certificate(certificate, make_context())
    assert any(failure.code == "NAIVE_TIMESTAMP" for failure in failures)


def test_naive_context_reference_time_rejected() -> None:
    certificate = make_certificate()
    context = make_context(now=datetime(2026, 8, 16, 12, 0))
    failures = validate_certificate(certificate, context)
    assert any(failure.code == "NAIVE_TIMESTAMP" for failure in failures)


def test_authorize_rejects_empty_decision_id() -> None:
    result = TransitionPolicy().authorize(
        make_decision(decision_id=""), make_certificate(), make_context()
    )
    assert not result.allowed
    assert any(failure.code == "EMPTY_DECISION_ID" for failure in result.failures)


def test_authorize_rejects_naive_decision_timestamp() -> None:
    result = TransitionPolicy().authorize(
        make_decision(decided_at=datetime(2026, 8, 16, 12, 0)),
        make_certificate(),
        make_context(),
    )
    assert not result.allowed
    assert any(failure.code == "NAIVE_TIMESTAMP" for failure in result.failures)


def test_authorize_rejects_decision_predating_certificate() -> None:
    result = TransitionPolicy().authorize(
        make_decision(decided_at=NOW - timedelta(hours=1)),
        make_certificate(),
        make_context(),
    )
    assert not result.allowed
    assert any(
        failure.code == "DECISION_PREDATES_CERTIFICATE" for failure in result.failures
    )


def test_authorize_rejects_decision_in_future() -> None:
    result = TransitionPolicy().authorize(
        make_decision(decided_at=NOW + timedelta(hours=1)),
        make_certificate(),
        make_context(),
    )
    assert not result.allowed
    assert any(failure.code == "DECISION_IN_FUTURE" for failure in result.failures)


def test_trace_detects_tampered_transition_fields() -> None:
    certificate = make_certificate()
    decision = make_decision()
    forged = FactTransition(
        transition_id="forged:2",
        record_id="OTHER-RECORD",
        field_key=certificate.field_key,
        created_version=999,
        record_version_id="REC-1",
        decision_id="d-1",
        certificate_id=certificate.certificate_id,
        evidence_sha256=EVIDENCE_HASH,
        evidence_locator="other-locator",
        producer_id="other-producer",
        producer_version="9.9",
        source_kind=SourceKind.RETRIEVAL,
        template_id="OTHER-T",
        template_version="9",
        created_at=NOW,
    )
    trace = build_provenance_trace(forged, decision, certificate, EVIDENCE_HASH)
    assert not trace.complete
    assert "transition record binding mismatch" in trace.failures
    assert "transition version mismatch" in trace.failures
    assert "transition producer binding mismatch" in trace.failures
    assert "transition producer version mismatch" in trace.failures
    assert "transition template binding mismatch" in trace.failures
    assert "transition template version mismatch" in trace.failures
    assert "transition source kind mismatch" in trace.failures
    assert "transition evidence locator mismatch" in trace.failures


def test_trace_detects_timestamp_ordering_violations() -> None:
    certificate = make_certificate()
    decision = make_decision()
    forged = FactTransition(
        transition_id="forged:2",
        record_id="REC-1",
        field_key=certificate.field_key,
        created_version=2,
        record_version_id="REC-1",
        decision_id="d-1",
        certificate_id=certificate.certificate_id,
        evidence_sha256=EVIDENCE_HASH,
        evidence_locator=certificate.evidence_locator,
        producer_id=certificate.producer_id,
        producer_version=certificate.producer_version,
        source_kind=certificate.source_kind,
        template_id=certificate.template_id,
        template_version=certificate.template_version,
        created_at=NOW - timedelta(hours=1),
    )
    trace = build_provenance_trace(forged, decision, certificate, EVIDENCE_HASH)
    assert not trace.complete
    assert "transition predates decision" in trace.failures


def test_trace_rejects_naive_timestamps() -> None:
    certificate = make_certificate(created_at=datetime(2026, 8, 16, 12, 0))
    decision = make_decision()
    forged = FactTransition(
        transition_id="forged:2",
        record_id="REC-1",
        field_key=certificate.field_key,
        created_version=2,
        record_version_id="REC-1",
        decision_id="d-1",
        certificate_id=certificate.certificate_id,
        evidence_sha256=EVIDENCE_HASH,
        evidence_locator=certificate.evidence_locator,
        producer_id=certificate.producer_id,
        producer_version=certificate.producer_version,
        source_kind=certificate.source_kind,
        template_id=certificate.template_id,
        template_version=certificate.template_version,
        created_at=NOW,
    )
    trace = build_provenance_trace(forged, decision, certificate, EVIDENCE_HASH)
    assert not trace.complete
    assert any("naive timestamp" in failure for failure in trace.failures)

def test_verify_attempt_rejects_field_key_binding_mismatch() -> None:
    # REVISE P0-1: decision.field_key must equal certificate.field_key.
    certificate = make_certificate()
    attempt = TransitionAttempt(
        fact_version=2,
        record_id="REC-1",
        evidence_sha256=EVIDENCE_HASH,
        decision=make_decision(field_key="other_field"),
        certificate=certificate,
    )
    failures = verify_transition_authorization(attempt, make_context())
    assert any(
        failure.code == "FIELD_KEY_BINDING_MISMATCH" for failure in failures
    )


def test_verify_attempt_field_binding_ok_when_keys_agree() -> None:
    certificate = make_certificate()
    attempt = TransitionAttempt(
        fact_version=2,
        record_id="REC-1",
        evidence_sha256=EVIDENCE_HASH,
        decision=make_decision(),
        certificate=certificate,
    )
    assert verify_transition_authorization(attempt, make_context()) == ()


def test_trace_detects_field_binding_mismatches() -> None:
    # REVISE P0-1: build_provenance_trace binds decision/transition field
    # keys to the certificate field key.
    certificate = make_certificate()
    decision = make_decision(field_key="other_field")
    forged = FactTransition(
        transition_id="forged:2",
        record_id="REC-1",
        field_key="yet_another_field",
        created_version=2,
        record_version_id="REC-1",
        decision_id="d-1",
        certificate_id=certificate.certificate_id,
        evidence_sha256=EVIDENCE_HASH,
        evidence_locator=certificate.evidence_locator,
        producer_id=certificate.producer_id,
        producer_version=certificate.producer_version,
        source_kind=certificate.source_kind,
        template_id=certificate.template_id,
        template_version=certificate.template_version,
        created_at=NOW,
    )
    trace = build_provenance_trace(forged, decision, certificate, EVIDENCE_HASH)
    assert not trace.complete
    assert "decision field binding mismatch" in trace.failures
    assert "transition field binding mismatch" in trace.failures
    assert "transition decision field mismatch" in trace.failures
