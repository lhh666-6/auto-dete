"""Deterministic authority-contract benchmarks (round 2).

Two separate experiments, per the round-2 review:

1. **Architecture safety** (`run_architecture_safety`): three isolated
   architectures (A direct write / B ordinary confirmation / C authority
   contract) process an identical, unified case set (27 fixed scenarios
   including fail-closed probes + a 200-case seeded pool). No simulated
   reviewer: facts either exist or not, and every created fact is
   re-verified against the contract through `verify_transition_authorization`
   and a real `ProvenanceTrace` traversal. All denominators are identical.

2. **Routing experiment** (`run_routing_experiment`): inside architecture C
   only, uniform-first-k review vs. risk-budgeted review at matched review
   budgets, using one shared simulated-reviewer detection model per case.
   Runs across 3 wrongness modes (correlated / uncorrelated / adversarial)
   and 16 evaluation seeds, reporting means, win rates, and 95% CI deltas.
   Routing weights are chosen by an executable calibration grid search on
   the disjoint calibration split (seed 424242) before evaluation.

Round-2 fixes: fail-closed certificate probes are part of the case set;
`unauthorized` and `reverse_trace_completeness` are measured, never
hard-coded; case sets and denominators are unified across architectures;
reviewer quality cannot leak across architectures because only experiment 2
uses a simulated reviewer, and only inside architecture C.
"""

import argparse
import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass, is_dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

from app.application.transition_policy import (
    FactTransitionResult,
    HumanDecision,
    ReviewRoute,
    RoutingConfig,
    TransitionPolicy,
)
from app.domain.authority import (
    AuthorityContext,
    CandidateCertificate,
    ProvenanceTrace,
    SelectionState,
    SourceKind,
    TransitionAttempt,
    build_provenance_trace,
    validate_certificate,
    verify_transition_authorization,
)

NOW = datetime(2026, 8, 16, 12, 0, tzinfo=UTC)
EVIDENCE_HASH = "ab" * 32
MAX_CERTIFICATE_AGE = timedelta(hours=1)

POOL_SIZE = 200
POOL_SEED = 20260816  # safety-experiment pool
ARCH_SEED = 3001  # fixed-scenario reviewer draws (unused by safety metrics)
CALIBRATION_SEED = 424242  # routing-parameter selection split
EVAL_SEEDS = tuple(range(20260816, 20260832))  # 16 held-out evaluation seeds

# Simulated-reviewer detection probabilities (fixed, identical for both
# routing policies; used only inside the routing experiment).
DETECT_STANDARD = 0.45
DETECT_ENHANCED = 0.93

BUDGETS = (0.25, 0.5, 0.75, 1.0)

WRONG_MODES = ("correlated", "uncorrelated", "adversarial")

KNOWN_SOURCES = frozenset(
    {
        SourceKind.RECOGNITION,
        SourceKind.RETRIEVAL,
        SourceKind.AI_SUGGESTION,
        SourceKind.MANUAL_ENTRY,
    }
)
KNOWN_PRODUCERS = frozenset({("recognizer-a", "1.0"), ("recognizer-b", "2.0")})
KNOWN_SELECTION_ARTIFACTS = frozenset({"cal-1", "cal-2"})

INVALID_TRANSITION_FAMILIES = frozenset(
    {
        "stale_version",
        "evidence_mismatch",
        "missing_locator",
        "unknown_producer",
        "missing_calibration",
        "incomplete_lineage",
        "expired_certificate",
        "missing_evidence_hash",
        "unknown_calibration",
        "abstained_forced",
        "decision_mismatch",
        "confidence_nan",
        "confidence_out_of_range",
        "empty_candidate_id",
        "empty_template",
        "empty_target_record",
        "future_timestamp",
    }
)
INDEPENDENT_FAULT_FAMILIES = frozenset({"wrong_value"})

# N3 verdict rule (pre-specified before the reported run; see round-3 notes —
# constants in the same commit as the results cannot prove formal
# pre-registration): the correlated mode must show a stable matched-budget
# advantage (win rate >= 0.8 at budgets 0.25 and 0.5, positive mean delta at
# 0.25/0.5/0.75, and never-worse rate >= 0.7 at 0.75), and the uncorrelated
# mode must not show systematic degradation (mean delta at 0.5 >= -0.2). The
# adversarial mode is reported and does not gate the verdict.
N3_WIN_RATE_THRESHOLD = 0.8
N3_NEVER_WORSE_THRESHOLD = 0.7
N3_UNCORRELATED_DELTA_FLOOR = -0.2


@dataclass(frozen=True, slots=True)
class Scenario:
    case_id: str
    fault: str
    fault_independent: bool
    truth_value: int | None
    candidate_value: int | None
    certificate: CandidateCertificate
    evidence_sha256: str
    current_fact_version: int
    disagreement: bool
    weak_evidence: bool
    reviewer_draw: float
    decision_candidate_override: str | None = None


@dataclass(frozen=True, slots=True)
class CaseOutcome:
    case_id: str
    architecture: str
    fault: str
    fault_independent: bool
    route: str
    rejected: bool
    rejection_codes: tuple[str, ...]
    fact_created: bool
    unauthorized: bool
    trace_complete: bool
    transition_id: str | None


