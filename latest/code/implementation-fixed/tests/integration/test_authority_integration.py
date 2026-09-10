"""Integration tests for the authority persistence layer (Task B+).

Task B scope: additive schema (UTCDateTime, three new tables, FK + busy
pragmas, user_version stamp) and everything the database itself can express.
Cross-form invariants (R3) arrive with the repository layer in Task C.
"""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session

from app.adapters.database.models import (
    Base,
    CandidateCertificateRow,
    FactTransitionRow,
)
from app.domain.authority import (
    AuthorizationBinding,
    CandidateCertificate,
    SourceKind,
    canonical_json,
)

NOW = datetime(2026, 8, 17, 9, 0, tzinfo=UTC)

# Minimal pre-certificate schema as it existed at the baseline commit
# (forms, record_versions, audit_events). New tables are created additively.
OLD_SCHEMA = """
CREATE TABLE forms (
    form_id TEXT PRIMARY KEY,
    template_id TEXT NOT NULL,
    template_version TEXT NOT NULL,
    coordinate_version TEXT NOT NULL,
    review_status TEXT NOT NULL,
    export_status TEXT NOT NULL,
    current_record_version INTEGER NOT NULL,
    created_at DATETIME NOT NULL
);
CREATE TABLE record_versions (
    record_id TEXT PRIMARY KEY,
    form_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    previous_version INTEGER,
    status TEXT NOT NULL,
    "values" JSON NOT NULL,
    change_reason TEXT NOT NULL,
    confirmed_by TEXT,
    created_at DATETIME NOT NULL,
    UNIQUE (form_id, version)
);
CREATE TABLE audit_events (
    event_id TEXT PRIMARY KEY,
    form_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    before JSON,
    after JSON,
    reason TEXT,
    evidence_ids JSON NOT NULL
);
"""


def _legacy_db(path: Path) -> None:
    connection = sqlite3.connect(path)
    connection.executescript(OLD_SCHEMA)
    connection.execute(
        "INSERT INTO forms VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("FORM-OLD", "T1", "1", "1", "CONFIRMED", "NOT_EXPORTED", 1, "2026-01-01 08:00:00"),
    )
    connection.execute(
        "INSERT INTO record_versions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "REC-OLD-1",
            "FORM-OLD",
            1,
            None,
            "CONFIRMED",
            '{"total_quantity": 7}',
            "legacy",
            "reviewer-old",
            "2026-01-01 08:00:00",
        ),
    )
    connection.execute(
        "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "EVENT-OLD-1",
            "FORM-OLD",
            "CONFIRM",
            "reviewer-old",
            "2026-01-01 08:00:00",
            None,
            '{"total_quantity": 7}',
            "legacy",
            "[]",
        ),
    )
    connection.commit()
    connection.close()


def _engine(path: Path) -> Engine:
    from app.adapters.database.repositories import install_sqlite_pragmas

    engine = create_engine(f"sqlite:///{path}")
    install_sqlite_pragmas(engine)
    return engine


def _seed(engine: Engine) -> None:
    """Parent rows required by the new FKs (form + evidence file).

    Inserts are flushed in FK order explicitly: without relationship()
    mappings, SQLAlchemy's unit of work does not topologically sort inserts,
    so the form row must be flushed before the evidence row.
    """
    from app.adapters.database.models import EvidenceFileRow, FormRow

    with Session(engine) as session, session.begin():
        session.add(
            FormRow(
                form_id="FORM-1",
                template_id="T1",
                template_version="1",
                coordinate_version="1",
                review_status="IMPORTED",
                export_status="NOT_EXPORTED",
                current_record_version=0,
                created_at=NOW,
            )
        )
        session.flush()
        session.add(
            EvidenceFileRow(
                file_id="EVID-1",
                form_id="FORM-1",
                type="ORIGINAL_IMAGE",
                uri="ev-1",
                sha256="ab" * 32,
                created_at=NOW,
            )
        )


def _cert_row(form_id: str = "FORM-1") -> CandidateCertificateRow:
    certificate = CandidateCertificate.from_manual_entry(
        candidate_id="manual-1",
        field_key="total_quantity",
        value=7,
        form_id=form_id,
        evidence_hash="ab" * 32,
        evidence_locator=f"{form_id}/manual/total_quantity",
        template_id="T1",
        template_version="1",
        target_record_id=form_id,
        expected_fact_version=0,
        created_at=NOW,
    )
    return CandidateCertificateRow(
        certificate_id=certificate.certificate_id,
        candidate_id=certificate.candidate_id,
        field_key=certificate.field_key,
        form_id=form_id,
        field_id=None,
        evidence_file_id="EVID-1",
        recognition_attempt_id=None,
        value_payload=certificate.value_payload,
        evidence_hash=certificate.evidence_hash,
        evidence_locator=certificate.evidence_locator,
        template_id=certificate.template_id,
        template_version=certificate.template_version,
        source_kind=certificate.source_kind.value,
        producer_id=certificate.producer_id,
        producer_version=certificate.producer_version,
        selection_artifact_id=certificate.selection_artifact_id,
        confidence=certificate.confidence,
        selection_state=certificate.selection_state.value,
        lineage_parent_ids=list(certificate.lineage_parent_ids),
        target_record_id=certificate.target_record_id,
        expected_fact_version=certificate.expected_fact_version,
        created_at=certificate.created_at,
    )


def test_migration_old_schema_to_v5(tmp_path: Path) -> None:
    from app.adapters.database.repositories import (
        install_sqlite_pragmas,
        stamp_schema_version,
    )

    db_path = tmp_path / "old.db"
    _legacy_db(db_path)
    engine = _engine(db_path)
    install_sqlite_pragmas(engine)
    Base.metadata.create_all(engine)
    stamp_schema_version(engine)
    with engine.connect() as connection:
        tables = {
            row[0]
            for row in connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        }
        assert {
            "candidate_certificates",
            "human_decisions",
            "fact_transitions",
            "authority_meta",
        }.issubset(tables)
        assert connection.execute(text("PRAGMA user_version")).scalar_one() == 5
        era = connection.execute(
            text("SELECT value FROM authority_meta WHERE key='certificate_era_started_at'")
        ).scalar_one()
        assert datetime.fromisoformat(era).tzinfo is not None
        # legacy rows intact and readable
        form = connection.execute(
            text("SELECT review_status, current_record_version FROM forms WHERE form_id='FORM-OLD'")
        ).one()
        assert form.current_record_version == 1
        version = connection.execute(
            text("SELECT version, \"values\" FROM record_versions WHERE record_id='REC-OLD-1'")
        ).one()
        assert version.values == '{"total_quantity": 7}'
    # idempotent re-run (era row is not duplicated)
    install_sqlite_pragmas(engine)
    Base.metadata.create_all(engine)
    stamp_schema_version(engine)
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA user_version")).scalar_one() == 5
        rows = connection.execute(
            text("SELECT COUNT(*) FROM authority_meta WHERE key='certificate_era_started_at'")
        ).scalar_one()
        assert rows == 1


def test_user_version_above_5_refuses_startup(tmp_path: Path) -> None:
    from app.adapters.database.repositories import stamp_schema_version

    db_path = tmp_path / "future.db"
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA user_version=6")
    connection.commit()
    connection.close()
    engine = _engine(db_path)
    with pytest.raises(RuntimeError):
        stamp_schema_version(engine)


def test_utcdatetime_round_trip(tmp_path: Path) -> None:
    engine = _engine(tmp_path / "ts.db")
    Base.metadata.create_all(engine)
    _seed(engine)
    with Session(engine) as session, session.begin():
        session.add(_cert_row())
    with Session(engine) as session:
        row = session.get(CandidateCertificateRow, _cert_row().certificate_id)
        assert row is not None
        assert row.created_at == NOW
        assert row.created_at.tzinfo is not None


def test_naive_timestamp_rejected_before_persist(tmp_path: Path) -> None:
    engine = _engine(tmp_path / "naive.db")
    Base.metadata.create_all(engine)
    _seed(engine)
    row = _cert_row()
    row.created_at = datetime(2026, 8, 17, 9, 0)  # naive
    with Session(engine) as session, session.begin():
        with pytest.raises(StatementError) as exc_info:
            session.add(row)
            session.flush()
    assert isinstance(exc_info.value.orig, ValueError)


