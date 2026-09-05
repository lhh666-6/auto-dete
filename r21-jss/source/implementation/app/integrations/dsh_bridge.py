"""Versioned one-shot JSON bridge for the DeepSeek Harness plugin experiment."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine

from app.adapters.database.authority_facades import (
    AuthorityReadFacade,
    CandidateWriteFacade,
    FactAdmissionFacade,
)
from app.adapters.database.models import Base
from app.adapters.database.repositories import (
    SqlAlchemyFormRepository,
    install_sqlite_pragmas,
    stamp_schema_version,
)
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.ai_suggestion_forms import AISuggestionForms
from app.application.review_forms import ReviewForms
from app.domain.authority import CandidateCertificate
from app.domain.models import AuditEvent, EvidenceFile, EvidenceType, Form, FormField, utc_now

BRIDGE_VERSION = "auto-decte.dsh-bridge.v1"
MODEL_OPERATIONS = frozenset({"propose", "verify"})
HOST_OPERATIONS = frozenset(
    {"init-fixture", "host-confirm", "host-confirm-substitution", "export-receipt"}
)
DSH_PRODUCER = ("deepseek-harness", "dsh-v0.1.1-rc.2+b150a551b")


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _runtime(data_root: Path) -> tuple[SqlAlchemyFormRepository, LocalEvidenceStorage]:
    database_path = data_root / "database" / "demo.db"
    database_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{database_path}")
    install_sqlite_pragmas(engine)
    Base.metadata.create_all(engine)
    stamp_schema_version(engine)
    return SqlAlchemyFormRepository(engine), LocalEvidenceStorage(data_root / "evidence")


def _require_text(request: dict[str, Any], key: str) -> str:
    value = request.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _init_fixture(
    request: dict[str, Any], repository: SqlAlchemyFormRepository, storage: LocalEvidenceStorage
) -> dict[str, Any]:
    form_id = str(request.get("form_id", "FORM-DSH-1"))
    field_id = str(request.get("field_id", "FIELD-DSH-1"))
    field_key = str(request.get("field_key", "total_quantity"))
    existing = repository.get_form(form_id)
    if existing is not None:
        certificates = repository.list_certificates_for_field(form_id, field_key, 0)
        if len(certificates) == 1:
            field = repository.get_form_field(field_id)
            if field is None or field.form_id != form_id or field.field_name != field_key:
                raise ValueError("existing fixture field identity does not match request")
            return {
                "form_id": form_id,
                "field_id": field_id,
                "field_key": field_key,
                "parent_certificate_id": certificates[0].certificate_id,
                "fact_version": existing.current_record_version,
                "created": False,
            }
        if certificates:
            raise ValueError("existing fixture does not contain exactly one root certificate")
        if repository.get_form_field(field_id) is not None:
            raise ValueError("requested fixture field id already exists")

    now = utc_now()
    if existing is None:
        repository.add_form(Form(form_id, "DSH-TEMPLATE", "1", created_at=now))
    repository.add_form_field(
        FormField(field_id, form_id, field_key, {"x": 0, "y": 0, "w": 8, "h": 8})
    )
    stored = storage.store_bytes(b"AUTO-DECTE DSH fixture\n", ".txt", "fixture")
    evidence = EvidenceFile(
        file_id=stored.file_id,
        form_id=form_id,
        type=EvidenceType.ORIGINAL_IMAGE,
        uri=stored.uri,
        sha256=stored.sha256,
        related_field_id=field_id,
        created_at=now,
    )
    parent = CandidateCertificate.from_manual_entry(
        candidate_id=(
            "dsh-fixture-parent"
            if form_id == "FORM-DSH-1" and field_key == "total_quantity"
            else f"dsh-fixture-parent:{form_id}:{field_key}"
        ),
        field_key=field_key,
        value=request.get("initial_value", 7),
        form_id=form_id,
        evidence_hash=stored.sha256,
        evidence_locator=f"fixture://{form_id}/{field_key}",
        template_id="DSH-TEMPLATE",
        template_version="1",
        target_record_id=form_id,
        expected_fact_version=0,
        created_at=now,
    )
    audit = AuditEvent(
        event_id=(
            "EVENT-DSH-FIXTURE-1"
            if form_id == "FORM-DSH-1" and field_key == "total_quantity"
            else f"EVENT-DSH-FIXTURE:{form_id}:{field_key}"
        ),
        form_id=form_id,
        event_type="DSH_FIXTURE_INITIALIZED",
        actor_id="host-driver",
        after={"certificate_id": parent.certificate_id},
        evidence_ids=(stored.file_id,),
        timestamp=now,
    )
    try:
        repository.append_candidate_certificate(
            evidence=evidence, certificate=parent, audit=audit, field_id=field_id
        )
    except Exception:
        storage.discard(stored.uri)
        raise
    return {
        "form_id": form_id,
        "field_id": field_id,
        "field_key": field_key,
        "parent_certificate_id": parent.certificate_id,
        "fact_version": 0,
        "created": True,
    }


def _propose(
    request: dict[str, Any], repository: SqlAlchemyFormRepository, storage: LocalEvidenceStorage
) -> dict[str, Any]:
    service = AISuggestionForms(
        forms=repository,
        authority=AuthorityReadFacade(repository),
        candidate_writer=CandidateWriteFacade(repository),
        storage=storage,
    )
    result = service.propose(
        form_id=_require_text(request, "form_id"),
        field_id=_require_text(request, "field_id"),
        parent_certificate_id=_require_text(request, "parent_certificate_id"),
        value=request.get("value"),
        confidence=float(request.get("confidence", 0.0)),
        producer_id=DSH_PRODUCER[0],
        producer_version=DSH_PRODUCER[1],
        selection_artifact_id=_require_text(request, "execution_id"),
        session_id=_require_text(request, "session_id"),
        execution_id=_require_text(request, "execution_id"),
    )
    return {
        "candidate_id": result.candidate_id,
        "certificate_id": result.certificate_id,
        "evidence_file_id": result.evidence_file_id,
        "evidence_uri": result.evidence_uri,
        "expected_fact_version": result.expected_fact_version,
    }


def _verify(
    request: dict[str, Any], repository: SqlAlchemyFormRepository, data_root: Path
) -> dict[str, Any]:
    certificate_id = _require_text(request, "certificate_id")
    failures: list[str] = []
    certificate = repository.get_certificate(certificate_id)
    if certificate is None:
        return {"verified": False, "failures": ["UNKNOWN_CERTIFICATE"]}
    if not certificate.verify_content_address():
        failures.append("CERTIFICATE_CONTENT_ADDRESS_MISMATCH")
    evidence_id = repository.get_certificate_evidence_file_id(certificate_id)
    evidence = repository.get_evidence(evidence_id) if evidence_id else None
    if evidence is None:
        failures.append("EVIDENCE_BINDING_MISSING")
    else:
        evidence_path = data_root / "evidence" / evidence.uri
        if not evidence_path.is_file():
            failures.append("EVIDENCE_FILE_MISSING")
        elif _sha256_path(evidence_path) != evidence.sha256:
            failures.append("EVIDENCE_FILE_HASH_MISMATCH")
        if certificate.evidence_hash != evidence.sha256:
            failures.append("CERTIFICATE_EVIDENCE_HASH_MISMATCH")
    form = repository.get_form(certificate.target_record_id)
    return {
        "verified": not failures,
        "failures": failures,
        "certificate_id": certificate_id,
        "candidate_id": certificate.candidate_id,
        "form_id": certificate.target_record_id,
        "field_key": certificate.field_key,
        "value": certificate.value,
        "expected_fact_version": certificate.expected_fact_version,
        "current_fact_version": form.current_record_version if form else None,
    }


def _host_confirm(
    request: dict[str, Any], repository: SqlAlchemyFormRepository, data_root: Path
) -> dict[str, Any]:
    certificate_id = _require_text(request, "certificate_id")
    certificate = repository.get_certificate(certificate_id)
    if certificate is None:
        raise ValueError(f"unknown certificate: {certificate_id}")
    verification = _verify({"certificate_id": certificate_id}, repository, data_root)
    if not verification["verified"]:
        failures = ",".join(verification["failures"])
        raise ValueError(f"offline evidence verification failed: {failures}")
    actor_id = str(request.get("actor_id", "reviewer-1"))
    reviews = ReviewForms(
        repository,
        repository,
        authority_read=AuthorityReadFacade(repository),
        admission=FactAdmissionFacade(repository),
        known_producers=frozenset(
            {
                DSH_PRODUCER,
                ("human-reviewer", "manual-entry-v1"),
            }
        ),
        known_selection_artifacts=frozenset(
            {certificate.selection_artifact_id} if certificate.selection_artifact_id else set()
        ),
    )
    value = request.get("value", certificate.value)
    record = reviews.confirm(
        certificate.target_record_id,
        int(request.get("expected_version", certificate.expected_fact_version)),
        {certificate.field_key: value},
        actor_id,
        str(request.get("reason", "host-side DSH integration decision")),
        certificate_ids_by_field={certificate.field_key: certificate_id},
        manual_evidence_ids_by_field={},
    )
    return {
        "record_id": record.record_id,
        "form_id": record.form_id,
        "fact_version": record.version,
        "status": record.status.value,
        "values": record.values,
        "confirmed_by": record.confirmed_by,
    }


def _host_confirm_substitution(
    request: dict[str, Any], repository: SqlAlchemyFormRepository, data_root: Path
) -> dict[str, Any]:
    """Attempt host admission of a certificate in an explicitly supplied context.

    This host-only probe exists for the live-agent cross-record/cross-field
    experiment.  It never expands the two-tool model surface.
    """
    certificate_id = _require_text(request, "certificate_id")
    certificate = repository.get_certificate(certificate_id)
    if certificate is None:
        raise ValueError(f"unknown certificate: {certificate_id}")
    verification = _verify({"certificate_id": certificate_id}, repository, data_root)
    if not verification["verified"]:
        failures = ",".join(verification["failures"])
        raise ValueError(f"offline evidence verification failed: {failures}")
    target_form_id = _require_text(request, "target_form_id")
    target_field_key = _require_text(request, "target_field_key")
    reviews = ReviewForms(
        repository,
        repository,
        authority_read=AuthorityReadFacade(repository),
        admission=FactAdmissionFacade(repository),
        known_producers=frozenset(
            {DSH_PRODUCER, ("human-reviewer", "manual-entry-v1")}
        ),
        known_selection_artifacts=frozenset(
            {certificate.selection_artifact_id} if certificate.selection_artifact_id else set()
        ),
    )
    record = reviews.confirm(
        target_form_id,
        int(request.get("expected_version", 0)),
        {target_field_key: request.get("value", certificate.value)},
        str(request.get("actor_id", "reviewer-1")),
        str(request.get("reason", "host-side substitution rejection probe")),
        certificate_ids_by_field={target_field_key: certificate_id},
        manual_evidence_ids_by_field={},
    )
    return {
        "record_id": record.record_id,
        "form_id": record.form_id,
        "fact_version": record.version,
        "status": record.status.value,
    }


def _export_receipt(repository: SqlAlchemyFormRepository, data_root: Path) -> dict[str, Any]:
    database_path = data_root / "database" / "demo.db"
    forms = []
    # The deterministic experiment owns one fixture form.
    form = repository.get_form("FORM-DSH-1")
    if form is not None:
        forms.append(
            {
                "form_id": form.form_id,
                "current_record_version": form.current_record_version,
                "records": [
                    {
                        "record_id": record.record_id,
                        "version": record.version,
                        "status": record.status.value,
                        "values": record.values,
                    }
                    for record in repository.list_record_versions(form.form_id)
                ],
                "certificates": [
                    {
                        "certificate_id": certificate.certificate_id,
                        "candidate_id": certificate.candidate_id,
                        "source_kind": certificate.source_kind.value,
                        "parent_ids": list(certificate.lineage_parent_ids),
                        "expected_fact_version": certificate.expected_fact_version,
                    }
                    for certificate in repository.list_certificates_for_form(form.form_id)
                ],
            }
        )
    authority_state_sha256 = hashlib.sha256(
        json.dumps(forms, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "forms": forms,
        "authority_state_sha256": authority_state_sha256,
        "database_path": str(database_path),
        "database_sha256": _sha256_path(database_path),
    }


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("bridge_version") != BRIDGE_VERSION:
        raise ValueError(f"bridge_version must equal {BRIDGE_VERSION}")
    surface = _require_text(request, "surface")
    operation = _require_text(request, "operation")
    allowed = (
        MODEL_OPERATIONS
        if surface == "model"
        else HOST_OPERATIONS
        if surface == "host"
        else ()
    )
    if operation not in allowed:
        raise PermissionError(f"operation {operation!r} is not exposed on the {surface!r} surface")
    data_root = Path(_require_text(request, "data_root")).resolve()
    repository, storage = _runtime(data_root)
    if operation == "init-fixture":
        result = _init_fixture(request, repository, storage)
    elif operation == "propose":
        result = _propose(request, repository, storage)
    elif operation == "verify":
        result = _verify(request, repository, data_root)
    elif operation == "host-confirm":
        result = _host_confirm(request, repository, data_root)
    elif operation == "host-confirm-substitution":
        result = _host_confirm_substitution(request, repository, data_root)
    elif operation == "export-receipt":
        result = _export_receipt(repository, data_root)
    else:  # pragma: no cover - allow-list above is exhaustive
        raise AssertionError(operation)
    return {"ok": True, "bridge_version": BRIDGE_VERSION, "operation": operation, "result": result}


def main() -> int:
    try:
        raw = sys.stdin.buffer.read()
        if not raw:
            raise ValueError("stdin request is empty")
        request = json.loads(raw)
        if not isinstance(request, dict):
            raise ValueError("request must be a JSON object")
        response = handle_request(request)
    except Exception as error:
        response = {
            "ok": False,
            "bridge_version": BRIDGE_VERSION,
            "error": {"type": type(error).__name__, "message": str(error)},
        }
        sys.stdout.write(json.dumps(response, sort_keys=True, separators=(",", ":")))
        return 1
    sys.stdout.write(json.dumps(response, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