@dataclass(frozen=True, slots=True)
class ArchitectureResult:
    architecture: str
    cases: int
    facts_created: int
    unauthorized_transitions: int
    invalid_transition_rejection_rate: float
    valid_certificate_coverage: float
    reverse_trace_completeness: float
    stale_transition_containment: float
    p1_probe_attempts: int
    p1_probe_blocked: int


@dataclass(frozen=True, slots=True)
class BudgetRow:
    budget: float
    policy: str
    reviewed: int
    wrong_reviewed: int
    escapes: int
    corrected: int
    pending: int


@dataclass(frozen=True, slots=True)
class RoutingSeedRow:
    mode: str
    seed: int
    budget: float
    standard_escapes: int
    risk_escapes: int


@dataclass(frozen=True, slots=True)
class RoutingAggregate:
    mode: str
    budget: float
    seeds: int
    standard_mean: float
    risk_mean: float
    mean_delta: float
    delta_ci: float
    win_rate: float
    never_worse_rate: float


@dataclass(frozen=True, slots=True)
class CalibrationRow:
    confidence_threshold: float
    weight_uncertainty: float
    standard_escapes: int
    risk_escapes: int
    advantage: int


@dataclass(frozen=True, slots=True)
class ProducerSummary:
    producer_id: str
    producer_version: str
    cases: int
    standard_routes: int
    enhanced_routes: int
    rejected: int
    allowed: int


def _write_json(path: Path, rows: Iterable[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    def jsonable(value: Any) -> Any:
        if is_dataclass(value) and not isinstance(value, type):
            return asdict(value)
        return value

    payload = [jsonable(row) for row in rows]
    encoded = (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=_default) + "\n"
    ).encode("utf-8")
    path.write_bytes(encoded)


def _default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, str):
        return value
    return str(value)


def _certificate(
    *,
    case_id: str,
    candidate_id: str | None = None,
    value: int | None,
    confidence: float,
    source_kind: SourceKind = SourceKind.RECOGNITION,
    producer_id: str = "recognizer-a",
    producer_version: str = "1.0",
    evidence_hash: str = EVIDENCE_HASH,
    evidence_locator: str = "form-1/page-1/field:total_quantity",
    template_id: str = "T1",
    template_version: str = "1",
    field_key: str = "total_quantity",
    selection_artifact_id: str | None = "cal-1",
    selection: SelectionState = SelectionState.SELECTED,
    lineage: tuple[str, ...] = (),
    target: str = "REC-1",
    expected_version: int = 1,
    created_at: datetime = NOW,
) -> CandidateCertificate:
    return CandidateCertificate.from_value(
        candidate_id=case_id if candidate_id is None else candidate_id,
        field_key=field_key,
        value=value,
        evidence_hash=evidence_hash,
        evidence_locator=evidence_locator,
        template_id=template_id,
        template_version=template_version,
        source_kind=source_kind,
        producer_id=producer_id,
        producer_version=producer_version,
        selection_artifact_id=selection_artifact_id,
        confidence=confidence,
        selection_state=selection,
        lineage_parent_ids=lineage,
        target_record_id=target,
        expected_fact_version=expected_version,
        created_at=created_at,
    )