def test_field_id_fk_requires_existing_field(tmp_path: Path) -> None:
    engine = _engine(tmp_path / "fk.db")
    Base.metadata.create_all(engine)
    _seed(engine)
    row = _cert_row()
    row.field_id = "NO-SUCH-FIELD"
    with Session(engine) as session, session.begin():
        with pytest.raises(IntegrityError):
            session.add(row)
            session.flush()


def test_recognition_attempt_id_unique_and_nullable(tmp_path: Path) -> None:
    engine = _engine(tmp_path / "uniq.db")
    Base.metadata.create_all(engine)
    _seed(engine)
    first = _cert_row()
    second = _cert_row()
    second.candidate_id = "manual-2"
    second.recognition_attempt_id = "ATTEMPT-1"
    first.recognition_attempt_id = "ATTEMPT-1"
    with Session(engine) as session, session.begin():
        with pytest.raises(IntegrityError):
            session.add(first)
            session.add(second)
            session.flush()


def test_transition_unique_form_version_field(tmp_path: Path) -> None:
    engine = _engine(tmp_path / "uniq2.db")
    Base.metadata.create_all(engine)
    _seed(engine)
    with Session(engine) as session, session.begin():
        session.add(_cert_row())
    base = dict(
        form_id="FORM-1",
        created_version=1,
        field_key="total_quantity",
        record_id="FORM-1",
        record_version_id="REC-1",
        decision_id="D-1",
        certificate_id=_cert_row().certificate_id,
        evidence_hash="ab" * 32,
        evidence_locator="FORM-1/manual/total_quantity",
        producer_id="human-reviewer",
        producer_version="manual-entry-v1",
        template_id="T1",
        template_version="1",
        source_kind=SourceKind.MANUAL_ENTRY.value,
        created_at=NOW,
    )
    with Session(engine) as session, session.begin():
        session.add(FactTransitionRow(transition_id="T-1", **base))
        with pytest.raises(IntegrityError):
            session.add(FactTransitionRow(transition_id="T-2", **base))
            session.flush()


# ---------------------------------------------------------------------------
# Task C: repository authority layer (discard, loaders, CAS unit, ports)
# ---------------------------------------------------------------------------


def test_discard_removes_file(tmp_path: Path) -> None:
    from app.adapters.storage.local import LocalEvidenceStorage

    storage = LocalEvidenceStorage(tmp_path / "evidence")
    stored = storage.store_bytes(b"payload", ".png", "field-crops")
    target = tmp_path / "evidence" / stored.uri
    assert target.exists()
    storage.discard(stored.uri)
    assert not target.exists()


def test_discard_missing_file_is_noop(tmp_path: Path) -> None:
    from app.adapters.storage.local import LocalEvidenceStorage

    storage = LocalEvidenceStorage(tmp_path / "evidence")
    storage.discard("field-crops/ab/file.png")


@pytest.mark.parametrize("uri", ["../escape.png", "field-crops/../../escape.png", "/absolute.png"])
def test_discard_refuses_traversal(tmp_path: Path, uri: str) -> None:
    from app.adapters.storage.local import LocalEvidenceStorage

    storage = LocalEvidenceStorage(tmp_path / "evidence")
    with pytest.raises(ValueError):
        storage.discard(uri)


def test_certificate_loader_round_trip_preserves_stored_id(tmp_path: Path) -> None:
    from app.adapters.database.repositories import SqlAlchemyFormRepository

    engine = _engine(tmp_path / "loaders.db")
    Base.metadata.create_all(engine)
    _seed(engine)
    repository = SqlAlchemyFormRepository(engine)
    certificate = CandidateCertificate.from_manual_entry(
        candidate_id="manual-1",
        field_key="total_quantity",
        value=7,
        form_id="FORM-1",
        evidence_hash="ab" * 32,
        evidence_locator="FORM-1/manual/total_quantity",
        template_id="T1",
        template_version="1",
        target_record_id="FORM-1",
        expected_fact_version=0,
        created_at=NOW,
    )
    repository.add_certificate(
        certificate,
        field_id=None,
        evidence_file_id="EVID-1",
        recognition_attempt_id=None,
    )
    loaded = repository.get_certificate(certificate.certificate_id)
    assert loaded is not None
    assert loaded.certificate_id == certificate.certificate_id
    assert loaded.value == 7
    assert loaded.verify_content_address() is True
    assert repository.list_certificates_for_form("FORM-1") == [loaded]


def test_tampered_certificate_row_detected(tmp_path: Path) -> None:
    from app.adapters.database.repositories import SqlAlchemyFormRepository
    from app.domain.authority import (
        AuthorityContext,
        HumanDecision,
        TransitionAttempt,
        verify_transition_authorization,
    )

    engine = _engine(tmp_path / "tamper.db")
    Base.metadata.create_all(engine)
    _seed(engine)
    repository = SqlAlchemyFormRepository(engine)
    certificate = CandidateCertificate.from_manual_entry(
        candidate_id="manual-1",
        field_key="total_quantity",
        value=7,
        form_id="FORM-1",
        evidence_hash="ab" * 32,
        evidence_locator="FORM-1/manual/total_quantity",
        template_id="T1",
        template_version="1",
        target_record_id="FORM-1",
        expected_fact_version=0,
        created_at=NOW,
    )
    repository.add_certificate(
        certificate,
        field_id=None,
        evidence_file_id="EVID-1",
        recognition_attempt_id=None,
    )
    # tamper the stored value_payload directly
    from sqlalchemy import update as sa_update

    from app.adapters.database.models import CandidateCertificateRow

    with engine.connect() as connection:
        connection.execute(
            sa_update(CandidateCertificateRow)
            .where(CandidateCertificateRow.certificate_id == certificate.certificate_id)
            .values(value_payload="999")
        )
        connection.commit()
    loaded = repository.get_certificate(certificate.certificate_id)
    assert loaded is not None
    assert loaded.verify_content_address() is False
    context = AuthorityContext(
        evidence_sha256="ab" * 32,
        current_fact_version=0,
        known_sources=frozenset({SourceKind.MANUAL_ENTRY}),
        known_producers=frozenset({("human-reviewer", "manual-entry-v1")}),
        known_selection_artifacts=frozenset(),
        now=NOW,
    )
    attempt = TransitionAttempt(
        fact_version=1,
        record_id="FORM-1",
        evidence_sha256="ab" * 32,
        decision=HumanDecision(
            decision_id="D-1",
            reviewer_id="reviewer-1",
            candidate_id="manual-1",
            field_key="total_quantity",
            reason="ok",
            decided_at=NOW,
        ),
        certificate=loaded,
    )
    assert verify_transition_authorization(attempt, context) != ()


def test_append_candidate_unit_rejects_cross_form_field(tmp_path: Path) -> None:
    from app.adapters.database.repositories import SqlAlchemyFormRepository
    from app.domain.models import (
        AuditEvent,
        EvidenceFile,
        EvidenceType,
        Form,
        FormField,
        RecognitionAttempt,
    )

    engine = _engine(tmp_path / "cross.db")
    Base.metadata.create_all(engine)
    _seed(engine)
    repository = SqlAlchemyFormRepository(engine)
    repository.add_form(Form(form_id="FORM-OTHER", template_id="T1", template_version="1"))
    repository.add_form_field(
        FormField("FIELD-OTHER", "FORM-OTHER", "total_quantity", {"x": 0, "y": 0, "w": 8, "h": 8})
    )
    certificate = CandidateCertificate.from_manual_entry(
        candidate_id="manual-1",
        field_key="total_quantity",
        value=7,
        form_id="FORM-1",
        evidence_hash="ab" * 32,
        evidence_locator="FORM-1/manual/total_quantity",
        template_id="T1",
        template_version="1",
        target_record_id="FORM-1",
        expected_fact_version=0,
        created_at=NOW,
    )
    evidence = EvidenceFile(
        file_id="EVID-2",
        form_id="FORM-1",
        type=EvidenceType.ORIGINAL_IMAGE,
        uri="ev-2",
        sha256="ab" * 32,
    )
    attempt = RecognitionAttempt(
        attempt_id="ATTEMPT-1",
        field_id="FIELD-OTHER",
        engine="manual",
        model_version="1",
        candidate_value=7,
        confidence=0.0,
        crop_file_id="EVID-2",
    )
    audit = AuditEvent(
        event_id="EVENT-1",
        form_id="FORM-1",
        event_type="RECOGNIZE",
        actor_id="x",
        after={"attempt_id": "ATTEMPT-1"},
    )
    with pytest.raises(ValueError):
        repository.append_candidate_unit(
            evidence=evidence,
            attempt=attempt,
            certificate=certificate,
            audit=audit,
            field_id="FIELD-OTHER",
        )


