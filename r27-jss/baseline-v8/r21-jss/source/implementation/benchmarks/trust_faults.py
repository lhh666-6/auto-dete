from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.adapters.ai.contracts import AIReview, AISuggestion
from app.adapters.database.authority_facades import (
    AuthorityReadFacade,
    CandidateWriteFacade,
    FactAdmissionFacade,
)
from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.recognition.candidate import RecognitionCandidate
from app.adapters.recognition.opencv import OpenCvImagePipeline
from app.adapters.storage.local import LocalEvidenceStorage
from app.adapters.vector.local import LocalVectorIndex, VectorDocument
from app.application.ai_review_forms import AIReviewForms
from app.application.import_forms import DuplicateEvidenceError, ImportForms
from app.application.recognize_forms import RecognizeForms
from app.application.review_forms import ConcurrentReviewError, ReviewForms
from app.domain.models import AIStatus, FormField, RecordVersion
from app.domain.principal import prototype_principal_policy


@dataclass(frozen=True, slots=True)
class FaultOutcome:
    fault: str
    machine_originated: bool
    fact_unchanged: bool
    audit_complete: bool
    expected_exception: str | None
    attempted_paths: int = 0
    blocked_paths: int = 0


@dataclass(frozen=True, slots=True)
class CandidateIsolationAblation:
    isolated_fact_changed: bool
    isolation_removed_fact_changed: bool
    injected_value: int


@dataclass(frozen=True, slots=True)
class StressOutcome:
    family: str
    trial: int
    trial_seed: int
    contained: bool
    expected_exception: str | None


@dataclass(slots=True)
class _Fixture:
    engine: Engine
    repository: SqlAlchemyFormRepository
    imports: ImportForms
    reviews: ReviewForms
    recognition: RecognizeForms
    image_path: Path
    versions: list[RecordVersion]


class _WrongSuggestionAdapter:
    def review(self, form_id: str, context: Mapping[str, Any]) -> AIReview:
        del context
        return AIReview(
            form_id=form_id,
            status=AIStatus.SUGGESTED,
            risk_level="HIGH",
            summary="Injected incorrect suggestion",
            suggestions=(
                AISuggestion(
                    field_name="total_quantity",
                    current_candidate=7,
                    suggested_value=999,
                    confidence=0.99,
                    evidence_types=("INJECTED_TEST",),
                    reason="Fault-injection case",
                ),
            ),
            missing_information=(),
            requires_human_confirmation=True,
        )


def _fixture(root: Path, case_name: str) -> _Fixture:
    case_root = root / case_name
    case_root.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{case_root / 'demo.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(
        engine,
        principal_policy=prototype_principal_policy(("reviewer", "reviewer-2", "machine")),
    )
    storage = LocalEvidenceStorage(case_root / "evidence")
    imports = ImportForms(repository, repository, repository, storage)
    reviews = ReviewForms(
        repository,
        repository,
        authority_read=AuthorityReadFacade(repository),
        admission=FactAdmissionFacade(repository),
        known_producers=frozenset({("human-reviewer", "manual-entry-v1"), ("fault-injector", "1")}),
        known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
    )
    recognition = RecognizeForms(
        repository,
        repository,
        repository,
        storage,
        OpenCvImagePipeline(),
        candidate_writer=CandidateWriteFacade(repository),
    )
    image_path = case_root / "form.png"
    image_path.write_bytes(b"synthetic immutable evidence")
    evidence = imports.import_image(image_path, "FORM-1", "T1", "1", "operator")
    baseline_values = {"total_quantity": 7}
    repository.add_form_field(FormField("FIELD-total_quantity", "FORM-1", "total_quantity", {}))
    reviews.confirm(
        "FORM-1",
        0,
        baseline_values,
        "reviewer",
        "controlled baseline",
        certificate_ids_by_field={field: None for field in baseline_values},
        manual_evidence_ids_by_field={field: evidence.file_id for field in baseline_values},
    )
    return _Fixture(
        engine=engine,
        repository=repository,
        imports=imports,
        reviews=reviews,
        recognition=recognition,
        image_path=image_path,
        versions=repository.list_record_versions("FORM-1"),
    )


def _outcome(
    fixture: _Fixture,
    *,
    fault: str,
    machine_originated: bool,
    required_event: str | None = None,
    expected_exception: str | None = None,
) -> FaultOutcome:
    events = {event.event_type for event in fixture.repository.list_audit_events("FORM-1")}
    audit_complete = {"IMPORT", "CONFIRM"}.issubset(events) and (
        required_event is None or required_event in events
    )
    return FaultOutcome(
        fault=fault,
        machine_originated=machine_originated,
        fact_unchanged=fixture.repository.list_record_versions("FORM-1") == fixture.versions,
        audit_complete=audit_complete,
        expected_exception=expected_exception,
    )


