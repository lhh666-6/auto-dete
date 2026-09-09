"""R8: canonical, idempotent v5 migration and constraint fingerprints."""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from app.adapters.database.migrations import (
    SCHEMA_VERSION,
    migrate_schema,
    schema_fingerprint,
)
from app.adapters.database.models import Base
from app.adapters.database.repositories import install_sqlite_pragmas

V5_INDEXES = {
    "uq_authorization_bindings_certificate_id",
    "uq_authorization_bindings_decision_id",
    "uq_fact_transitions_certificate_id",
    "uq_fact_transitions_decision_id",
}


def _engine(path: Path):
    engine = create_engine(f"sqlite:///{path}")
    install_sqlite_pragmas(engine)
    return engine


def _fresh(path: Path):
    engine = _engine(path)
    Base.metadata.create_all(engine)
    migrate_schema(engine)
    return engine


def test_fresh_and_v4_upgrade_have_same_declared_schema_fingerprint(
    tmp_path: Path,
) -> None:
    fresh = _fresh(tmp_path / "fresh.db")
    upgraded = _engine(tmp_path / "upgraded.db")
    Base.metadata.create_all(upgraded)
    with upgraded.begin() as connection:
        for index_name in V5_INDEXES:
            connection.execute(text(f'DROP INDEX IF EXISTS "{index_name}"'))
        connection.execute(text("PRAGMA user_version=4"))

    migrate_schema(upgraded)

    assert schema_fingerprint(fresh) == schema_fingerprint(upgraded)
    with upgraded.connect() as connection:
        assert connection.execute(text("PRAGMA user_version")).scalar_one() == 5
        marker = connection.execute(
            text(
                "SELECT value FROM authority_meta "
                "WHERE key='canonical_evidence_locator_v1_started_at'"
            )
        ).scalar_one()
        assert marker


def test_repeated_migration_is_no_op_and_future_version_refuses(
    tmp_path: Path,
) -> None:
    engine = _fresh(tmp_path / "repeat.db")
    before = schema_fingerprint(engine)

    migrate_schema(engine)

    assert schema_fingerprint(engine) == before
    with engine.begin() as connection:
        connection.execute(text(f"PRAGMA user_version={SCHEMA_VERSION + 1}"))
    with pytest.raises(RuntimeError):
        migrate_schema(engine)


def _transition_values(
    transition_id: str, decision_id: str, certificate_id: str, field_key: str
) -> dict[str, object]:
    return {
        "transition_id": transition_id,
        "form_id": "FORM-1",
        "created_version": 1,
        "field_key": field_key,
        "record_id": "FORM-1",
        "record_version_id": "REC-1",
        "decision_id": decision_id,
        "certificate_id": certificate_id,
        "evidence_hash": "ab" * 32,
        "evidence_locator": "locator",
        "producer_id": "producer",
        "producer_version": "1",
        "template_id": "T1",
        "template_version": "1",
        "source_kind": "MANUAL_ENTRY",
        "value_payload": "1",
        "created_at": "2026-08-23T00:00:00+00:00",
    }


@pytest.mark.parametrize("duplicate", ("decision", "certificate"))
def test_transition_decision_and_certificate_are_each_single_use(
    tmp_path: Path, duplicate: str
) -> None:
    engine = _fresh(tmp_path / f"unique-{duplicate}.db")
    columns = ", ".join(_transition_values("", "", "", ""))
    placeholders = ", ".join(f":{column}" for column in _transition_values("", "", "", ""))
    statement = text(f"INSERT INTO fact_transitions ({columns}) VALUES ({placeholders})")
    first = _transition_values("T-1", "D-1", "C-1", "a")
    second = _transition_values(
        "T-2",
        "D-1" if duplicate == "decision" else "D-2",
        "C-1" if duplicate == "certificate" else "C-2",
        "b",
    )
    with engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
        connection.commit()
        connection.execute(statement, first)
        connection.commit()
        with pytest.raises(IntegrityError):
            connection.execute(statement, second)
        connection.rollback()
