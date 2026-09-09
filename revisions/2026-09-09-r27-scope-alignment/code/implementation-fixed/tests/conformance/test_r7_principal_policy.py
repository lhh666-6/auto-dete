"""R7 conformance: commit-time principal policy is fail-closed."""

from dataclasses import dataclass
from pathlib import Path
from threading import Thread

import pytest
from sqlalchemy import create_engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.application.review_forms import AuthorityRejectionError, ReviewForms
from app.domain.models import EvidenceFile, EvidenceType, Form, FormField
from app.domain.principal import FACT_ADMISSION_ROLE, PrincipalRolePolicy
from tests.conformance.oracle import database_digest


@dataclass(frozen=True)
class _ForgeablePrincipal:
    principal_id: str
    roles: frozenset[str]


def _env(tmp_path: Path, policy: PrincipalRolePolicy):
    engine = create_engine(f"sqlite:///{tmp_path / 'principal.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine, principal_policy=policy)
    repository.add_form(Form("FORM-1", "T1", "1"))
    repository.add_form_field(
        FormField(
            "FIELD-1",
            "FORM-1",
            "total_quantity",
            {"x": 0, "y": 0, "w": 8, "h": 8},
        )
    )
    repository.add_evidence(
        EvidenceFile(
            "EVID-1",
            "FORM-1",
            EvidenceType.ORIGINAL_IMAGE,
            "manual/source.png",
            "ab" * 32,
        )
    )
    reviews = ReviewForms(
        repository,
        repository,
        authority_read=repository,
        admission=repository,
        known_producers=frozenset({("human-reviewer", "manual-entry-v1")}),
        known_selection_artifacts=frozenset(),
    )
    return engine, repository, reviews


def _confirm(reviews: ReviewForms, actor_id: object) -> None:
    reviews.confirm(  # type: ignore[arg-type]
        "FORM-1",
        0,
        {"total_quantity": 7},
        actor_id,
        "r7",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
    )


def _assert_zero_authority_writes(repository: SqlAlchemyFormRepository) -> None:
    assert repository.get_form("FORM-1").current_record_version == 0  # type: ignore[union-attr]
    assert repository.list_record_versions("FORM-1") == []
    assert repository.list_transitions_for_version("FORM-1", 1) == []
    assert repository.list_decisions_for_form("FORM-1") == []


def test_allowed_principal_commits(tmp_path: Path) -> None:
    policy = PrincipalRolePolicy({"reviewer-1": frozenset({FACT_ADMISSION_ROLE})})
    _, repository, reviews = _env(tmp_path, policy)

    _confirm(reviews, "reviewer-1")

    assert repository.get_form("FORM-1").current_record_version == 1  # type: ignore[union-attr]


@pytest.mark.parametrize(
    "principal",
    (
        "unknown-reviewer",
        _ForgeablePrincipal("reviewer-1", frozenset({FACT_ADMISSION_ROLE})),
    ),
)
def test_unknown_or_forgeable_principal_is_zero_write_rejection(
    tmp_path: Path, principal: object
) -> None:
    policy = PrincipalRolePolicy({"reviewer-1": frozenset({FACT_ADMISSION_ROLE})})
    engine, repository, reviews = _env(tmp_path, policy)
    before = database_digest(engine)

    with pytest.raises(AuthorityRejectionError) as exc_info:
        _confirm(reviews, principal)

    assert {failure.code for failure in exc_info.value.failures} == {"PRINCIPAL_NOT_AUTHORIZED"}
    _assert_zero_authority_writes(repository)
    assert database_digest(engine) == before


def test_revoked_principal_is_rechecked_at_commit(tmp_path: Path) -> None:
    policy = PrincipalRolePolicy({"reviewer-1": frozenset({FACT_ADMISSION_ROLE})})
    engine, repository, reviews = _env(tmp_path, policy)
    policy.revoke("reviewer-1", FACT_ADMISSION_ROLE)
    before = database_digest(engine)

    with pytest.raises(AuthorityRejectionError) as exc_info:
        _confirm(reviews, "reviewer-1")

    assert {failure.code for failure in exc_info.value.failures} == {"PRINCIPAL_NOT_AUTHORIZED"}
    _assert_zero_authority_writes(repository)
    assert database_digest(engine) == before


@pytest.mark.parametrize("stage", ["before_cas", "before_commit"])
def test_revocation_after_policy_check_does_not_cancel_inflight_admission(
    tmp_path: Path, stage: str
) -> None:
    """Controlled schedules verify the declared commit-entry policy boundary."""
    policy = PrincipalRolePolicy({"reviewer-1": frozenset({FACT_ADMISSION_ROLE})})
    engine, repository, reviews = _env(tmp_path, policy)
    reached = []

    def revoke_after_check(name: str) -> None:
        if name == stage:
            thread = Thread(target=policy.revoke, args=("reviewer-1", FACT_ADMISSION_ROLE))
            thread.start()
            thread.join(timeout=5)
            assert not thread.is_alive(), "policy lock unexpectedly held through commit"
            reached.append(name)

    repository._admission_failpoint = revoke_after_check
    try:
        _confirm(reviews, "reviewer-1")
        assert reached == [stage]
        assert repository.get_form("FORM-1").current_record_version == 1
        assert len(repository.list_record_versions("FORM-1")) == 1
    finally:
        engine.dispose()