def test_append_candidate_unit_persists_all_rows(tmp_path: Path) -> None:
    from app.adapters.database.repositories import SqlAlchemyFormRepository
    from app.domain.models import (
        AuditEvent,
        EvidenceFile,
        EvidenceType,
        FormField,
        RecognitionAttempt,
    )

    engine = _engine(tmp_path / "unit.db")
    Base.metadata.create_all(engine)
    _seed(engine)
    repository = SqlAlchemyFormRepository(engine)
    repository.add_form_field(
        FormField("FIELD-1", "FORM-1", "total_quantity", {"x": 0, "y": 0, "w": 8, "h": 8})
    )
    certificate = CandidateCertificate.from_manual_entry(
        candidate_id="manual-1",
        field_key="total_quantity",
        value=7,
        form_id="FORM-1",
        evidence_hash="ab" * 32,
        evidence_locator="FORM-1/manual/total_quantity",
        template_id="T1",
        template_version="1",
        target_record_id="FORM-1",
        expected_fact_version=0,
        created_at=NOW,
    )
    evidence = EvidenceFile(
        file_id="EVID-2",
        form_id="FORM-1",
        type=EvidenceType.ORIGINAL_IMAGE,
        uri="ev-2",
        sha256="ab" * 32,
    )
    attempt = RecognitionAttempt(
        attempt_id="ATTEMPT-1",
        field_id="FIELD-1",
        engine="manual",
        model_version="1",
        candidate_value=7,
        confidence=0.0,
        crop_file_id="EVID-2",
    )
    audit = AuditEvent(
        event_id="EVENT-1",
        form_id="FORM-1",
        event_type="RECOGNIZE",
        actor_id="x",
        after={"attempt_id": "ATTEMPT-1"},
    )
    repository.append_candidate_unit(
        evidence=evidence,
        attempt=attempt,
        certificate=certificate,
        audit=audit,
        field_id="FIELD-1",
    )
    assert repository.get_certificate(certificate.certificate_id) is not None
    assert len(repository.list_audit_events("FORM-1")) == 1
    assert len(repository.list_recognition_attempts("FIELD-1")) == 1
    assert len(repository.list_evidence("FORM-1")) == 2


def _seed_version(engine: Engine) -> None:
    """Form with current_record_version=0 plus its evidence."""
    from app.adapters.database.repositories import SqlAlchemyFormRepository
    from app.domain.models import AuditEvent, FormField

    _seed(engine)
    repository = SqlAlchemyFormRepository(engine)
    repository.add_form_field(
        FormField(
            "FIELD-1",
            "FORM-1",
            "total_quantity",
            {"x": 0, "y": 0, "w": 8, "h": 8},
        )
    )
    repository.add_audit_event(
        AuditEvent(
            event_id="EVENT-SEED",
            form_id="FORM-1",
            event_type="IMPORT",
            actor_id="op",
            after={"file_id": "EVID-1"},
        )
    )


def _ready_cert() -> CandidateCertificate:
    from app.domain.evidence_identity import canonical_evidence_locator

    return CandidateCertificate.from_manual_entry(
        candidate_id="manual-1",
        field_key="total_quantity",
        value=7,
        form_id="FORM-1",
        evidence_hash="ab" * 32,
        evidence_locator=canonical_evidence_locator(
            form_id="FORM-1", related_field_id=None, uri="ev-1"
        ),
        template_id="T1",
        template_version="1",
        target_record_id="FORM-1",
        expected_fact_version=0,
        created_at=NOW,
    )


def _confirm_args():
    from app.domain.authority import FactTransition, HumanDecision
    from app.domain.models import AuditEvent, RecordStatus, RecordVersion

    certificate = _ready_cert()
    decision = HumanDecision(
        decision_id="D-1",
        reviewer_id="reviewer-1",
        candidate_id="manual-1",
        field_key="total_quantity",
        reason="ok",
        decided_at=NOW,
    )
    transition = FactTransition(
        transition_id="T-1",
        record_id="FORM-1",
        field_key="total_quantity",
        created_version=1,
        record_version_id="REC-1",
        decision_id="D-1",
        certificate_id=certificate.certificate_id,
        evidence_sha256="ab" * 32,
        evidence_locator=certificate.evidence_locator,
        producer_id="human-reviewer",
        producer_version="manual-entry-v1",
        source_kind=SourceKind.MANUAL_ENTRY,
        template_id="T1",
        template_version="1",
        value_payload=canonical_json(7),
        created_at=NOW,
    )
    binding = AuthorizationBinding(
        binding_id="AUTH-1",
        decision_id="D-1",
        certificate_id=certificate.certificate_id,
        authorized_value_payload=canonical_json(7),
        bound_at=NOW,
    )
    record = RecordVersion(
        record_id="REC-1",
        form_id="FORM-1",
        version=1,
        status=RecordStatus.CONFIRMED,
        values={"total_quantity": 7},
        change_reason="ok",
        confirmed_by="reviewer-1",
        created_at=NOW,
    )
    audit = AuditEvent(
        event_id="EVENT-1",
        form_id="FORM-1",
        event_type="CONFIRM",
        actor_id="reviewer-1",
        after={"total_quantity": 7},
        evidence_ids=("EVID-1",),
    )
    return certificate, decision, transition, record, audit, binding


def test_append_fact_transition_cas_conflict(tmp_path: Path) -> None:
    from app.adapters.database.repositories import SqlAlchemyFormRepository
    from app.domain.models import ReviewStatus

    engine = _engine(tmp_path / "cas.db")
    Base.metadata.create_all(engine)
    _seed_version(engine)
    repository = SqlAlchemyFormRepository(engine)
    certificate, decision, transition, record, audit, binding = _confirm_args()
    repository.add_certificate(
        certificate,
        field_id=None,
        evidence_file_id="EVID-1",
        recognition_attempt_id=None,
    )
    ok = repository.append_fact_transition(
        form_id="FORM-1",
        expected_version=0,
        record=record,
        decisions=[decision],
        transitions=[transition],
        derived_certificates=[],
        authorization_bindings=[binding],
        audit=audit,
        review_status=ReviewStatus.CONFIRMED,
        export_status=None,
    )
    assert ok is True
    stale = repository.append_fact_transition(
        form_id="FORM-1",
        expected_version=0,
        record=record,
        decisions=[decision],
        transitions=[transition],
        derived_certificates=[],
        authorization_bindings=[binding],
        audit=audit,
        review_status=ReviewStatus.CONFIRMED,
        export_status=None,
    )
    assert stale is False
    versions = repository.list_record_versions("FORM-1")
    assert len(versions) == 1


