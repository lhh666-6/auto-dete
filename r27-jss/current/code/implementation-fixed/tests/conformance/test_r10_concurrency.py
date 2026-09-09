"""R10 safety/liveness races with distinct contender identities."""

from __future__ import annotations

import multiprocessing
import os
import queue
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine, text

from app.adapters.database.repositories import (
    SqlAlchemyFormRepository,
    install_sqlite_pragmas,
)
from app.application.query_forms import QueryForms
from app.domain.authority import (
    AuthorizationBinding,
    FactTransition,
    HumanDecision,
    canonical_json,
)
from app.domain.models import (
    AuditEvent,
    RecordStatus,
    RecordVersion,
    ReviewStatus,
    utc_now,
)
from tests.conformance.test_g3b_conformance import _env, _record_machine

PAPER_PROFILE = os.environ.get("AUTODECTE_PAPER_PROFILE") == "1"
THREAD_CASES = ((2, 50), (4, 20), (8, 20)) if PAPER_PROFILE else ((2, 4), (4, 3), (8, 2))
PROCESS_REPETITIONS = 20 if PAPER_PROFILE else 1


@dataclass(frozen=True)
class _Bundle:
    record: RecordVersion
    decision: HumanDecision
    transition: FactTransition
    binding: AuthorizationBinding
    audit: AuditEvent


def _bundle(index: int, certificate) -> _Bundle:
    now = utc_now()
    decision_id = f"R10-D-{index}"
    record_id = f"R10-REC-{index}"
    transition_id = f"R10-T-{index}"
    decision = HumanDecision(
        decision_id=decision_id,
        reviewer_id="reviewer-1",
        candidate_id=certificate.candidate_id,
        field_key="a",
        reason=f"contender-{index}",
        decided_at=now,
    )
    record = RecordVersion(
        record_id=record_id,
        form_id="FORM-1",
        version=1,
        previous_version=None,
        status=RecordStatus.CONFIRMED,
        values={"a": index},
        change_reason=f"contender-{index}",
        confirmed_by="reviewer-1",
        created_at=now,
    )
    transition = FactTransition(
        transition_id=transition_id,
        record_id="FORM-1",
        field_key="a",
        created_version=1,
        record_version_id=record_id,
        decision_id=decision_id,
        certificate_id=certificate.certificate_id,
        evidence_sha256=certificate.evidence_hash,
        evidence_locator=certificate.evidence_locator,
        producer_id=certificate.producer_id,
        producer_version=certificate.producer_version,
        source_kind=certificate.source_kind,
        template_id=certificate.template_id,
        template_version=certificate.template_version,
        value_payload=canonical_json(index),
        created_at=now,
    )
    binding = AuthorizationBinding(
        binding_id=f"R10-B-{index}",
        decision_id=decision_id,
        certificate_id=certificate.certificate_id,
        authorized_value_payload=canonical_json(index),
        bound_at=now,
    )
    audit = AuditEvent(
        event_id=f"R10-A-{index}",
        form_id="FORM-1",
        event_type="CONFIRM",
        actor_id="reviewer-1",
        after={"a": index},
        reason=f"contender-{index}",
    )
    return _Bundle(record, decision, transition, binding, audit)


def _append(repository: SqlAlchemyFormRepository, bundle: _Bundle) -> bool:
    return repository.append_fact_transition(
        form_id="FORM-1",
        expected_version=0,
        record=bundle.record,
        decisions=[bundle.decision],
        transitions=[bundle.transition],
        derived_certificates=[],
        authorization_bindings=[bundle.binding],
        audit=bundle.audit,
        review_status=ReviewStatus.CONFIRMED,
        export_status=None,
    )


def _prepare(tmp_path: Path, contenders: int):
    tmp_path.mkdir(parents=True, exist_ok=True)
    engine, repository, _, recognition, field_ids = _env(tmp_path, ["a"])
    with engine.begin() as connection:
        connection.execute(text("PRAGMA journal_mode=WAL"))
        connection.execute(text("PRAGMA synchronous=NORMAL"))
    certificates = [
        _record_machine(repository, recognition, field_ids["a"], index)
        for index in range(1, contenders + 1)
    ]
    return engine, repository, [_bundle(index, cert) for index, cert in enumerate(certificates, 1)]