def _fixed_scenarios() -> list[Scenario]:
    rng = np.random.default_rng(ARCH_SEED)

    def make(
        case_id: str,
        fault: str,
        truth: int | None,
        certificate: CandidateCertificate,
        *,
        independent: bool = False,
        evidence: str = EVIDENCE_HASH,
        version: int = 1,
        disagreement: bool = False,
        weak: bool = False,
        override: str | None = None,
    ) -> Scenario:
        return Scenario(
            case_id=case_id,
            fault=fault,
            fault_independent=independent,
            truth_value=truth,
            candidate_value=certificate.value,
            certificate=certificate,
            evidence_sha256=evidence,
            current_fact_version=version,
            disagreement=disagreement,
            weak_evidence=weak,
            reviewer_draw=float(rng.random()),
            decision_candidate_override=override,
        )

    scenarios = [
        make("s-01", "none", 7, _certificate(case_id="s-01", value=7, confidence=0.97)),
        make("s-02", "none", 7, _certificate(case_id="s-02", value=7, confidence=0.52)),
        make(
            "s-03",
            "none",
            7,
            _certificate(case_id="s-03", value=7, confidence=0.95),
            disagreement=True,
        ),
        make(
            "s-04",
            "wrong_value",
            7,
            _certificate(case_id="s-04", value=999, confidence=0.97),
            independent=True,
        ),
        make(
            "s-05",
            "wrong_value",
            7,
            _certificate(case_id="s-05", value=999, confidence=0.42),
            independent=True,
        ),
        make(
            "s-06",
            "stale_version",
            7,
            _certificate(case_id="s-06", value=7, confidence=0.97, expected_version=1),
            version=2,
        ),
        make(
            "s-07",
            "evidence_mismatch",
            7,
            _certificate(case_id="s-07", value=7, confidence=0.97, evidence_hash="ff" * 32),
        ),
        make(
            "s-08",
            "missing_locator",
            7,
            _certificate(case_id="s-08", value=7, confidence=0.97, evidence_locator=""),
        ),
        make(
            "s-09",
            "unknown_producer",
            7,
            _certificate(
                case_id="s-09",
                value=7,
                confidence=0.97,
                producer_id="mystery-engine",
                producer_version="9.9",
            ),
        ),
        make(
            "s-10",
            "missing_calibration",
            7,
            _certificate(case_id="s-10", value=7, confidence=0.97, selection_artifact_id=None),
        ),
        make(
            "s-11",
            "incomplete_lineage",
            7,
            _certificate(
                case_id="s-11",
                value=7,
                confidence=0.9,
                source_kind=SourceKind.AI_SUGGESTION,
                lineage=("missing-parent",),
            ),
        ),
        make(
            "s-12",
            "abstained_forced",
            7,
            _certificate(
                case_id="s-12",
                value=None,
                confidence=0.0,
                selection=SelectionState.ABSTAINED,
            ),
        ),
        make(
            "s-13",
            "abstained_resolved",
            7,
            _certificate(
                case_id="s-13",
                value=None,
                confidence=0.0,
                selection=SelectionState.ABSTAINED,
            ),
        ),
        make(
            "s-14",
            "expired_certificate",
            7,
            _certificate(
                case_id="s-14",
                value=7,
                confidence=0.97,
                created_at=NOW - timedelta(hours=2),
            ),
        ),
        make(
            "s-15",
            "none",
            7,
            _certificate(
                case_id="s-15",
                value=7,
                confidence=0.9,
                producer_id="recognizer-b",
                producer_version="2.0",
                selection_artifact_id="cal-2",
            ),
        ),
        make(
            "s-16",
            "wrong_value",
            7,
            _certificate(
                case_id="s-16",
                value=999,
                confidence=0.97,
                producer_id="recognizer-b",
                producer_version="2.0",
                selection_artifact_id="cal-2",
            ),
            independent=True,
        ),
        make(
            "s-17",
            "missing_evidence_hash",
            7,
            _certificate(case_id="s-17", value=7, confidence=0.97, evidence_hash=""),
        ),
        make(
            "s-18",
            "unknown_calibration",
            7,
            _certificate(
                case_id="s-18", value=7, confidence=0.97, selection_artifact_id="cal-none"
            ),
        ),
        make(
            "s-19",
            "none",
            7,
            _certificate(case_id="s-19", value=7, confidence=0.9),
            weak=True,
        ),
        make(
            "s-20",
            "decision_mismatch",
            7,
            _certificate(case_id="s-20", value=7, confidence=0.97),
            override="other-candidate",
        ),
        # Round-2 fail-closed probes.
        make(
            "s-22",
            "confidence_nan",
            7,
            _certificate(case_id="s-22", value=7, confidence=float("nan")),
        ),
        make(
            "s-23",
            "confidence_out_of_range",
            7,
            _certificate(case_id="s-23", value=7, confidence=2.0),
        ),
        make(
            "s-24",
            "empty_candidate_id",
            7,
            _certificate(case_id="s-24", value=7, confidence=0.97, candidate_id=""),
        ),
        make(
            "s-25",
            "empty_template",
            7,
            _certificate(case_id="s-25", value=7, confidence=0.97, template_id=""),
        ),
        make(
            "s-26",
            "empty_target_record",
            7,
            _certificate(case_id="s-26", value=7, confidence=0.97, target=""),
        ),
        make(
            "s-27",
            "future_timestamp",
            7,
            _certificate(
                case_id="s-27",
                value=7,
                confidence=0.97,
                created_at=NOW + timedelta(hours=2),
            ),
        ),
    ]
    derived = make(
        "s-21",
        "none",
        7,
        _certificate(
            case_id="s-21",
            value=7,
            confidence=0.91,
            source_kind=SourceKind.AI_SUGGESTION,
            lineage=("s-01",),
        ),
    )
    scenarios.append(derived)
    return scenarios