def test_concurrent_confirm_exactly_one_succeeds(tmp_path: Path) -> None:
    import threading

    from app.adapters.database.repositories import SqlAlchemyFormRepository
    from app.domain.models import ReviewStatus

    db_path = tmp_path / "concurrent.db"
    engine = _engine(db_path)
    Base.metadata.create_all(engine)
    _seed_version(engine)

    outcomes: list[bool] = []
    barrier = threading.Barrier(2)
    lock = threading.Lock()

    # The certificate exists before the race; workers only run the CAS unit
    # (inserting the same certificate from two threads would deadlock the
    # barrier on the UNIQUE candidate_id).
    repository = SqlAlchemyFormRepository(engine)
    certificate, decision, transition, record, audit, binding = _confirm_args()
    repository.add_certificate(
        certificate,
        field_id=None,
        evidence_file_id="EVID-1",
        recognition_attempt_id=None,
    )

    def worker() -> None:
        worker_engine = create_engine(f"sqlite:///{db_path}")
        worker_repository = SqlAlchemyFormRepository(worker_engine)
        barrier.wait()
        result = worker_repository.append_fact_transition(
            form_id="FORM-1",
            expected_version=0,
            record=record,
            decisions=[decision],
            transitions=[transition],
            derived_certificates=[],
            authorization_bindings=[binding],
            audit=audit,
            review_status=ReviewStatus.CONFIRMED,
            export_status=None,
        )
        with lock:
            outcomes.append(result)
        worker_engine.dispose()

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == [False, True]
    # The winner produces exactly one complete admission unit; the loser
    # leaves no partial version/decision/binding/transition rows.
    versions = repository.list_record_versions("FORM-1")
    assert len(versions) == 1
    assert len(repository.list_decisions_for_form("FORM-1")) == 1
    assert len(repository.list_authorization_bindings_for_form("FORM-1")) == 1
    transitions = repository.list_transitions_for_version("FORM-1", 1)
    assert len(transitions) == 1
    assert versions[0].fact_sources["total_quantity"] == transitions[0].transition_id
    assert len(repository.list_audit_events("FORM-1")) == 2  # IMPORT + CONFIRM


def test_cas_lock_without_retry_returns_conflict(tmp_path: Path) -> None:
    import sqlite3

    from app.adapters.database.repositories import SqlAlchemyFormRepository
    from app.domain.models import ReviewStatus

    db_path = tmp_path / "locked.db"
    engine = _engine(db_path)
    Base.metadata.create_all(engine)
    _seed_version(engine)
    repository = SqlAlchemyFormRepository(engine)
    certificate, decision, transition, record, audit, binding = _confirm_args()
    repository.add_certificate(
        certificate,
        field_id=None,
        evidence_file_id="EVID-1",
        recognition_attempt_id=None,
    )
    blocker = sqlite3.connect(db_path)
    blocker.execute("BEGIN EXCLUSIVE")
    try:
        locked_engine = create_engine(f"sqlite:///{db_path}", connect_args={"timeout": 0.1})
        locked_repository = SqlAlchemyFormRepository(locked_engine)
        result = locked_repository.append_fact_transition(
            form_id="FORM-1",
            expected_version=0,
            record=record,
            decisions=[decision],
            transitions=[transition],
            derived_certificates=[],
            authorization_bindings=[binding],
            audit=audit,
            review_status=ReviewStatus.CONFIRMED,
            export_status=None,
        )
        assert result is False
        locked_engine.dispose()
    finally:
        blocker.execute("ROLLBACK")
        blocker.close()
    assert len(repository.list_record_versions("FORM-1")) == 0


# ---------------------------------------------------------------------------
# Task E: RecognizeForms atomic candidate + certificate persistence
# ---------------------------------------------------------------------------


def _recognize_env(tmp_path: Path, *, with_field: bool = True):
    """Form + field + recognition service on a scratch database."""
    import numpy as np

    from app.adapters.database.repositories import SqlAlchemyFormRepository
    from app.adapters.recognition.candidate import RecognitionCandidate
    from app.adapters.recognition.opencv import OpenCvImagePipeline
    from app.adapters.storage.local import LocalEvidenceStorage
    from app.application.recognize_forms import RecognizeForms
    from app.domain.models import Form, FormField

    engine = _engine(tmp_path / "recognize.db")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    repository.add_form(Form(form_id="FORM-1", template_id="T1", template_version="1"))
    if with_field:
        repository.add_form_field(
            FormField("FIELD-1", "FORM-1", "total_quantity", {"x": 0, "y": 0, "w": 8, "h": 8})
        )
    storage = LocalEvidenceStorage(tmp_path / "evidence")
    recognition = RecognizeForms(
        repository,
        repository,
        repository,
        storage,
        OpenCvImagePipeline(),
        candidate_writer=repository,
    )
    crop = np.full((64, 48), 255, dtype=np.uint8)
    candidate = RecognitionCandidate("7", 0.9, "recognizer-a", "1.0", "OK")
    return repository, recognition, crop, candidate, storage


def test_recognition_atomicity_on_db_failure(tmp_path: Path) -> None:
    # No FormFieldRow for FIELD-1 -> the unit must fail, roll back, and
    # discard the already-written crop file.
    repository, recognition, crop, candidate, storage = _recognize_env(tmp_path, with_field=False)
    with pytest.raises(ValueError):
        recognition.record_candidate("FORM-1", "FIELD-1", crop, candidate, "machine")
    assert repository.list_evidence("FORM-1") == []
    assert len(repository.list_audit_events("FORM-1")) == 0
    assert repository.list_certificates_for_form("FORM-1") == []
    assert len(list((tmp_path / "evidence").rglob("*"))) == 0


def test_recognition_persists_certificate_content(tmp_path: Path) -> None:
    from app.domain.authority import SelectionState

    repository, recognition, crop, candidate, _ = _recognize_env(tmp_path)
    attempt = recognition.record_candidate("FORM-1", "FIELD-1", crop, candidate, "machine")
    certificates = repository.list_certificates_for_form("FORM-1")
    assert len(certificates) == 1
    certificate = certificates[0]
    assert certificate.candidate_id == attempt.attempt_id
    assert certificate.field_key == "total_quantity"
    assert certificate.target_record_id == "FORM-1"
    assert certificate.expected_fact_version == 0
    from app.domain.evidence_identity import locator_from_evidence

    evidence = repository.list_evidence("FORM-1")
    assert len(evidence) == 1
    assert certificate.evidence_locator == locator_from_evidence(evidence[0])
    assert certificate.selection_artifact_id == "recognition-threshold-v1"
    assert certificate.source_kind is SourceKind.RECOGNITION
    assert certificate.selection_state is SelectionState.SELECTED
    assert certificate.verify_content_address() is True
    # evidence hash comes from the stored crop row, never from the caller
    assert certificate.evidence_hash == evidence[0].sha256
    assert certificate.evidence_hash != "ab" * 32
    assert len(repository.list_audit_events("FORM-1")) == 1
    assert len(repository.list_recognition_attempts("FIELD-1")) == 1


def test_recognition_abstained_certificate(tmp_path: Path) -> None:
    from app.adapters.recognition.candidate import RecognitionCandidate
    from app.domain.authority import SelectionState

    repository, recognition, crop, _, _ = _recognize_env(tmp_path)
    abstained = RecognitionCandidate(None, 0.0, "recognizer-a", "1.0", "LOW_CONF", accepted=False)
    recognition.record_candidate("FORM-1", "FIELD-1", crop, abstained, "machine")
    certificate = repository.list_certificates_for_form("FORM-1")[0]
    assert certificate.selection_state is SelectionState.ABSTAINED
    assert certificate.value is None


# ---------------------------------------------------------------------------
# Task D: ReviewForms evidence-bound confirm (red tests)
# ---------------------------------------------------------------------------


def _review_env(tmp_path: Path):
    """Form + evidence + review service with registries."""
    from app.adapters.database.repositories import SqlAlchemyFormRepository
    from app.application.review_forms import ReviewForms

    tmp_path.mkdir(parents=True, exist_ok=True)
    engine = _engine(tmp_path / "review.db")
    Base.metadata.create_all(engine)
    _seed_version(engine)
    repository = SqlAlchemyFormRepository(engine)
    reviews = ReviewForms(
        repository,
        repository,
        authority_read=repository,
        admission=repository,
        known_producers=frozenset(
            {
                ("human-reviewer", "manual-entry-v1"),
                ("recognizer-a", "1.0"),
            }
        ),
        known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
    )
    return engine, repository, reviews