def run_fault_matrix(root: Path) -> list[FaultOutcome]:
    outcomes: list[FaultOutcome] = []

    recognition = _fixture(root, "wrong-recognition")
    recognition.repository.add_form_field(
        FormField("FIELD-1", "FORM-1", "total_quantity", {"x": 0, "y": 0, "width": 8, "height": 8})
    )
    recognition.recognition.record_candidate(
        "FORM-1",
        "FIELD-1",
        np.zeros((8, 8), dtype=np.uint8),
        RecognitionCandidate("999", 0.99, "fault-injector", "1", "INJECTED"),
        "machine",
    )
    outcomes.append(
        _outcome(
            recognition,
            fault="wrong_recognition",
            machine_originated=True,
            required_event="RECOGNIZE",
        )
    )
    recognition.engine.dispose()

    llm = _fixture(root, "wrong-llm")
    AIReviewForms(llm.repository, llm.repository, _WrongSuggestionAdapter()).run(
        "FORM-1", {"total_quantity": 7}, "machine"
    )
    outcomes.append(
        _outcome(
            llm,
            fault="wrong_llm_suggestion",
            machine_originated=True,
            required_event="AI_SUGGEST",
        )
    )
    llm.engine.dispose()

    retrieval = _fixture(root, "irrelevant-retrieval")
    index = LocalVectorIndex()
    index.add(VectorDocument("V1", "OTHER", "REFERENCE", "irrelevant payroll reference"))
    index.search("payroll")
    outcomes.append(_outcome(retrieval, fault="irrelevant_retrieval", machine_originated=True))
    retrieval.engine.dispose()

    stale = _fixture(root, "stale-human")
    stale_exception: str | None = None
    try:
        stale_evidence = stale.repository.list_evidence("FORM-1")[0].file_id
        stale.reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 999},
            "reviewer-2",
            "stale",
            certificate_ids_by_field={"total_quantity": None},
            manual_evidence_ids_by_field={"total_quantity": stale_evidence},
        )
    except ConcurrentReviewError as error:
        stale_exception = type(error).__name__
    outcomes.append(
        _outcome(
            stale,
            fault="stale_human_replay",
            machine_originated=False,
            expected_exception=stale_exception,
        )
    )
    stale.engine.dispose()

    duplicate = _fixture(root, "duplicate-evidence")
    duplicate_exception: str | None = None
    try:
        duplicate.imports.import_image(duplicate.image_path, "FORM-2", "T1", "1", "operator")
    except DuplicateEvidenceError as error:
        duplicate_exception = type(error).__name__
    outcomes.append(
        _outcome(
            duplicate,
            fault="duplicate_evidence",
            machine_originated=False,
            expected_exception=duplicate_exception,
        )
    )
    duplicate.engine.dispose()

    direct = _fixture(root, "direct-fact-write")
    machine_services: tuple[object, ...] = (
        direct.recognition,
        AIReviewForms(direct.repository, direct.repository, _WrongSuggestionAdapter()),
        LocalVectorIndex(),
    )
    method_names = ("add_record_version", "confirm", "correct", "write_fact")
    attempted_paths = len(machine_services) * len(method_names)
    blocked_paths = 0
    for service in machine_services:
        for method_name in method_names:
            try:
                getattr(service, method_name)
            except AttributeError:
                blocked_paths += 1
    base_outcome = _outcome(
        direct,
        fault="attempted_direct_fact_write",
        machine_originated=True,
        expected_exception="AttributeError" if blocked_paths == attempted_paths else None,
    )
    outcomes.append(
        FaultOutcome(
            fault=base_outcome.fault,
            machine_originated=base_outcome.machine_originated,
            fact_unchanged=base_outcome.fact_unchanged,
            audit_complete=base_outcome.audit_complete,
            expected_exception=base_outcome.expected_exception,
            attempted_paths=attempted_paths,
            blocked_paths=blocked_paths,
        )
    )
    direct.engine.dispose()
    return outcomes