def _assert_one_complete_winner(
    repository: SqlAlchemyFormRepository, bundles: list[_Bundle], outcomes: list[bool]
) -> None:
    # Safety and liveness are reported independently.
    assert sum(outcomes) <= 1, "safety: more than one contender committed"
    assert sum(outcomes) >= 1, "liveness: no contender committed"
    assert sum(outcomes) == 1

    versions = repository.list_record_versions("FORM-1")
    decisions = repository.list_decisions_for_form("FORM-1")
    bindings = repository.list_authorization_bindings_for_form("FORM-1")
    transitions = repository.list_transitions_for_version("FORM-1", 1)
    assert len(versions) == len(decisions) == len(bindings) == len(transitions) == 1
    winner_transition = transitions[0]
    winner = next(
        bundle
        for bundle in bundles
        if bundle.transition.transition_id == winner_transition.transition_id
    )
    assert versions[0].record_id == winner.record.record_id
    assert decisions[0].decision_id == winner.decision.decision_id
    assert bindings[0].binding_id == winner.binding.binding_id
    assert versions[0].fact_sources == {"a": winner.transition.transition_id}
    assert QueryForms(repository).trace("FORM-1").status == "complete"

    loser_ids = {
        bundle.decision.decision_id
        for bundle in bundles
        if bundle.decision.decision_id != winner.decision.decision_id
    }
    assert loser_ids.isdisjoint({decision.decision_id for decision in decisions})
    assert loser_ids.isdisjoint({binding.decision_id for binding in bindings})
    assert loser_ids.isdisjoint({transition.decision_id for transition in transitions})


@pytest.mark.parametrize(
    ("contenders", "repetitions"),
    THREAD_CASES,
)
def test_thread_contention_safety_and_liveness(
    tmp_path: Path, contenders: int, repetitions: int
) -> None:
    for repetition in range(repetitions):
        run_path = tmp_path / f"t{contenders}-{repetition}"
        engine, repository, bundles = _prepare(run_path, contenders)
        db_path = run_path / "conformance.db"
        barrier = threading.Barrier(contenders)
        outcomes: list[bool] = []
        errors: list[BaseException] = []
        result_lock = threading.Lock()

        threads = [
            threading.Thread(
                target=_thread_worker,
                args=(db_path, bundle, barrier, outcomes, errors, result_lock),
            )
            for bundle in bundles
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=45)
        assert all(not thread.is_alive() for thread in threads)
        assert errors == []
        assert len(outcomes) == contenders
        _assert_one_complete_winner(repository, bundles, outcomes)
        engine.dispose()


def _process_worker(
    db_path: str,
    bundle: _Bundle,
    barrier: Any,
    results: Any,
) -> None:
    engine = create_engine(f"sqlite:///{db_path}")
    install_sqlite_pragmas(engine)
    repository = SqlAlchemyFormRepository(engine)
    try:
        barrier.wait()
        results.put(("outcome", _append(repository, bundle)))
    except BaseException as error:
        results.put(("error", repr(error)))
    finally:
        engine.dispose()


def _thread_worker(
    db_path: Path,
    bundle: _Bundle,
    barrier: threading.Barrier,
    outcomes: list[bool],
    errors: list[BaseException],
    result_lock: Any,
) -> None:
    worker_engine = create_engine(f"sqlite:///{db_path}")
    install_sqlite_pragmas(worker_engine)
    worker_repository = SqlAlchemyFormRepository(worker_engine)
    try:
        barrier.wait()
        outcome = _append(worker_repository, bundle)
        with result_lock:
            outcomes.append(outcome)
    except BaseException as error:
        with result_lock:
            errors.append(error)
    finally:
        worker_engine.dispose()


@pytest.mark.parametrize("repetition", range(PROCESS_REPETITIONS))
def test_multiprocess_two_contender_control(tmp_path: Path, repetition: int) -> None:
    del repetition
    engine, repository, bundles = _prepare(tmp_path, 2)
    context = multiprocessing.get_context("spawn")
    barrier = context.Barrier(2)
    results = context.Queue()
    processes = [
        context.Process(
            target=_process_worker,
            args=(str(tmp_path / "conformance.db"), bundle, barrier, results),
        )
        for bundle in bundles
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=60)
    assert all(not process.is_alive() for process in processes)
    messages = []
    for _ in processes:
        try:
            messages.append(results.get(timeout=5))
        except queue.Empty:
            break
    assert [kind for kind, _ in messages if kind == "error"] == []
    outcomes = [value for kind, value in messages if kind == "outcome"]
    assert len(outcomes) == 2
    _assert_one_complete_winner(repository, bundles, outcomes)
    engine.dispose()