def test_confirm_manual_entry_creates_transition(tmp_path: Path) -> None:
    _, repository, reviews = _review_env(tmp_path)
    record = reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
    )
    assert record.version == 1
    certificates = repository.list_certificates_for_form("FORM-1")
    assert len(certificates) == 1
    assert certificates[0].source_kind is SourceKind.MANUAL_ENTRY
    assert certificates[0].value == 7
    transitions = repository.list_transitions_for_version("FORM-1", 1)
    assert len(transitions) == 1
    assert transitions[0].field_key == "total_quantity"
    assert transitions[0].record_id == "FORM-1"
    assert transitions[0].certificate_id == certificates[0].certificate_id
    decisions = repository.list_decisions_for_form("FORM-1")
    assert len(decisions) == 1
    assert decisions[0].field_key == "total_quantity"
    assert decisions[0].candidate_id == certificates[0].candidate_id
    confirm_events = [
        a for a in repository.list_audit_events("FORM-1") if a.event_type == "CONFIRM"
    ]
    assert len(confirm_events) == 1
    assert confirm_events[0].evidence_ids == ("EVID-1",)
    # record_version_id points at the version row
    versions = repository.list_record_versions("FORM-1")
    assert transitions[0].created_version == versions[-1].version


def test_confirm_rejects_input_invariants(tmp_path: Path) -> None:
    from app.application.review_forms import AuthorityRejectionError

    _, _, reviews = _review_env(tmp_path)
    base = dict(
        form_id="FORM-1",
        expected_version=0,
        actor_id="reviewer-1",
        reason="ok",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
    )
    with pytest.raises(AuthorityRejectionError):
        reviews.confirm(**base, values={})
    with pytest.raises(AuthorityRejectionError):
        reviews.confirm(**base, values={" total_quantity ": 7})
    with pytest.raises(AuthorityRejectionError):
        reviews.confirm(
            **{**base, "certificate_ids_by_field": {"total_quantity": None}},
            values={"total_quantity": 7, "extra": 1},
        )
    with pytest.raises(AuthorityRejectionError):
        reviews.confirm(
            **{**base, "manual_evidence_ids_by_field": {}},
            values={"total_quantity": 7},
        )
    with pytest.raises(AuthorityRejectionError):
        reviews.confirm(
            **{**base, "certificate_ids_by_field": {"total_quantity": "NO-SUCH-CERT"}},
            values={"total_quantity": 7},
        )


def test_confirm_machine_certificate_value_binding(tmp_path: Path) -> None:
    from app.adapters.recognition.candidate import RecognitionCandidate
    from app.domain.models import AuditEvent

    engine, repository, reviews = _review_env(tmp_path)
    import numpy as np

    from app.adapters.recognition.opencv import OpenCvImagePipeline
    from app.adapters.storage.local import LocalEvidenceStorage
    from app.application.recognize_forms import RecognizeForms

    recognition = RecognizeForms(
        repository,
        repository,
        repository,
        LocalEvidenceStorage(tmp_path / "evidence"),
        OpenCvImagePipeline(),
        candidate_writer=repository,
    )
    crop = np.full((64, 48), 255, dtype=np.uint8)
    recognition.record_candidate(
        "FORM-1",
        "FIELD-1",
        crop,
        RecognitionCandidate(7, 0.9, "recognizer-a", "1.0", "OK"),
        "machine",
    )
    cert = repository.list_certificates_for_form("FORM-1")[0]

    # 1) matching value: the machine certificate is used as-is
    record = reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": cert.certificate_id},
        manual_evidence_ids_by_field={},
    )
    assert record.version == 1
    transitions = repository.list_transitions_for_version("FORM-1", 1)
    assert transitions[0].certificate_id == cert.certificate_id

    # 2) human modifies the value: derived MANUAL_ENTRY with lineage parent
    repository.add_audit_event(
        AuditEvent(
            event_id="EVENT-2",
            form_id="FORM-1",
            event_type="CONFIRM",
            actor_id="reviewer-1",
            evidence_ids=(),
        )
    )
    # note: a second confirm on the same version would be stale; build a
    # fresh form in a separate database instead
    engine2, repository2, reviews2 = _review_env(tmp_path / "second")
    recognition2 = RecognizeForms(
        repository2,
        repository2,
        repository2,
        LocalEvidenceStorage(tmp_path / "evidence2"),
        OpenCvImagePipeline(),
        candidate_writer=repository2,
    )
    recognition2.record_candidate(
        "FORM-1",
        "FIELD-1",
        crop,
        RecognitionCandidate(7, 0.9, "recognizer-a", "1.0", "OK"),
        "machine",
    )
    cert2 = repository2.list_certificates_for_form("FORM-1")[0]
    reviews2.confirm(
        "FORM-1",
        0,
        {"total_quantity": 8},
        "reviewer-1",
        "corrected",
        certificate_ids_by_field={"total_quantity": cert2.certificate_id},
        manual_evidence_ids_by_field={},
    )
    # G3b correction semantics: keep the original machine certificate;
    # freeze the human-authorized corrected value in AuthorizationBinding.
    certs2 = repository2.list_certificates_for_form("FORM-1")
    assert len(certs2) == 1
    assert certs2[0].certificate_id == cert2.certificate_id
    transitions2 = repository2.list_transitions_for_version("FORM-1", 1)
    assert transitions2[0].certificate_id == cert2.certificate_id
    assert transitions2[0].value == 8
    bindings2 = repository2.list_authorization_bindings_for_form("FORM-1")
    assert len(bindings2) == 1
    assert bindings2[0].certificate_id == cert2.certificate_id
    assert bindings2[0].value == 8
    versions2 = repository2.list_record_versions("FORM-1")
    assert versions2[-1].fact_sources["total_quantity"] == transitions2[0].transition_id
    audit = [a for a in repository2.list_audit_events("FORM-1") if a.event_type == "CONFIRM"][0]
    assert audit.evidence_ids == (
        repository2.get_certificate_evidence_file_id(cert2.certificate_id),
    )


def test_confirm_abstained_persists_manual_resolution(tmp_path: Path) -> None:
    import numpy as np

    from app.adapters.recognition.candidate import RecognitionCandidate
    from app.adapters.recognition.opencv import OpenCvImagePipeline
    from app.adapters.storage.local import LocalEvidenceStorage
    from app.application.recognize_forms import RecognizeForms
    from app.domain.authority import SelectionState

    engine, repository, reviews = _review_env(tmp_path)
    recognition = RecognizeForms(
        repository,
        repository,
        repository,
        LocalEvidenceStorage(tmp_path / "evidence"),
        OpenCvImagePipeline(),
        candidate_writer=repository,
    )
    crop = np.full((64, 48), 255, dtype=np.uint8)
    recognition.record_candidate(
        "FORM-1",
        "FIELD-1",
        crop,
        RecognitionCandidate(None, 0.0, "recognizer-a", "1.0", "LOW", accepted=False),
        "machine",
    )
    cert = repository.list_certificates_for_form("FORM-1")[0]
    assert cert.selection_state is SelectionState.ABSTAINED
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 9},
        "reviewer-1",
        "manual resolution",
        certificate_ids_by_field={"total_quantity": cert.certificate_id},
        manual_evidence_ids_by_field={},
    )
    decisions = repository.list_decisions_for_form("FORM-1")
    assert decisions[0].manual_resolution is True


def test_confirm_stale_version_rejected(tmp_path: Path) -> None:
    from app.application.review_forms import ConcurrentReviewError

    _, repository, reviews = _review_env(tmp_path)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
    )
    with pytest.raises(ConcurrentReviewError):
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 8},
            "reviewer-2",
            "stale",
            certificate_ids_by_field={"total_quantity": None},
            manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
        )
    versions = repository.list_record_versions("FORM-1")
    assert len(versions) == 1


def test_no_public_add_record_version_bypass(tmp_path: Path) -> None:
    from app.adapters.database.repositories import SqlAlchemyFormRepository
    from app.application.ports import FormRepository

    engine = _engine(tmp_path / "nobypass.db")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    assert not hasattr(repository, "add_record_version")
    assert "add_record_version" not in dir(FormRepository)