def _wrong_probability(mode: str, confidence: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    if mode == "correlated":
        return 0.10 + 0.55 * (1.0 - confidence)
    if mode == "uncorrelated":
        return np.full(confidence.shape, 0.20)
    if mode == "adversarial":
        return 0.05 + 0.55 * confidence
    raise ValueError(f"unknown wrongness mode: {mode}")


def _disagreement_probability(mode: str, wrong: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    if mode == "uncorrelated":
        return np.full(wrong.shape, 0.13)
    return 0.05 + 0.4 * wrong


def _pool_scenarios(seed: int, mode: str) -> list[Scenario]:
    """Seeded candidate pool with value-level fault injection.

    Generation order is fixed: confidence, wrongness (mode-dependent),
    disagreement, then the per-case reviewer draw. Wrong values come from an
    independent value generator that knows nothing about certificate rules.
    """
    rng = np.random.default_rng(seed)
    confidences = rng.uniform(0.35, 0.99, POOL_SIZE)
    wrong = rng.random(POOL_SIZE) < _wrong_probability(mode, confidences)
    disagreement = rng.random(POOL_SIZE) < _disagreement_probability(mode, wrong)
    draws = rng.random(POOL_SIZE)
    scenarios: list[Scenario] = []
    for index in range(POOL_SIZE):
        truth = int(rng.integers(1, 100))
        value = int(rng.integers(1, 100)) if bool(wrong[index]) else truth
        producer_a = index % 2 == 0
        certificate = _certificate(
            case_id=f"pool-{index:03d}",
            value=value,
            confidence=float(confidences[index]),
            producer_id="recognizer-a" if producer_a else "recognizer-b",
            producer_version="1.0" if producer_a else "2.0",
            selection_artifact_id="cal-1" if index % 3 else "cal-2",
        )
        scenarios.append(
            Scenario(
                case_id=f"pool-{index:03d}",
                fault="wrong_value" if bool(wrong[index]) else "none",
                fault_independent=True,
                truth_value=truth,
                candidate_value=value,
                certificate=certificate,
                evidence_sha256=EVIDENCE_HASH,
                current_fact_version=1,
                disagreement=bool(disagreement[index]),
                weak_evidence=False,
                reviewer_draw=float(draws[index]),
            )
        )
    return scenarios


def _parents(scenarios: list[Scenario]) -> dict[str, CandidateCertificate]:
    return {
        scenario.certificate.candidate_id: scenario.certificate
        for scenario in scenarios
        if scenario.case_id == "s-01"
    }


def _context(scenario: Scenario, parents: dict[str, CandidateCertificate]) -> AuthorityContext:
    return AuthorityContext(
        evidence_sha256=scenario.evidence_sha256,
        current_fact_version=scenario.current_fact_version,
        known_sources=KNOWN_SOURCES,
        known_producers=KNOWN_PRODUCERS,
        known_selection_artifacts=KNOWN_SELECTION_ARTIFACTS,
        parent_certificates=parents,
        max_certificate_age=MAX_CERTIFICATE_AGE,
        now=NOW,
    )


def _decision(
    scenario: Scenario, architecture: str, *, manual_resolution: bool = False
) -> HumanDecision:
    return HumanDecision(
        decision_id=f"{scenario.case_id}:{architecture}",
        reviewer_id="reviewer-1",
        candidate_id=(scenario.decision_candidate_override or scenario.certificate.candidate_id),
        field_key=scenario.certificate.field_key,
        reason="accept candidate" if not manual_resolution else "manual resolution",
        decided_at=NOW,
        manual_resolution=manual_resolution,
    )


def _run_architecture_a(scenarios: list[Scenario]) -> list[CaseOutcome]:
    """Direct write: machine output becomes the fact; no decision, no certificate."""
    outcomes: list[CaseOutcome] = []
    for scenario in scenarios:
        if scenario.certificate.selection_state is not SelectionState.SELECTED:
            outcomes.append(
                CaseOutcome(
                    case_id=scenario.case_id,
                    architecture="A",
                    fault=scenario.fault,
                    fault_independent=scenario.fault_independent,
                    route="NO_OUTPUT",
                    rejected=False,
                    rejection_codes=(),
                    fact_created=False,
                    unauthorized=False,
                    trace_complete=False,
                    transition_id=None,
                )
            )
            continue
        if scenario.candidate_value is None:
            outcomes.append(
                CaseOutcome(
                    case_id=scenario.case_id,
                    architecture="A",
                    fault=scenario.fault,
                    fault_independent=scenario.fault_independent,
                    route="NO_OUTPUT",
                    rejected=False,
                    rejection_codes=(),
                    fact_created=False,
                    unauthorized=False,
                    trace_complete=False,
                    transition_id=None,
                )
            )
            continue
        attempt = TransitionAttempt(
            fact_version=scenario.current_fact_version + 1,
            record_id=scenario.certificate.target_record_id,
            evidence_sha256=scenario.evidence_sha256,
            decision=None,
            certificate=None,
        )
        unauthorized = bool(verify_transition_authorization(attempt, _context(scenario, {})))
        outcomes.append(
            CaseOutcome(
                case_id=scenario.case_id,
                architecture="A",
                fault=scenario.fault,
                fault_independent=scenario.fault_independent,
                route="DIRECT_WRITE",
                rejected=False,
                rejection_codes=(),
                fact_created=True,
                unauthorized=unauthorized,
                trace_complete=False,
                transition_id=None,
            )
        )
    return outcomes


def _run_architecture_b(scenarios: list[Scenario]) -> list[CaseOutcome]:
    """Ordinary confirmation: human confirms, but no certificate mechanism."""
    outcomes: list[CaseOutcome] = []
    for scenario in scenarios:
        decision = _decision(scenario, "B")
        attempt = TransitionAttempt(
            fact_version=scenario.current_fact_version + 1,
            record_id=scenario.certificate.target_record_id,
            evidence_sha256=scenario.evidence_sha256,
            decision=decision,
            certificate=None,
        )
        unauthorized = bool(verify_transition_authorization(attempt, _context(scenario, {})))
        outcomes.append(
            CaseOutcome(
                case_id=scenario.case_id,
                architecture="B",
                fault=scenario.fault,
                fault_independent=scenario.fault_independent,
                route="CONFIRMATION",
                rejected=False,
                rejection_codes=(),
                fact_created=True,
                unauthorized=unauthorized,
                trace_complete=False,
                transition_id=None,
            )
        )
    return outcomes


def _run_architecture_c(scenarios: list[Scenario], policy: TransitionPolicy) -> list[CaseOutcome]:
    """Authority contract: route, review, authorize, then measure the result."""
    outcomes: list[CaseOutcome] = []
    parents = _parents(scenarios)
    for scenario in scenarios:
        context = _context(scenario, parents)
        routing = policy.route(
            scenario.certificate,
            context,
            disagreement=scenario.disagreement,
            weak_evidence=scenario.weak_evidence,
        )
        if routing.route is ReviewRoute.REJECT_REACQUIRE:
            outcomes.append(
                CaseOutcome(
                    case_id=scenario.case_id,
                    architecture="C",
                    fault=scenario.fault,
                    fault_independent=scenario.fault_independent,
                    route=str(routing.route),
                    rejected=True,
                    rejection_codes=tuple(failure.code for failure in routing.failures),
                    fact_created=False,
                    unauthorized=False,
                    trace_complete=False,
                    transition_id=None,
                )
            )
            continue
        manual_resolution = scenario.fault == "abstained_resolved"
        decision = _decision(scenario, "C", manual_resolution=manual_resolution)
        authorization: FactTransitionResult = policy.authorize(
            decision, scenario.certificate, context
        )
        if not authorization.allowed or authorization.transition is None:
            outcomes.append(
                CaseOutcome(
                    case_id=scenario.case_id,
                    architecture="C",
                    fault=scenario.fault,
                    fault_independent=scenario.fault_independent,
                    route=str(routing.route),
                    rejected=True,
                    rejection_codes=tuple(failure.code for failure in authorization.failures),
                    fact_created=False,
                    unauthorized=False,
                    trace_complete=False,
                    transition_id=None,
                )
            )
            continue
        transition = authorization.transition
        attempt = TransitionAttempt(
            fact_version=transition.created_version,
            record_id=transition.record_id,
            evidence_sha256=transition.evidence_sha256,
            decision=decision,
            certificate=scenario.certificate,
        )
        verification = verify_transition_authorization(attempt, context)
        trace: ProvenanceTrace = build_provenance_trace(
            transition, decision, scenario.certificate, context.evidence_sha256
        )
        outcomes.append(
            CaseOutcome(
                case_id=scenario.case_id,
                architecture="C",
                fault=scenario.fault,
                fault_independent=scenario.fault_independent,
                route=str(routing.route),
                rejected=False,
                rejection_codes=(),
                fact_created=True,
                unauthorized=bool(verification),
                trace_complete=trace.complete,
                transition_id=transition.transition_id,
            )
        )
    return outcomes


def _p1_probes(policy: TransitionPolicy, certificate: CandidateCertificate) -> tuple[int, int]:
    """Negative probes: machine-facing objects expose no fact-writing path."""
    attempts = 0
    blocked = 0
    for obj in (policy, certificate):
        for method in ("add_record_version", "confirm", "correct", "write_fact", "apply"):
            attempts += 1
            if not hasattr(obj, method):
                blocked += 1
    probe_context = AuthorityContext(
        evidence_sha256=EVIDENCE_HASH,
        current_fact_version=1,
        known_sources=KNOWN_SOURCES,
        known_producers=KNOWN_PRODUCERS,
        known_selection_artifacts=KNOWN_SELECTION_ARTIFACTS,
        max_certificate_age=MAX_CERTIFICATE_AGE,
        now=NOW,
    )
    try:
        policy.authorize(certificate, probe_context)  # type: ignore[call-arg]
    except TypeError:
        blocked += 1
    attempts += 1
    return attempts, blocked


def _architecture_metrics(
    architecture: str,
    scenarios: list[Scenario],
    outcomes: list[CaseOutcome],
    policy: TransitionPolicy,
) -> ArchitectureResult:
    total = len(scenarios)
    outcome_by_case = {outcome.case_id: outcome for outcome in outcomes}
    facts_created = sum(outcome.fact_created for outcome in outcomes)
    unauthorized = sum(1 for outcome in outcomes if outcome.unauthorized)
    invalid_attempted = sum(
        1 for scenario in scenarios if scenario.fault in INVALID_TRANSITION_FAMILIES
    )
    invalid_rejected = sum(
        1
        for scenario in scenarios
        if scenario.fault in INVALID_TRANSITION_FAMILIES
        and outcome_by_case[scenario.case_id].rejected
    )
    stale_attempted = sum(1 for scenario in scenarios if scenario.fault == "stale_version")
    stale_rejected = sum(
        1
        for scenario in scenarios
        if scenario.fault == "stale_version" and outcome_by_case[scenario.case_id].rejected
    )
    parents = _parents(scenarios)
    certificate_valid = (
        sum(
            1
            for scenario in scenarios
            if not validate_certificate(scenario.certificate, _context(scenario, parents))
        )
        if architecture == "C"
        else 0
    )
    trace_complete = sum(1 for outcome in outcomes if outcome.trace_complete)
    p1_attempts, p1_blocked = (
        _p1_probes(policy, scenarios[0].certificate) if architecture == "C" else (0, 0)
    )
    return ArchitectureResult(
        architecture=architecture,
        cases=total,
        facts_created=facts_created,
        unauthorized_transitions=unauthorized,
        invalid_transition_rejection_rate=(
            invalid_rejected / invalid_attempted if invalid_attempted else 0.0
        ),
        valid_certificate_coverage=certificate_valid / total,
        reverse_trace_completeness=trace_complete / facts_created if facts_created else 0.0,
        stale_transition_containment=(stale_rejected / stale_attempted if stale_attempted else 0.0),
        p1_probe_attempts=p1_attempts,
        p1_probe_blocked=p1_blocked,
    )


def _risk_score_of(scenario: Scenario, policy: TransitionPolicy) -> float:
    decision = policy.route(
        scenario.certificate,
        _context(scenario, {}),
        disagreement=scenario.disagreement,
        weak_evidence=scenario.weak_evidence,
    )
    assert decision.risk_score is not None
    return decision.risk_score


def _escapes_for_selection(
    pool: list[Scenario], policy: TransitionPolicy, indices: Iterable[int]
) -> tuple[int, int]:
    wrong_reviewed = 0
    escapes = 0
    for index in indices:
        scenario = pool[index]
        if (
            scenario.candidate_value is None
            or scenario.truth_value is None
            or scenario.candidate_value == scenario.truth_value
        ):
            continue
        wrong_reviewed += 1
        route = policy.route(
            scenario.certificate,
            _context(scenario, {}),
            disagreement=scenario.disagreement,
            weak_evidence=scenario.weak_evidence,
        ).route
        detect = DETECT_ENHANCED if route is ReviewRoute.ENHANCED_REVIEW else DETECT_STANDARD
        if scenario.reviewer_draw > detect:
            escapes += 1
    return wrong_reviewed, escapes


def _budget_rows_for_pool(pool: list[Scenario], policy: TransitionPolicy) -> list[BudgetRow]:
    scores = [_risk_score_of(scenario, policy) for scenario in pool]
    risk_order = sorted(range(len(pool)), key=lambda index: (-scores[index], index))
    rows: list[BudgetRow] = []
    for budget in BUDGETS:
        k = int(round(len(pool) * budget))
        for label, indices in (("standard", range(k)), ("risk", risk_order[:k])):
            wrong_reviewed, escapes = _escapes_for_selection(pool, policy, indices)
            rows.append(
                BudgetRow(
                    budget=budget,
                    policy=label,
                    reviewed=k,
                    wrong_reviewed=wrong_reviewed,
                    escapes=escapes,
                    corrected=wrong_reviewed - escapes,
                    pending=len(pool) - k,
                )
            )
    return rows


def calibrate_routing(pool: list[Scenario]) -> tuple[RoutingConfig, list[CalibrationRow]]:
    """Executable calibration: grid-search routing parameters on the
    calibration split (disjoint from every evaluation seed), maximizing the
    matched-budget advantage at budget 0.5."""
    best: tuple[int, float, RoutingConfig] | None = None
    rows: list[CalibrationRow] = []
    for threshold in (0.5, 0.6, 0.7):
        for weight_uncertainty in (0.3, 0.5, 0.7):
            config = RoutingConfig(
                confidence_threshold=threshold, weight_uncertainty=weight_uncertainty
            )
            policy = TransitionPolicy(config)
            standard_escapes, risk_escapes = _escapes_at_budget(pool, policy, 0.5)
            advantage = standard_escapes - risk_escapes
            rows.append(
                CalibrationRow(
                    confidence_threshold=threshold,
                    weight_uncertainty=weight_uncertainty,
                    standard_escapes=standard_escapes,
                    risk_escapes=risk_escapes,
                    advantage=advantage,
                )
            )
            if (
                best is None
                or advantage > best[0]
                or (advantage == best[0] and -threshold > best[1])
            ):
                best = (advantage, -threshold, config)
    assert best is not None
    return best[2], rows


def _escapes_at_budget(
    pool: list[Scenario], policy: TransitionPolicy, budget: float
) -> tuple[int, int]:
    rows = _budget_rows_for_pool(pool, policy)
    standard = next(row for row in rows if row.policy == "standard" and row.budget == budget)
    risk = next(row for row in rows if row.policy == "risk" and row.budget == budget)
    return standard.escapes, risk.escapes


def run_routing_experiment(
    policy: TransitionPolicy,
) -> tuple[list[RoutingSeedRow], list[RoutingAggregate]]:
    """Multi-seed, multi-mode matched-budget routing evaluation (C only)."""
    seed_rows: list[RoutingSeedRow] = []
    aggregates: list[RoutingAggregate] = []
    for mode in WRONG_MODES:
        per_budget: dict[float, list[tuple[int, int]]] = {budget: [] for budget in BUDGETS}
        for seed in EVAL_SEEDS:
            pool = _pool_scenarios(seed, mode)
            rows = _budget_rows_for_pool(pool, policy)
            for row in rows:
                if row.policy == "standard":
                    risk = next(
                        other
                        for other in rows
                        if other.policy == "risk" and other.budget == row.budget
                    )
                    seed_rows.append(
                        RoutingSeedRow(
                            mode=mode,
                            seed=seed,
                            budget=row.budget,
                            standard_escapes=row.escapes,
                            risk_escapes=risk.escapes,
                        )
                    )
                    per_budget[row.budget].append((row.escapes, risk.escapes))
        for budget in BUDGETS:
            pairs = per_budget[budget]
            standard_values = [pair[0] for pair in pairs]
            risk_values = [pair[1] for pair in pairs]
            deltas = [std - risk for std, risk in pairs]
            mean_delta = float(np.mean(deltas))
            std_delta = float(np.std(deltas, ddof=1)) if len(deltas) > 1 else 0.0
            win_rate = sum(1 for std, risk in pairs if risk < std) / len(pairs)
            never_worse = sum(1 for std, risk in pairs if risk <= std) / len(pairs)
            aggregates.append(
                RoutingAggregate(
                    mode=mode,
                    budget=budget,
                    seeds=len(pairs),
                    standard_mean=float(np.mean(standard_values)),
                    risk_mean=float(np.mean(risk_values)),
                    mean_delta=mean_delta,
                    delta_ci=1.96 * std_delta / (len(pairs) ** 0.5),
                    win_rate=win_rate,
                    never_worse_rate=never_worse,
                )
            )
    return seed_rows, aggregates


def _n3_verdict(
    aggregates: list[RoutingAggregate],
) -> dict[str, Any]:
    by_mode: dict[str, dict[float, RoutingAggregate]] = {}
    for aggregate in aggregates:
        by_mode.setdefault(aggregate.mode, {})[aggregate.budget] = aggregate
    correlated = by_mode["correlated"]
    uncorrelated = by_mode["uncorrelated"]
    win_025 = correlated[0.25].win_rate
    win_050 = correlated[0.5].win_rate
    delta_positive = all(correlated[budget].mean_delta > 0 for budget in (0.25, 0.5, 0.75))
    never_worse_075 = correlated[0.75].never_worse_rate
    uncorrelated_delta_050 = uncorrelated[0.5].mean_delta
    pass_ = (
        win_025 >= N3_WIN_RATE_THRESHOLD
        and win_050 >= N3_WIN_RATE_THRESHOLD
        and delta_positive
        and never_worse_075 >= N3_NEVER_WORSE_THRESHOLD
        and uncorrelated_delta_050 >= N3_UNCORRELATED_DELTA_FLOOR
    )
    return {
        "verdict": "PASS" if pass_ else "FAIL",
        "correlated_win_rate_025": win_025,
        "correlated_win_rate_050": win_050,
        "correlated_never_worse_075": never_worse_075,
        "correlated_delta_positive_at_025_050_075": delta_positive,
        "uncorrelated_mean_delta_050": uncorrelated_delta_050,
        "thresholds": {
            "win_rate": N3_WIN_RATE_THRESHOLD,
            "never_worse": N3_NEVER_WORSE_THRESHOLD,
            "uncorrelated_delta_floor": N3_UNCORRELATED_DELTA_FLOOR,
        },
    }


def _producer_summaries(
    scenarios: list[Scenario], outcomes: list[CaseOutcome]
) -> list[ProducerSummary]:
    by_producer: dict[tuple[str, str], ProducerSummary] = {}
    outcome_by_case = {outcome.case_id: outcome for outcome in outcomes}
    for scenario in scenarios:
        key = (scenario.certificate.producer_id, scenario.certificate.producer_version)
        summary = by_producer.setdefault(
            key,
            ProducerSummary(
                producer_id=key[0],
                producer_version=key[1],
                cases=0,
                standard_routes=0,
                enhanced_routes=0,
                rejected=0,
                allowed=0,
            ),
        )
        outcome = outcome_by_case[scenario.case_id]
        by_producer[key] = ProducerSummary(
            producer_id=summary.producer_id,
            producer_version=summary.producer_version,
            cases=summary.cases + 1,
            standard_routes=summary.standard_routes + (outcome.route == "STANDARD_REVIEW"),
            enhanced_routes=summary.enhanced_routes + (outcome.route == "ENHANCED_REVIEW"),
            rejected=summary.rejected + (1 if outcome.rejected else 0),
            allowed=summary.allowed + (1 if outcome.fact_created else 0),
        )
    return sorted(by_producer.values(), key=lambda item: (item.producer_id, item.producer_version))


def _evaluate_gates(
    scenarios: list[Scenario],
    outcomes: list[CaseOutcome],
    aggregates: list[RoutingAggregate],
    calibration_selected: RoutingConfig,
) -> dict[str, Any]:
    c_outcomes = [outcome for outcome in outcomes if outcome.architecture == "C"]
    b_outcomes = [outcome for outcome in outcomes if outcome.architecture == "B"]
    c_by_case = {outcome.case_id: outcome for outcome in c_outcomes}
    b_by_case = {outcome.case_id: outcome for outcome in b_outcomes}

    n1 = all(
        c_by_case[scenario.case_id].rejected
        for scenario in scenarios
        if scenario.fault in INVALID_TRANSITION_FAMILIES
    )
    n2_cases = [
        scenario.case_id
        for scenario in scenarios
        if scenario.fault in {"stale_version", "evidence_mismatch", "missing_locator"}
        and b_by_case[scenario.case_id].fact_created
        and c_by_case[scenario.case_id].rejected
    ]
    independent = sum(
        1
        for scenario in scenarios
        if scenario.fault in INDEPENDENT_FAULT_FAMILIES and scenario.fault_independent
    )
    n3 = _n3_verdict(aggregates)
    return {
        "N1_enforced": n1,
        "N2_distinguishable_cases": sorted(n2_cases),
        "N2_pass": bool(n2_cases),
        "N3": n3,
        "N4_independent_faults": independent,
        "N4_uncorrelated_mode_present": "uncorrelated" in WRONG_MODES,
        "N5_claim_discipline": "documented in docs/dsh/authority-prototype-notes.md",
        "c_unauthorized_transitions": sum(1 for outcome in c_outcomes if outcome.unauthorized),
        "c_reverse_trace_complete": all(
            not outcome.fact_created or outcome.trace_complete for outcome in c_outcomes
        ),
        "c_stale_containment": all(
            c_by_case[scenario.case_id].rejected
            for scenario in scenarios
            if scenario.fault == "stale_version"
        ),
        "calibration_seed": CALIBRATION_SEED,
        "evaluation_seeds": list(EVAL_SEEDS),
        "calibration_selected": {
            "confidence_threshold": calibration_selected.confidence_threshold,
            "weight_uncertainty": calibration_selected.weight_uncertainty,
            "weight_disagreement": calibration_selected.weight_disagreement,
        },
    }


def _rejection_examples(outcomes: list[CaseOutcome]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    examples: list[dict[str, Any]] = []
    for outcome in outcomes:
        if outcome.architecture != "C" or not outcome.rejected:
            continue
        if outcome.fault in seen:
            continue
        seen.add(outcome.fault)
        examples.append(
            {
                "fault": outcome.fault,
                "case_id": outcome.case_id,
                "route": outcome.route,
                "rejection_codes": list(outcome.rejection_codes),
                "fact_unchanged": not outcome.fact_created,
            }
        )
    return examples


def run_authority_routing(output: Path) -> dict[str, Any]:
    """Run calibration, safety, and routing experiments; write JSON artifacts."""
    output.mkdir(parents=True, exist_ok=True)

    calibration_pool = _pool_scenarios(CALIBRATION_SEED, "correlated")
    config, calibration_rows = calibrate_routing(calibration_pool)
    policy = TransitionPolicy(config)

    fixed = _fixed_scenarios()
    safety_pool = _pool_scenarios(POOL_SEED, "correlated")
    scenarios = fixed + safety_pool

    outcomes_a = _run_architecture_a(scenarios)
    outcomes_b = _run_architecture_b(scenarios)
    outcomes_c = _run_architecture_c(scenarios, policy)
    all_outcomes = outcomes_a + outcomes_b + outcomes_c

    results = [
        _architecture_metrics("A", scenarios, outcomes_a, policy),
        _architecture_metrics("B", scenarios, outcomes_b, policy),
        _architecture_metrics("C", scenarios, outcomes_c, policy),
    ]
    seed_rows, aggregates = run_routing_experiment(policy)
    producer_summaries = _producer_summaries(scenarios, outcomes_c)
    gates = _evaluate_gates(scenarios, all_outcomes, aggregates, policy._config)
    examples = _rejection_examples(outcomes_c)

    _write_json(output / "authority_safety.json", results)
    _write_json(output / "authority_safety_cases.json", all_outcomes)
    _write_json(output / "authority_routing.json", seed_rows)
    _write_json(output / "authority_routing_aggregates.json", aggregates)
    _write_json(output / "authority_routing_calibration.json", calibration_rows)
    _write_json(output / "authority_routing_gates.json", [gates])
    _write_json(output / "authority_routing_producers.json", producer_summaries)
    _write_json(output / "authority_routing_rejections.json", examples)

    summary = {
        "architecture_results": results,
        "gates": gates,
        "aggregates": aggregates,
        "calibration_selected": policy._config,
        "calibration_rows": calibration_rows,
        "rejection_examples": examples,
        "producer_summaries": producer_summaries,
        "seed_rows": seed_rows,
        "cases": all_outcomes,
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the authority-contract benchmarks")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = run_authority_routing(args.output)
    gates = summary["gates"]
    print("Architecture safety comparison (unified case set)")
    print("arch  cases  facts  unauthorized  reject_inv  coverage  trace  stale  p1")
    for result in summary["architecture_results"]:
        print(
            f"{result.architecture}  {result.cases:5d}  {result.facts_created:5d}  "
            f"{result.unauthorized_transitions:12d}  "
            f"{result.invalid_transition_rejection_rate:.2f}  "
            f"{result.valid_certificate_coverage:.2f}  {result.reverse_trace_completeness:.2f}  "
            f"{result.stale_transition_containment:.2f}  "
            f"{result.p1_probe_blocked}/{result.p1_probe_attempts}"
        )
    print()
    print("Calibration (calibration seed", CALIBRATION_SEED, ")")
    selected = summary["calibration_selected"]
    print(
        "selected: threshold",
        selected.confidence_threshold,
        "w_uncertainty",
        selected.weight_uncertainty,
    )
    print("Routing experiment (16 evaluation seeds, matched budgets)")
    print("mode         budget  std_mean  risk_mean  delta    CI95     win_rate  never_worse")
    for aggregate in summary["aggregates"]:
        print(
            f"{aggregate.mode:11s}  {aggregate.budget:.2f}  "
            f"{aggregate.standard_mean:8.2f}  {aggregate.risk_mean:9.2f}  "
            f"{aggregate.mean_delta:7.2f}  {aggregate.delta_ci:7.2f}  "
            f"{aggregate.win_rate:8.2f}  {aggregate.never_worse_rate:10.2f}"
        )
    print()
    print("Gates")
    for key, value in gates.items():
        print(f"  {key}: {value}")
    print()
    print("Rejection families")
    for example in summary["rejection_examples"]:
        print(f"  {example['case_id']} [{example['fault']}] -> {example['rejection_codes']}")
    c_result = next(
        result for result in summary["architecture_results"] if result.architecture == "C"
    )
    valid = (
        bool(gates["N1_enforced"])
        and bool(gates["N2_pass"])
        and bool(gates["N4_independent_faults"])
        and c_result.unauthorized_transitions == 0
        and c_result.reverse_trace_completeness == 1.0
        and c_result.stale_transition_containment == 1.0
        and c_result.p1_probe_blocked == c_result.p1_probe_attempts
    )
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