def run_candidate_isolation_ablation(root: Path) -> CandidateIsolationAblation:
    injected_value = 999
    isolated = _fixture(root, "candidate-isolation-enabled")
    isolated.repository.add_form_field(
        FormField("FIELD-1", "FORM-1", "total_quantity", {"x": 0, "y": 0, "width": 8, "height": 8})
    )
    before_isolated = isolated.repository.list_record_versions("FORM-1")
    isolated.recognition.record_candidate(
        "FORM-1",
        "FIELD-1",
        np.zeros((8, 8), dtype=np.uint8),
        RecognitionCandidate(str(injected_value), 0.99, "fault-injector", "1", "INJECTED"),
        "machine",
    )
    isolated_changed = isolated.repository.list_record_versions("FORM-1") != before_isolated
    isolated.engine.dispose()

    removed = _fixture(root, "candidate-isolation-removed")
    before_removed = removed.repository.list_record_versions("FORM-1")
    removed_evidence = removed.repository.list_evidence("FORM-1")[0].file_id
    removed_values = {"total_quantity": injected_value}
    removed.reviews.confirm(
        "FORM-1",
        1,
        removed_values,
        "machine",
        "test-only unsafe capability wiring",
        certificate_ids_by_field={field: None for field in removed_values},
        manual_evidence_ids_by_field={field: removed_evidence for field in removed_values},
    )
    removed_changed = removed.repository.list_record_versions("FORM-1") != before_removed
    removed.engine.dispose()
    return CandidateIsolationAblation(
        isolated_fact_changed=isolated_changed,
        isolation_removed_fact_changed=removed_changed,
        injected_value=injected_value,
    )


def run_randomized_fault_stress(
    root: Path, *, trials_per_family: int, seed: int
) -> list[StressOutcome]:
    if trials_per_family <= 0:
        raise ValueError("trials_per_family must be positive")
    rng = np.random.default_rng(seed)
    outcomes: list[StressOutcome] = []
    families = (
        "wrong_recognition",
        "wrong_llm_suggestion",
        "irrelevant_retrieval",
        "stale_human_replay",
        "duplicate_evidence",
    )
    for family in families:
        for trial in range(trials_per_family):
            trial_seed = int(rng.integers(0, 2**31 - 1))
            fixture = _fixture(root, f"stress-{family}-{trial:04d}")
            before = fixture.repository.list_record_versions("FORM-1")
            expected_exception: str | None = None
            if family == "wrong_recognition":
                fixture.repository.add_form_field(
                    FormField(
                        "FIELD-1",
                        "FORM-1",
                        "total_quantity",
                        {"x": 0, "y": 0, "width": 8, "height": 8},
                    )
                )
                wrong_value = str(int(rng.integers(100, 1000)))
                fixture.recognition.record_candidate(
                    "FORM-1",
                    "FIELD-1",
                    rng.integers(0, 256, size=(8, 8), dtype=np.uint8),
                    RecognitionCandidate(
                        wrong_value,
                        float(rng.uniform(0.5, 1.0)),
                        "stress-injector",
                        "1",
                        "INJECTED",
                    ),
                    "machine",
                )
            elif family == "wrong_llm_suggestion":
                AIReviewForms(
                    fixture.repository, fixture.repository, _WrongSuggestionAdapter()
                ).run("FORM-1", {"nonce": trial_seed}, "machine")
            elif family == "irrelevant_retrieval":
                index = LocalVectorIndex()
                index.add(
                    VectorDocument(
                        f"V-{trial_seed}",
                        "OTHER",
                        "REFERENCE",
                        f"irrelevant randomized reference {trial_seed}",
                    )
                )
                index.search(f"missing-{trial_seed}")
            elif family == "stale_human_replay":
                try:
                    stress_values = {"total_quantity": int(rng.integers(100, 1000))}
                    stress_evidence = fixture.repository.list_evidence("FORM-1")[0].file_id
                    fixture.reviews.confirm(
                        "FORM-1",
                        0,
                        stress_values,
                        "reviewer-2",
                        "randomized stale replay",
                        certificate_ids_by_field={field: None for field in stress_values},
                        manual_evidence_ids_by_field={
                            field: stress_evidence for field in stress_values
                        },
                    )
                except ConcurrentReviewError as error:
                    expected_exception = type(error).__name__
            else:
                try:
                    fixture.imports.import_image(
                        fixture.image_path,
                        f"FORM-DUP-{trial_seed}",
                        "T1",
                        "1",
                        "operator",
                    )
                except DuplicateEvidenceError as error:
                    expected_exception = type(error).__name__
            unchanged = fixture.repository.list_record_versions("FORM-1") == before
            rejected_when_required = (
                family
                not in {
                    "stale_human_replay",
                    "duplicate_evidence",
                }
                or expected_exception is not None
            )
            outcomes.append(
                StressOutcome(
                    family=family,
                    trial=trial,
                    trial_seed=trial_seed,
                    contained=unchanged and rejected_when_required,
                    expected_exception=expected_exception,
                )
            )
            fixture.engine.dispose()
    return outcomes