def test_container_wiring_smoke(tmp_path: Path) -> None:
    from app.domain.models import FormField
    from app.services.container import build_services
    from config.settings import Settings

    settings = Settings(data_root=tmp_path / "data")
    services = build_services(settings)
    image = tmp_path / "form.png"
    image.write_bytes(b"container-form")
    evidence = services.imports.import_image(image, "FORM-1", "T1", "1", "operator")
    services.repository.add_form_field(
        FormField(
            "FIELD-1",
            "FORM-1",
            "total_quantity",
            {"x": 0, "y": 0, "w": 8, "h": 8},
        )
    )
    values = {"total_quantity": 7}
    record = services.reviews.confirm(
        "FORM-1",
        0,
        values,
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": evidence.file_id},
    )
    assert record.version == 1
    transitions = services.repository.list_transitions_for_version("FORM-1", 1)
    assert len(transitions) == 1
    assert transitions[0].field_key == "total_quantity"


# ---------------------------------------------------------------------------
# Task F: QueryForms.trace authority chain
# ---------------------------------------------------------------------------


def test_trace_complete_after_confirm(tmp_path: Path) -> None:
    from app.application.query_forms import QueryForms

    _, repository, reviews = _review_env(tmp_path)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
    )
    trace = QueryForms(repository).trace("FORM-1")
    assert trace.status == "complete"
    assert len(trace.fields) == 1
    field = trace.fields[0]
    assert field.field_key == "total_quantity"
    assert field.status == "complete"
    assert field.created_version == 1
    assert field.decision_id == "FORM-1:1:total_quantity"
    assert field.certificate_id is not None
    assert field.evidence_file_id == "EVID-1"
    assert field.failures == ()


def test_trace_pre_certificate_for_legacy_version(tmp_path: Path) -> None:
    from datetime import UTC, datetime

    from app.adapters.database.repositories import (
        SqlAlchemyFormRepository,
        stamp_schema_version,
    )
    from app.application.query_forms import QueryForms
    from app.domain.models import Form
    from tests.helpers.legacy_fixtures import add_legacy_record_version

    engine = _engine(tmp_path / "legacy.db")
    Base.metadata.create_all(engine)
    stamp_schema_version(engine)
    repository = SqlAlchemyFormRepository(engine)
    repository.add_form(Form("FORM-1", "T1", "1"))
    add_legacy_record_version(
        engine,
        form_id="FORM-1",
        version=1,
        values={"total_quantity": 7},
        confirmed_by="reviewer-old",
        created_at=datetime(2026, 1, 1, 9, 0, tzinfo=UTC),
    )
    trace = QueryForms(repository).trace("FORM-1")
    assert trace.status == "pre-certificate"
    assert trace.fields == ()


def test_trace_incomplete_after_corruption(tmp_path: Path) -> None:
    """Simulated disk corruption: FK disabled, decision row deleted."""
    import sqlite3

    from app.application.query_forms import QueryForms

    _, repository, reviews = _review_env(tmp_path)
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
    )
    db_path = tmp_path / "review.db"
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys=OFF")
    connection.execute("DELETE FROM human_decisions")
    connection.commit()
    connection.close()
    trace = QueryForms(repository).trace("FORM-1")
    assert trace.status == "incomplete"
    assert trace.fields[0].status == "incomplete"
    assert any("decision" in failure for failure in trace.fields[0].failures)


def test_trace_version_filter_and_compatibility(tmp_path: Path) -> None:
    from app.application.query_forms import QueryForms

    _, repository, reviews = _review_env(tmp_path)
    values = {"total_quantity": 7}
    reviews.confirm(
        "FORM-1",
        0,
        values,
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
    )
    reviews.confirm(
        "FORM-1",
        1,
        {"total_quantity": 8},
        "reviewer-1",
        "correction",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
    )
    queries = QueryForms(repository)
    latest = queries.trace("FORM-1")
    assert latest.status == "complete"
    assert latest.fields[0].created_version == 2
    first = queries.trace("FORM-1", 1)
    assert first.fields[0].created_version == 1
    assert len(first.versions) == 2  # history stays complete


# ---------------------------------------------------------------------------
# Codex REVISE round: P0 binding, completeness, and evidence ownership fixes
# ---------------------------------------------------------------------------


def _two_field_env(tmp_path):
    """FORM-1 with two recognized machine fields, ready for confirm."""
    import numpy as np

    from app.adapters.recognition.candidate import RecognitionCandidate
    from app.adapters.recognition.opencv import OpenCvImagePipeline
    from app.adapters.storage.local import LocalEvidenceStorage
    from app.application.recognize_forms import RecognizeForms
    from app.domain.models import FormField

    engine, repository, reviews = _review_env(tmp_path)
    repository.add_form_field(
        FormField("FIELD-2", "FORM-1", "qualified_quantity", {"x": 0, "y": 0, "w": 8, "h": 8})
    )
    recognition = RecognizeForms(
        repository,
        repository,
        repository,
        LocalEvidenceStorage(tmp_path / "evidence"),
        OpenCvImagePipeline(),
        candidate_writer=repository,
    )
    crop = np.full((64, 48), 255, dtype=np.uint8)
    recognition.record_candidate(
        "FORM-1",
        "FIELD-1",
        crop,
        RecognitionCandidate(7, 0.9, "recognizer-a", "1.0", "OK"),
        "machine",
    )
    recognition.record_candidate(
        "FORM-1",
        "FIELD-2",
        crop,
        RecognitionCandidate(5, 0.9, "recognizer-a", "1.0", "OK"),
        "machine",
    )
    certificates = repository.list_certificates_for_form("FORM-1")
    by_field = {certificate.field_key: certificate for certificate in certificates}
    assert set(by_field) == {"total_quantity", "qualified_quantity"}
    return engine, repository, reviews, by_field


def _confirm_two_fields(reviews, by_field) -> None:
    reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7, "qualified_quantity": 5},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={
            "total_quantity": by_field["total_quantity"].certificate_id,
            "qualified_quantity": by_field["qualified_quantity"].certificate_id,
        },
        manual_evidence_ids_by_field={},
    )


def _tamper(db_path, sql, params=()) -> None:
    """Run raw SQL with foreign keys off (corruption simulation)."""
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys=OFF")
    connection.execute(sql, params)
    connection.commit()
    connection.close()


def _assert_no_writes(repository, form_id: str) -> None:
    assert repository.list_record_versions(form_id) == []
    assert repository.list_transitions_for_version(form_id, 1) == []
    assert repository.list_decisions_for_form(form_id) == []
    assert repository.get_form(form_id).current_record_version == 0
    fact_events = [
        event
        for event in repository.list_audit_events(form_id)
        if event.event_type in ("CONFIRM", "CORRECT")
    ]
    assert fact_events == []


def test_confirm_rejects_cross_field_selected_certificate(tmp_path) -> None:
    """P0-1: a certificate for one field supplied under another rejects.

    The supplied value (8) also differs from the certificate value (7), so
    this doubles as the derived-manual substitution probe: the field binding
    must reject before any derivation happens.
    """
    from app.application.review_forms import AuthorityRejectionError

    engine, repository, reviews, by_field = _two_field_env(tmp_path)
    certificate = by_field["total_quantity"]
    with pytest.raises(AuthorityRejectionError) as exc_info:
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 7, "extra_field": 8},
            "reviewer-1",
            "ok",
            certificate_ids_by_field={
                "total_quantity": None,
                "extra_field": certificate.certificate_id,
            },
            manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
        )
    codes = {failure.code for failure in exc_info.value.failures}
    assert "FIELD_KEY_BINDING_MISMATCH" in codes
    _assert_no_writes(repository, "FORM-1")


