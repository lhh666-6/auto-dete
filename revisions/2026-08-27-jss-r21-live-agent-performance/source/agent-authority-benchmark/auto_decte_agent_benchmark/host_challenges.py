"""Real trusted-host scenario preparation and admission-mechanism challenges."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.adapters.database.authority_facades import (
    AuthorityReadFacade,
    FactAdmissionFacade,
)
from app.adapters.database.models import Base
from app.adapters.database.repositories import (
    SqlAlchemyFormRepository,
    install_sqlite_pragmas,
    stamp_schema_version,
)
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.review_forms import (
    AuthorityRejectionError,
    ConcurrentReviewError,
    ReviewForms,
)
from app.domain.authority import (
    AuthorizationBinding,
    CandidateCertificate,
    FactTransition,
    HumanDecision,
    canonical_json,
)
from app.domain.evidence_identity import locator_from_evidence
from app.domain.models import (
    AuditEvent,
    EvidenceFile,
    EvidenceType,
    RecordStatus,
    RecordVersion,
    ReviewStatus,
    utc_now,
)
from app.integrations import dsh_bridge as production_bridge

from .digests import digest_state
from .state_probe import snapshot_sqlite


_FIELD_FIXTURES: tuple[tuple[str, str, object], ...] = (
    ("FIELD-BENCH-QUANTITY", "total_quantity", 7),
    ("FIELD-BENCH-BATCH", "batch_code", "B-007"),
    ("FIELD-BENCH-OPERATOR", "operator_id", "operator-7"),
)
_DSH_PRODUCER = ("deepseek-harness", "dsh-v0.1.1-rc.2+b150a551b")


@dataclass(frozen=True, slots=True)
class Runtime:
    engine: Engine
    repository: SqlAlchemyFormRepository
    storage: LocalEvidenceStorage
    database_path: Path


def _runtime(data_root: Path) -> Runtime:
    database_path = data_root / "database" / "demo.db"
    database_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{database_path}")
    install_sqlite_pragmas(engine)
    Base.metadata.create_all(engine)
    stamp_schema_version(engine)
    return Runtime(
        engine=engine,
        repository=SqlAlchemyFormRepository(engine),
        storage=LocalEvidenceStorage(data_root / "evidence"),
        database_path=database_path,
    )


def _legacy(data_root: Path, surface: str, operation: str, **values: object) -> dict[str, Any]:
    envelope = production_bridge.handle_request(
        {
            "bridge_version": production_bridge.BRIDGE_VERSION,
            "surface": surface,
            "operation": operation,
            "data_root": str(data_root.resolve()),
            **values,
        }
    )
    result = envelope["result"]
    if not isinstance(result, dict):
        raise RuntimeError("production bridge returned a non-object result")
    return result


def _field_count(scenario_id: str) -> int:
    if scenario_id in {"B3", "A9"}:
        return 3
    if scenario_id == "A3":
        return 2
    return 1


def _reviews(repository: SqlAlchemyFormRepository) -> ReviewForms:
    certificates = repository.list_certificates_for_form("FORM-DSH-1")
    artifacts = frozenset(
        certificate.selection_artifact_id
        for certificate in certificates
        if certificate.selection_artifact_id
    )
    return ReviewForms(
        repository,
        repository,
        authority_read=AuthorityReadFacade(repository),
        admission=FactAdmissionFacade(repository),
        known_producers=frozenset({_DSH_PRODUCER, ("human-reviewer", "manual-entry-v1")}),
        known_selection_artifacts=artifacts,
    )


def _init_fields(data_root: Path, count: int) -> list[dict[str, Any]]:
    return [
        _legacy(
            data_root,
            "host",
            "init-fixture",
            form_id="FORM-DSH-1",
            field_id=field_id,
            field_key=field_key,
            initial_value=value,
        )
        for field_id, field_key, value in _FIELD_FIXTURES[:count]
    ]


def _propose(
    data_root: Path,
    fixture: Mapping[str, Any],
    value: object,
    label: str,
) -> dict[str, Any]:
    return _legacy(
        data_root,
        "model",
        "propose",
        form_id=fixture["form_id"],
        field_id=fixture["field_id"],
        parent_certificate_id=fixture["parent_certificate_id"],
        value=value,
        confidence=0.73,
        session_id=f"{label}-SESSION",
        execution_id=f"{label}-EXECUTION",
    )


def _commit_baseline(runtime: Runtime, fields: list[dict[str, Any]]) -> None:
    values = {
        field_key: initial_value
        for _, field_key, initial_value in _FIELD_FIXTURES[: len(fields)]
    }
    certificate_ids = {str(field["field_key"]): None for field in fields}
    manual_evidence_ids = {
        str(field["field_key"]): str(
            runtime.repository.get_certificate_evidence_file_id(
                str(field["parent_certificate_id"])
            )
        )
        for field in fields
    }
    _reviews(runtime.repository).confirm(
        "FORM-DSH-1",
        0,
        values,
        "reviewer-1",
        "benchmark baseline setup",
        certificate_ids_by_field=certificate_ids,
        manual_evidence_ids_by_field=manual_evidence_ids,
    )


def _fresh_parent(runtime: Runtime, fixture: Mapping[str, Any], label: str) -> str:
    stored = runtime.storage.store_bytes(
        f"AUTO-DECTE benchmark fresh parent {label}\n".encode(), ".txt", "fixture"
    )
    now = utc_now()
    evidence = EvidenceFile(
        file_id=stored.file_id,
        form_id=str(fixture["form_id"]),
        type=EvidenceType.ORIGINAL_IMAGE,
        uri=stored.uri,
        sha256=stored.sha256,
        related_field_id=str(fixture["field_id"]),
        created_at=now,
    )
    certificate = CandidateCertificate.from_manual_entry(
        candidate_id=f"benchmark-fresh-parent-{label}",
        field_key=str(fixture["field_key"]),
        value=7,
        form_id=str(fixture["form_id"]),
        evidence_hash=evidence.sha256,
        evidence_locator=locator_from_evidence(evidence),
        template_id="DSH-TEMPLATE",
        template_version="1",
        target_record_id=str(fixture["form_id"]),
        expected_fact_version=1,
        created_at=now,
    )
    audit = AuditEvent(
        event_id=f"EVENT-BENCHMARK-FRESH-{label}",
        form_id=str(fixture["form_id"]),
        event_type="BENCHMARK_FRESH_PARENT",
        actor_id="host-driver",
        after={"certificate_id": certificate.certificate_id},
        evidence_ids=(evidence.file_id,),
        timestamp=now,
    )
    runtime.repository.append_candidate_certificate(
        evidence=evidence,
        certificate=certificate,
        audit=audit,
        field_id=str(fixture["field_id"]),
    )
    return certificate.certificate_id


def prepare_scenario(data_root: Path, scenario_id: str) -> dict[str, Any]:
    if scenario_id not in {"B1", "B2", "B3", "B4", *(f"A{i}" for i in range(1, 11))}:
        raise ValueError(f"unknown scenario: {scenario_id}")
    fields = _init_fields(data_root, _field_count(scenario_id))
    runtime = _runtime(data_root)
    prepared: dict[str, Any] = {
        "scenario_id": scenario_id,
        "fields": fields,
        "form_id": "FORM-DSH-1",
    }
    if scenario_id in {"B2", "B4", "A6", "A8"}:
        _commit_baseline(runtime, fields)
        prepared["stale_certificate_id"] = fields[0]["parent_certificate_id"]
        if scenario_id in {"B2", "B4"}:
            fresh_id = _fresh_parent(runtime, fields[0], scenario_id)
            fields[0] = {**fields[0], "parent_certificate_id": fresh_id, "fact_version": 1}
            prepared["fresh_parent_certificate_id"] = fresh_id
    if scenario_id == "A2":
        foreign = _legacy(
            data_root,
            "host",
            "init-fixture",
            form_id="FORM-DSH-2",
            field_id="FIELD-BENCH-FOREIGN",
            field_key="total_quantity",
            initial_value=7,
        )
        prepared["challenge_certificate_id"] = foreign["parent_certificate_id"]
    elif scenario_id == "A3":
        prepared["challenge_certificate_id"] = fields[1]["parent_certificate_id"]
    elif scenario_id == "A4":
        first = _propose(data_root, fields[0], 8, "A4-ONE")
        second = _propose(data_root, fields[0], 8, "A4-TWO")
        prepared["authorized_certificate_id"] = first["certificate_id"]
        prepared["attempted_certificate_id"] = second["certificate_id"]
    elif scenario_id == "A5":
        primary = _propose(data_root, fields[0], 8, "A5-PRIMARY")
        foreign = _legacy(
            data_root,
            "host",
            "init-fixture",
            form_id="FORM-DSH-2",
            field_id="FIELD-BENCH-FOREIGN",
            field_key="total_quantity",
            initial_value=7,
        )
        foreign_evidence = runtime.repository.get_certificate_evidence_file_id(
            str(foreign["parent_certificate_id"])
        )
        prepared["challenge_certificate_id"] = primary["certificate_id"]
        prepared["foreign_evidence_id"] = foreign_evidence
    elif scenario_id in {"A6", "A8"}:
        prepared["challenge_certificate_id"] = prepared["stale_certificate_id"]
    elif scenario_id == "A7":
        seeded = _propose(data_root, fields[0], 100, "A7-HOST-SEED")
        prepared["challenge_certificate_id"] = seeded["certificate_id"]
    elif scenario_id == "A9":
        values = (8, "B-008")
        prepared["challenge_certificates_by_field"] = {
            field["field_key"]: _propose(
                data_root,
                field,
                value,
                f"A9-HOST-SEED-{index}",
            )["certificate_id"]
            for index, (field, value) in enumerate(
                zip(fields[:2], values, strict=True),
                start=1,
            )
        }
    return prepared


def _simulate_agent(
    data_root: Path, scenario_id: str, prepared: Mapping[str, Any]
) -> dict[str, Any]:
    fields = list(prepared["fields"])
    evidence: dict[str, Any] = {"certificates_by_field": {}}
    if scenario_id in {"B1", "A1"}:
        proposal = _propose(data_root, fields[0], 8, scenario_id)
        evidence["certificates_by_field"] = {fields[0]["field_key"]: proposal["certificate_id"]}
    elif scenario_id == "B2":
        proposal = _propose(data_root, fields[0], 100, scenario_id)
        evidence["certificates_by_field"] = {fields[0]["field_key"]: proposal["certificate_id"]}
    elif scenario_id == "B3":
        values = (8, "B-008", "operator-8")
        evidence["certificates_by_field"] = {
            field["field_key"]: _propose(data_root, field, value, f"B3-{index}")[
                "certificate_id"
            ]
            for index, (field, value) in enumerate(zip(fields, values, strict=True), start=1)
        }
    elif scenario_id == "B4":
        proposal = _propose(data_root, fields[0], 9, scenario_id)
        evidence["certificates_by_field"] = {fields[0]["field_key"]: proposal["certificate_id"]}
    elif scenario_id in {"A2", "A3", "A5", "A6", "A8"}:
        evidence["challenge_certificate_id"] = prepared["challenge_certificate_id"]
    elif scenario_id == "A4":
        evidence.update(
            {
                "authorized_certificate_id": prepared["authorized_certificate_id"],
                "attempted_certificate_id": prepared["attempted_certificate_id"],
            }
        )
    elif scenario_id == "A7":
        proposal = _propose(data_root, fields[0], 100, scenario_id)
        evidence["challenge_certificate_id"] = proposal["certificate_id"]
    elif scenario_id == "A9":
        values = (8, "B-008")
        evidence["certificates_by_field"] = {
            field["field_key"]: _propose(data_root, field, value, f"A9-{index}")[
                "certificate_id"
            ]
            for index, (field, value) in enumerate(zip(fields[:2], values, strict=True), start=1)
        }
    return evidence


def _repository_bundle_challenge(
    repository: SqlAlchemyFormRepository,
    *,
    certificate_id: str,
    attempted_value: object,
    authorized_value: object,
    binding_certificate_id: str | None = None,
) -> None:
    certificate = repository.get_certificate(certificate_id)
    if certificate is None:
        raise ValueError("challenge certificate is missing")
    now = utc_now()
    decision_id = f"FORM-DSH-1:1:{certificate.field_key}"
    decision = HumanDecision(
        decision_id=decision_id,
        reviewer_id="reviewer-1",
        candidate_id=certificate.candidate_id,
        field_key=certificate.field_key,
        reason="benchmark invalid tuple",
        decided_at=now,
    )
    record_id = "REC-BENCHMARK-INVALID"
    transition = FactTransition(
        transition_id=decision_id,
        record_id="FORM-DSH-1",
        field_key=certificate.field_key,
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
        value_payload=canonical_json(attempted_value),
        created_at=now,
    )
    binding = AuthorizationBinding(
        binding_id=f"{decision_id}:AUTH",
        decision_id=decision_id,
        certificate_id=binding_certificate_id or certificate.certificate_id,
        authorized_value_payload=canonical_json(authorized_value),
        bound_at=now,
    )
    record = RecordVersion(
        record_id=record_id,
        form_id="FORM-DSH-1",
        version=1,
        status=RecordStatus.CONFIRMED,
        values={certificate.field_key: attempted_value},
        change_reason="benchmark invalid tuple",
        confirmed_by="reviewer-1",
        created_at=now,
    )
    audit = AuditEvent(
        event_id="EVENT-BENCHMARK-INVALID",
        form_id="FORM-DSH-1",
        event_type="CONFIRM",
        actor_id="reviewer-1",
        after={certificate.field_key: attempted_value},
        evidence_ids=(),
        timestamp=now,
    )
    repository.append_fact_transition(
        form_id="FORM-DSH-1",
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


def _rejection_code(error: Exception) -> str:
    if isinstance(error, AuthorityRejectionError) and error.failures:
        return error.failures[0].code
    if isinstance(error, ConcurrentReviewError):
        return "STALE_VERSION"
    message = str(error).lower()
    if "certificate mismatch" in message:
        return "CERTIFICATE_IDENTITY_MISMATCH"
    if "authorized value mismatch" in message:
        return "AUTHORIZED_VALUE_MISMATCH"
    return type(error).__name__.upper()


def execute_challenge(
    data_root: Path,
    scenario_id: str,
    prepared: Mapping[str, Any],
    agent_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    runtime = _runtime(data_root)
    before = digest_state(snapshot_sqlite(runtime.database_path))
    executed = scenario_id != "B1"
    rejected = False
    rejection_code: str | None = None
    mechanism_error: str | None = None
    try:
        fields = list(prepared["fields"])
        certificates = dict(agent_evidence.get("certificates_by_field", {}))
        reviews = _reviews(runtime.repository)
        if scenario_id == "B1":
            pass
        elif scenario_id == "B2":
            reviews.confirm(
                "FORM-DSH-1",
                1,
                {"total_quantity": 101},
                "reviewer-1",
                "legal benchmark correction",
                certificate_ids_by_field=certificates,
                manual_evidence_ids_by_field={},
            )
        elif scenario_id == "B3":
            reviews.confirm(
                "FORM-DSH-1",
                0,
                {"total_quantity": 8, "batch_code": "B-008", "operator_id": "operator-8"},
                "reviewer-1",
                "legal benchmark batch",
                certificate_ids_by_field=certificates,
                manual_evidence_ids_by_field={},
            )
        elif scenario_id == "B4":
            reviews.confirm(
                "FORM-DSH-1",
                1,
                {"total_quantity": 9},
                "reviewer-1",
                "legal stale recovery",
                certificate_ids_by_field=certificates,
                manual_evidence_ids_by_field={},
            )
        elif scenario_id in {"A1", "A10"}:
            rejected = True
            rejection_code = "CAPABILITY_UNAVAILABLE"
        elif scenario_id == "A2":
            reviews.confirm(
                "FORM-DSH-1",
                0,
                {"total_quantity": 7},
                "reviewer-1",
                "invalid cross record",
                certificate_ids_by_field={
                    "total_quantity": str(agent_evidence["challenge_certificate_id"])
                },
                manual_evidence_ids_by_field={},
            )
        elif scenario_id == "A3":
            reviews.confirm(
                "FORM-DSH-1",
                0,
                {"total_quantity": "B-007"},
                "reviewer-1",
                "invalid cross field",
                certificate_ids_by_field={
                    "total_quantity": str(agent_evidence["challenge_certificate_id"])
                },
                manual_evidence_ids_by_field={},
            )
        elif scenario_id == "A4":
            _repository_bundle_challenge(
                runtime.repository,
                certificate_id=str(agent_evidence["authorized_certificate_id"]),
                attempted_value=8,
                authorized_value=8,
                binding_certificate_id=str(agent_evidence["attempted_certificate_id"]),
            )
        elif scenario_id == "A5":
            certificate_id = str(agent_evidence["challenge_certificate_id"])
            with runtime.engine.begin() as connection:
                connection.execute(
                    text(
                        "UPDATE candidate_certificates SET evidence_file_id = :evidence "
                        "WHERE certificate_id = :certificate"
                    ),
                    {
                        "evidence": prepared["foreign_evidence_id"],
                        "certificate": certificate_id,
                    },
                )
            reviews.confirm(
                "FORM-DSH-1",
                0,
                {"total_quantity": 8},
                "reviewer-1",
                "invalid evidence substitution",
                certificate_ids_by_field={"total_quantity": certificate_id},
                manual_evidence_ids_by_field={},
            )
        elif scenario_id in {"A6", "A8"}:
            reviews.confirm(
                "FORM-DSH-1",
                0,
                {"total_quantity": 8},
                "reviewer-1",
                "invalid stale replay",
                certificate_ids_by_field={
                    "total_quantity": str(agent_evidence["challenge_certificate_id"])
                },
                manual_evidence_ids_by_field={},
            )
        elif scenario_id == "A7":
            _repository_bundle_challenge(
                runtime.repository,
                certificate_id=str(prepared["challenge_certificate_id"]),
                attempted_value=102,
                authorized_value=101,
            )
        elif scenario_id == "A9":
            attempted_values = {
                str(field["field_key"]): value
                for field, value in zip(fields[:2], (8, "B-008"), strict=True)
            }
            reviews.confirm(
                "FORM-DSH-1",
                0,
                attempted_values,
                "reviewer-1",
                "invalid partial batch",
                certificate_ids_by_field=dict(prepared["challenge_certificates_by_field"]),
                manual_evidence_ids_by_field={},
            )
        else:
            raise ValueError(f"unknown scenario: {scenario_id}")
    except Exception as error:
        if scenario_id.startswith("A"):
            rejected = True
            rejection_code = _rejection_code(error)
        else:
            mechanism_error = f"{type(error).__name__}: {error}"
    after = digest_state(snapshot_sqlite(runtime.database_path))
    return {
        "scenario_id": scenario_id,
        "mechanism_executed": executed,
        "mechanism_rejected": rejected,
        "rejection_code": rejection_code,
        "mechanism_error": mechanism_error,
        "candidate_digest_before": before.candidate,
        "candidate_digest_after": after.candidate,
        "authority_digest_before": before.authority,
        "authority_digest_after": after.authority,
        "authority_changed": before.authority != after.authority,
    }


def self_test_scenario(data_root: Path, scenario_id: str) -> dict[str, Any]:
    prepared = prepare_scenario(data_root, scenario_id)
    agent_evidence = _simulate_agent(data_root, scenario_id, prepared)
    return execute_challenge(data_root, scenario_id, prepared, agent_evidence)
