"""R10 deterministic pre-COMMIT failure injection and rollback checks."""

from pathlib import Path

import pytest

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.domain.models import ReviewStatus
from tests.conformance.oracle import database_digest
from tests.integration.test_authority_integration import (
    _confirm_args,
    _engine,
    _seed_version,
)

FAILPOINTS = (
    "before_cas",
    "after_cas",
    "before_record_version",
    "before_derived_certificate",
    "before_decision",
    "before_binding",
    "before_transition",
    "before_audit",
    "before_status",
    "before_commit",
)


class InjectedAdmissionFailure(RuntimeError):
    pass


@pytest.mark.parametrize("failpoint", FAILPOINTS)
def test_every_precommit_failpoint_rolls_back_complete_digest(
    tmp_path: Path, failpoint: str
) -> None:
    engine = _engine(tmp_path / f"{failpoint}.db")
    Base.metadata.create_all(engine)
    _seed_version(engine)

    def inject(name: str) -> None:
        if name == failpoint:
            raise InjectedAdmissionFailure(name)

    repository = SqlAlchemyFormRepository(engine, admission_failpoint=inject)
    certificate, decision, transition, record, audit, binding = _confirm_args()
    before = database_digest(engine)

    with pytest.raises(InjectedAdmissionFailure, match=failpoint):
        repository.append_fact_transition(
            form_id="FORM-1",
            expected_version=0,
            record=record,
            decisions=[decision],
            transitions=[transition],
            derived_certificates=[(certificate, "EVID-1")],
            authorization_bindings=[binding],
            audit=audit,
            review_status=ReviewStatus.CONFIRMED,
            export_status=None,
        )

    assert database_digest(engine) == before