def test_confirm_rejects_cross_field_abstained_certificate(tmp_path) -> None:
    """P0-1: abstained-path substitution rejects before manual resolution."""
    import numpy as np

    from app.adapters.recognition.candidate import RecognitionCandidate
    from app.adapters.recognition.opencv import OpenCvImagePipeline
    from app.adapters.storage.local import LocalEvidenceStorage
    from app.application.recognize_forms import RecognizeForms
    from app.application.review_forms import AuthorityRejectionError

    engine, repository, reviews = _review_env(tmp_path)
    recognition = RecognizeForms(
        repository,
        repository,
        repository,
        LocalEvidenceStorage(tmp_path / "evidence"),
        OpenCvImagePipeline(),
        candidate_writer=repository,
    )
    crop = np.full((64, 48), 255, dtype=np.uint8)
    recognition.record_candidate(
        "FORM-1",
        "FIELD-1",
        crop,
        RecognitionCandidate(None, 0.0, "recognizer-a", "1.0", "LOW", accepted=False),
        "machine",
    )
    certificate = repository.list_certificates_for_form("FORM-1")[0]
    assert certificate.field_key == "total_quantity"
    with pytest.raises(AuthorityRejectionError) as exc_info:
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 9, "extra_field": 9},
            "reviewer-1",
            "ok",
            certificate_ids_by_field={
                "total_quantity": None,
                "extra_field": certificate.certificate_id,
            },
            manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
        )
    codes = {failure.code for failure in exc_info.value.failures}
    assert "FIELD_KEY_BINDING_MISMATCH" in codes
    _assert_no_writes(repository, "FORM-1")


@pytest.mark.parametrize(
    ("table", "column", "value", "expected_failure"),
    [
        (
            "fact_transitions",
            "producer_id",
            "tampered-producer",
            "transition producer binding mismatch",
        ),
        (
            "fact_transitions",
            "producer_version",
            "tampered",
            "transition producer version mismatch",
        ),
        (
            "fact_transitions",
            "template_id",
            "TAMPERED",
            "transition template binding mismatch",
        ),
        (
            "fact_transitions",
            "template_version",
            "99",
            "transition template version mismatch",
        ),
        (
            "fact_transitions",
            "source_kind",
            "MANUAL_ENTRY",
            "transition source kind mismatch",
        ),
        (
            "fact_transitions",
            "evidence_hash",
            "ff" * 32,
            "transition is not bound to the evidence",
        ),
        (
            "fact_transitions",
            "evidence_locator",
            "tampered/locator",
            "transition evidence locator mismatch",
        ),
        (
            "fact_transitions",
            "record_id",
            "FORM-OTHER",
            "transition record binding mismatch",
        ),
        # A transition moved to another created_version no longer belongs
        # to this version: the field reports missing, never complete.
        (
            "fact_transitions",
            "created_version",
            99,
            "missing transition for field total_quantity",
        ),
        # A wrong-but-existing record-version row id is a provenance lie:
        # the FK proves only that SOME row exists.
        (
            "fact_transitions",
            "record_version_id",
            "REC-NEXT",
            "transition record-version row mismatch",
        ),
        (
            "fact_transitions",
            "field_key",
            "tampered_field",
            "transition field binding mismatch",
        ),
        (
            "fact_transitions",
            "decision_id",
            "NO-SUCH-DECISION",
            "missing decision",
        ),
        (
            "fact_transitions",
            "certificate_id",
            "NO-SUCH-CERT",
            "missing certificate",
        ),
        (
            "candidate_certificates",
            "field_key",
            "tampered_field",
            "certificate content address mismatch",
        ),
        (
            "candidate_certificates",
            "producer_id",
            "tampered-producer",
            "certificate content address mismatch",
        ),
        (
            "candidate_certificates",
            "evidence_hash",
            "ff" * 32,
            "certificate content address mismatch",
        ),
        (
            "candidate_certificates",
            "value_payload",
            '"999"',
            "certificate content address mismatch",
        ),
        (
            "candidate_certificates",
            "target_record_id",
            "FORM-OTHER",
            "certificate content address mismatch",
        ),
        (
            "candidate_certificates",
            "expected_fact_version",
            5,
            "certificate content address mismatch",
        ),
        (
            "human_decisions",
            "candidate_id",
            "other-candidate",
            "decision is not bound to the certificate",
        ),
        (
            "human_decisions",
            "field_key",
            "tampered_field",
            "decision field binding mismatch",
        ),
        (
            "human_decisions",
            "decided_at",
            "2099-01-01 00:00:00.000000",
            "transition predates decision",
        ),
    ],
)
def test_trace_incomplete_after_any_tampered_binding(
    tmp_path: Path,
    table: str,
    column: str,
    value: object,
    expected_failure: str,
) -> None:
    """P0-2: every duplicated transition binding is re-verified from the DB."""
    from app.application.query_forms import QueryForms

    engine, repository, reviews, by_field = _two_field_env(tmp_path)
    _confirm_two_fields(reviews, by_field)
    if table == "fact_transitions":
        where = "field_key='total_quantity'"
    elif table == "candidate_certificates":
        where = f"certificate_id='{by_field['total_quantity'].certificate_id}'"
    else:
        where = (
            "decision_id=(SELECT decision_id FROM fact_transitions "
            "WHERE field_key='total_quantity')"
        )
    _tamper(
        tmp_path / "review.db",
        f"UPDATE {table} SET {column} = ? WHERE {where}",
        (value,),
    )
    trace = QueryForms(repository).trace("FORM-1")
    assert trace.status == "incomplete"
    all_failures = [failure for field in trace.fields for failure in field.failures]
    assert any(expected_failure in failure for failure in all_failures)


def test_trace_incomplete_when_one_transition_deleted(tmp_path) -> None:
    """P0-3: deleting one of two field transitions breaks version completeness."""
    from app.application.query_forms import QueryForms

    engine, repository, reviews, by_field = _two_field_env(tmp_path)
    _confirm_two_fields(reviews, by_field)
    _tamper(
        tmp_path / "review.db",
        "DELETE FROM fact_transitions WHERE field_key='total_quantity'",
    )
    trace = QueryForms(repository).trace("FORM-1")
    assert trace.status == "incomplete"
    missing = next(field for field in trace.fields if field.field_key == "total_quantity")
    assert missing.status == "incomplete"
    assert missing.failures == ("missing transition for field total_quantity",)


def test_trace_certificate_era_without_transitions_is_corruption(tmp_path) -> None:
    """P0-3: a new record with all transitions deleted is never pre-certificate."""
    from app.application.query_forms import QueryForms

    engine, repository, reviews, by_field = _two_field_env(tmp_path)
    _confirm_two_fields(reviews, by_field)
    _tamper(tmp_path / "review.db", "DELETE FROM fact_transitions")
    trace = QueryForms(repository).trace("FORM-1")
    assert trace.status == "incomplete"
    keys = {field.field_key for field in trace.fields}
    assert keys == {"total_quantity", "qualified_quantity"}
    assert all(field.status == "incomplete" for field in trace.fields)
    assert all("missing transition" in field.failures[0] for field in trace.fields)


def test_trace_incomplete_with_extra_transition(tmp_path) -> None:
    """P0-3: an extra transition field not present in the record values."""
    from app.application.query_forms import QueryForms

    engine, repository, reviews, by_field = _two_field_env(tmp_path)
    _confirm_two_fields(reviews, by_field)
    # Simulate storage corruption below the v5 constraint boundary.
    _tamper(
        tmp_path / "review.db",
        "DROP INDEX uq_fact_transitions_decision_id",
    )
    _tamper(
        tmp_path / "review.db",
        "DROP INDEX uq_fact_transitions_certificate_id",
    )
    _tamper(
        tmp_path / "review.db",
        "INSERT INTO fact_transitions (transition_id, form_id, created_version, "
        "field_key, record_id, record_version_id, decision_id, certificate_id, "
        "evidence_hash, evidence_locator, producer_id, producer_version, "
        "template_id, template_version, source_kind, created_at) "
        "SELECT 'T-EXTRA', form_id, created_version, 'extra_field', record_id, "
        "record_version_id, decision_id, certificate_id, evidence_hash, "
        "evidence_locator, producer_id, producer_version, template_id, "
        "template_version, source_kind, created_at "
        "FROM fact_transitions WHERE field_key='total_quantity'",
    )
    trace = QueryForms(repository).trace("FORM-1")
    assert trace.status == "incomplete"
    extra = next(field for field in trace.fields if field.field_key == "extra_field")
    assert "transition field not present in record values" in extra.failures


