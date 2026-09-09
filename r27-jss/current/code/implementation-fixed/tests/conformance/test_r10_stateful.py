"""R10 bounded adversarial state machine with full-digest rejection oracle."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine,
    initialize,
    invariant,
    rule,
    run_state_machine_as_test,
)

from app.application.query_forms import QueryForms
from app.application.review_forms import (
    AuthorityRejectionError,
    ConcurrentReviewError,
)
from tests.conformance.oracle import (
    canonical_database_state,
    database_digest,
    relational_authority_violations,
)
from tests.conformance.test_g3b_conformance import _env, _record_machine

PAPER_PROFILE = os.environ.get("AUTODECTE_PAPER_PROFILE") == "1"


class AdversarialAdmissionStateMachine(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        self._tmp = Path(tempfile.mkdtemp(prefix="r10-state-"))
        self._engine, self._repo, self._reviews, self._recog, self._field_ids = _env(
            self._tmp, ["a", "b"]
        )
        self._model = {"a": 0, "b": 0}
        self._coverage = {
            "noop": 0,
            "cross_field": 0,
            "stale": 0,
            "principal": 0,
            "legal": 0,
        }

    @initialize()
    def initial_snapshot(self) -> None:
        cert_a = _record_machine(self._repo, self._recog, self._field_ids["a"], 0)
        cert_b = _record_machine(self._repo, self._recog, self._field_ids["b"], 0)
        self._reviews.confirm(
            "FORM-1",
            0,
            self._model,
            "reviewer-1",
            "r10-initial",
            certificate_ids_by_field={
                "a": cert_a.certificate_id,
                "b": cert_b.certificate_id,
            },
            manual_evidence_ids_by_field={},
        )

    def _assert_rejection_stutter(self, action) -> None:
        before = database_digest(self._engine)
        action()
        assert database_digest(self._engine) == before

    @rule(delta=st.integers(min_value=1, max_value=20))
    def adversarial_round(self, delta: int) -> None:
        current_version = len(self._repo.list_record_versions("FORM-1"))

        noop_cert = _record_machine(self._repo, self._recog, self._field_ids["a"], self._model["a"])

        def noop() -> None:
            with pytest.raises(AuthorityRejectionError) as error:
                self._reviews.confirm(
                    "FORM-1",
                    current_version,
                    {"a": self._model["a"]},
                    "reviewer-1",
                    "r10-noop",
                    certificate_ids_by_field={"a": noop_cert.certificate_id},
                    manual_evidence_ids_by_field={},
                )
            assert {failure.code for failure in error.value.failures} == {"NO_CHANGED_FIELDS"}

        self._assert_rejection_stutter(noop)
        self._coverage["noop"] += 1

        cross_cert = _record_machine(
            self._repo,
            self._recog,
            self._field_ids["a"],
            int(self._model["b"]) + delta,
        )

        def cross_field() -> None:
            with pytest.raises(AuthorityRejectionError) as error:
                self._reviews.confirm(
                    "FORM-1",
                    current_version,
                    {"b": int(self._model["b"]) + delta},
                    "reviewer-1",
                    "r10-cross-field",
                    certificate_ids_by_field={"b": cross_cert.certificate_id},
                    manual_evidence_ids_by_field={},
                )
            assert "FIELD_KEY_BINDING_MISMATCH" in {
                failure.code for failure in error.value.failures
            }

        self._assert_rejection_stutter(cross_field)
        self._coverage["cross_field"] += 1

        def stale() -> None:
            with pytest.raises(ConcurrentReviewError):
                self._reviews.confirm(
                    "FORM-1",
                    current_version - 1,
                    {"a": int(self._model["a"]) + delta},
                    "reviewer-1",
                    "r10-stale",
                    certificate_ids_by_field={"a": cross_cert.certificate_id},
                    manual_evidence_ids_by_field={},
                )

        self._assert_rejection_stutter(stale)
        self._coverage["stale"] += 1

        next_value = int(self._model["a"]) + delta
        principal_cert = _record_machine(self._repo, self._recog, self._field_ids["a"], next_value)

        def unknown_principal() -> None:
            with pytest.raises(AuthorityRejectionError) as error:
                self._reviews.confirm(
                    "FORM-1",
                    current_version,
                    {"a": next_value},
                    "unknown-reviewer",
                    "r10-principal",
                    certificate_ids_by_field={"a": principal_cert.certificate_id},
                    manual_evidence_ids_by_field={},
                )
            assert {failure.code for failure in error.value.failures} == {
                "PRINCIPAL_NOT_AUTHORIZED"
            }

        self._assert_rejection_stutter(unknown_principal)
        self._coverage["principal"] += 1

        self._reviews.confirm(
            "FORM-1",
            current_version,
            {"a": next_value},
            "reviewer-1",
            "r10-legal",
            certificate_ids_by_field={"a": principal_cert.certificate_id},
            manual_evidence_ids_by_field={},
        )
        self._model["a"] = next_value
        self._coverage["legal"] += 1

    @invariant()
    def persisted_state_and_independent_oracle_match(self) -> None:
        latest = self._repo.list_record_versions("FORM-1")[-1]
        assert latest.values == self._model
        trace = QueryForms(self._repo).trace("FORM-1")
        assert trace.status == "complete"
        state = canonical_database_state(self._engine)
        assert relational_authority_violations(state, "FORM-1") == ()

    def teardown(self) -> None:
        self._engine.dispose()


def test_r10_adversarial_state_machine() -> None:
    run_state_machine_as_test(
        AdversarialAdmissionStateMachine,
        settings=settings(
            max_examples=100 if PAPER_PROFILE else 8,
            stateful_step_count=25 if PAPER_PROFILE else 6,
            derandomize=True,
            database=None,
            deadline=None,
        ),
    )


def test_r10_declared_rule_coverage() -> None:
    machine = AdversarialAdmissionStateMachine()
    try:
        machine.initial_snapshot()
        machine.adversarial_round(1)
        assert machine._coverage == {
            "noop": 1,
            "cross_field": 1,
            "stale": 1,
            "principal": 1,
            "legal": 1,
        }
    finally:
        machine.teardown()