def test_trace_incomplete_after_field_rename(tmp_path) -> None:
    """P0-3: renaming a record value key breaks the exact field-set equality."""
    from app.application.query_forms import QueryForms

    engine, repository, reviews, by_field = _two_field_env(tmp_path)
    _confirm_two_fields(reviews, by_field)
    _tamper(
        tmp_path / "review.db",
        "UPDATE record_versions SET \"values\" = ? WHERE form_id='FORM-1' AND version=1",
        ('{"renamed_quantity": 7, "qualified_quantity": 5}',),
    )
    trace = QueryForms(repository).trace("FORM-1")
    assert trace.status == "incomplete"
    keys = {field.field_key for field in trace.fields}
    assert "renamed_quantity" in keys  # missing-transition entry
    assert "total_quantity" in keys  # extra-transition entry


def test_confirm_rejects_cross_form_manual_evidence(tmp_path) -> None:
    """P0-4: evidence owned by another form cannot confirm this form."""
    from app.application.review_forms import AuthorityRejectionError
    from app.domain.models import EvidenceFile, EvidenceType, Form, FormField

    engine, repository, reviews = _review_env(tmp_path)
    repository.add_form(Form(form_id="FORM-OTHER", template_id="T1", template_version="1"))
    repository.add_form_field(
        FormField(
            "FIELD-OTHER",
            "FORM-OTHER",
            "total_quantity",
            {"x": 0, "y": 0, "w": 8, "h": 8},
        )
    )
    repository.add_evidence(
        EvidenceFile(
            file_id="EVID-OTHER",
            form_id="FORM-OTHER",
            type=EvidenceType.ORIGINAL_IMAGE,
            uri="other",
            sha256="cd" * 32,
        )
    )
    with pytest.raises(AuthorityRejectionError) as exc_info:
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 7},
            "reviewer-1",
            "ok",
            certificate_ids_by_field={"total_quantity": None},
            manual_evidence_ids_by_field={"total_quantity": "EVID-OTHER"},
        )
    codes = {failure.code for failure in exc_info.value.failures}
    assert "EVIDENCE_FORM_MISMATCH" in codes
    _assert_no_writes(repository, "FORM-1")


def test_confirm_rejects_rebound_machine_evidence(tmp_path) -> None:
    """P0-4: a machine certificate rebound to another form's evidence rejects."""
    from app.application.review_forms import AuthorityRejectionError
    from app.domain.models import EvidenceFile, EvidenceType, Form, FormField

    engine, repository, reviews, by_field = _two_field_env(tmp_path)
    repository.add_form(Form(form_id="FORM-OTHER", template_id="T1", template_version="1"))
    repository.add_form_field(
        FormField(
            "FIELD-OTHER",
            "FORM-OTHER",
            "total_quantity",
            {"x": 0, "y": 0, "w": 8, "h": 8},
        )
    )
    repository.add_evidence(
        EvidenceFile(
            file_id="EVID-OTHER",
            form_id="FORM-OTHER",
            type=EvidenceType.ORIGINAL_IMAGE,
            uri="other",
            sha256="cd" * 32,
        )
    )
    certificate = by_field["total_quantity"]
    _tamper(
        tmp_path / "review.db",
        "UPDATE candidate_certificates SET evidence_file_id='EVID-OTHER' "
        f"WHERE certificate_id='{certificate.certificate_id}'",
    )
    with pytest.raises(AuthorityRejectionError) as exc_info:
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 7},
            "reviewer-1",
            "ok",
            certificate_ids_by_field={"total_quantity": certificate.certificate_id},
            manual_evidence_ids_by_field={},
        )
    codes = {failure.code for failure in exc_info.value.failures}
    assert "EVIDENCE_FORM_MISMATCH" in codes
    _assert_no_writes(repository, "FORM-1")


def test_confirm_rejects_tampered_evidence_row_hash(tmp_path) -> None:
    """P0-4: the persisted evidence row hash must equal the certificate hash."""
    from app.application.review_forms import AuthorityRejectionError

    engine, repository, reviews, by_field = _two_field_env(tmp_path)
    certificate = by_field["total_quantity"]
    evidence_file_id = repository.get_certificate_evidence_file_id(certificate.certificate_id)
    assert evidence_file_id is not None
    _tamper(
        tmp_path / "review.db",
        f"UPDATE evidence_files SET sha256 = ? WHERE file_id='{evidence_file_id}'",
        ("ff" * 32,),
    )
    with pytest.raises(AuthorityRejectionError) as exc_info:
        reviews.confirm(
            "FORM-1",
            0,
            {"total_quantity": 7},
            "reviewer-1",
            "ok",
            certificate_ids_by_field={"total_quantity": certificate.certificate_id},
            manual_evidence_ids_by_field={},
        )
    codes = {failure.code for failure in exc_info.value.failures}
    assert "EVIDENCE_HASH_MISMATCH" in codes
    _assert_no_writes(repository, "FORM-1")


def test_trace_incomplete_when_record_version_id_points_to_next_version(tmp_path) -> None:
    """P0-2 (second review): FK-valid rebind to the NEXT version's row."""
    from app.application.query_forms import QueryForms

    engine, repository, reviews = _review_env(tmp_path)
    first = reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
    )
    second = reviews.confirm(
        "FORM-1",
        1,
        {"total_quantity": 8},
        "reviewer-1",
        "correction",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
    )
    assert first.record_id != second.record_id
    # The target row exists (version 2), so this rebind is FK-valid.
    _tamper(
        tmp_path / "review.db",
        "UPDATE fact_transitions SET record_version_id = ? "
        "WHERE created_version=1 AND form_id='FORM-1'",
        (second.record_id,),
    )
    version_one = QueryForms(repository).trace("FORM-1", 1)
    assert version_one.status == "incomplete"
    assert any(
        "transition record-version row mismatch" in field.failures for field in version_one.fields
    )
    # A later trace validates the full prefix, so the historical corruption
    # taints version 2 even though its terminal transition is untouched.
    version_two = QueryForms(repository).trace("FORM-1", 2)
    assert version_two.status == "incomplete"
    assert "version 1 source record-version mismatch" in version_two.fields[0].failures


def test_trace_incomplete_when_record_version_id_points_to_other_form(tmp_path) -> None:
    """P0-2 (second review): rebind to another form's valid record row."""
    from app.application.query_forms import QueryForms
    from app.domain.models import EvidenceFile, EvidenceType, Form, FormField

    engine, repository, reviews = _review_env(tmp_path)
    repository.add_form(Form(form_id="FORM-OTHER", template_id="T1", template_version="1"))
    repository.add_form_field(
        FormField(
            "FIELD-OTHER",
            "FORM-OTHER",
            "total_quantity",
            {"x": 0, "y": 0, "w": 8, "h": 8},
        )
    )
    repository.add_evidence(
        EvidenceFile(
            file_id="EVID-OTHER",
            form_id="FORM-OTHER",
            type=EvidenceType.ORIGINAL_IMAGE,
            uri="other",
            sha256="cd" * 32,
        )
    )
    other = reviews.confirm(
        "FORM-OTHER",
        0,
        {"total_quantity": 3},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-OTHER"},
    )
    record = reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
    )
    assert record.record_id != other.record_id
    _tamper(
        tmp_path / "review.db",
        "UPDATE fact_transitions SET record_version_id = ? "
        "WHERE created_version=1 AND form_id='FORM-1'",
        (other.record_id,),
    )
    trace = QueryForms(repository).trace("FORM-1", 1)
    assert trace.status == "incomplete"
    assert any("transition record-version row mismatch" in field.failures for field in trace.fields)


def test_transition_record_version_id_matches_returned_record(tmp_path) -> None:
    """P0-2 (second review): positive FK persistence assertion."""
    _, repository, reviews = _review_env(tmp_path)
    record = reviews.confirm(
        "FORM-1",
        0,
        {"total_quantity": 7},
        "reviewer-1",
        "ok",
        certificate_ids_by_field={"total_quantity": None},
        manual_evidence_ids_by_field={"total_quantity": "EVID-1"},
    )
    transitions = repository.list_transitions_for_version("FORM-1", 1)
    assert len(transitions) == 1
    assert transitions[0].record_version_id == record.record_id
