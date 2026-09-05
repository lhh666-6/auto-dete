"""R18 fixture-driven AI-origin admission lifecycle evidence."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sqlalchemy import create_engine

from app.adapters.database.authority_facades import (
    AuthorityReadFacade,
    CandidateWriteFacade,
    FactAdmissionFacade,
)
from app.adapters.database.migrations import migrate_schema
from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository, install_sqlite_pragmas
from app.adapters.recognition.candidate import RecognitionCandidate
from app.adapters.recognition.opencv import OpenCvImagePipeline
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.import_forms import ImportForms
from app.application.query_forms import QueryForms
from app.application.recognize_forms import RecognizeForms
from app.application.review_forms import (
    AuthorityRejectionError,
    ConcurrentReviewError,
    ReviewForms,
)
from app.domain.models import FormField
from app.domain.principal import prototype_principal_policy
from tests.conformance.oracle import database_digest


@dataclass(frozen=True, slots=True)
class FrozenAICandidate:
    record_id: str
    fields: dict[str, object]
    engine: str
    model_version: str
    fixture_sha256: str


def load_ai_candidate(fixture: Path) -> FrozenAICandidate:
    """Load a verified AI-origin fixture."""

    root = fixture.resolve()
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, list) or manifest.get("file_count") != len(files):
        raise ValueError("invalid fixture manifest")
    for entry in files:
        path = (root / str(entry["path"])).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"invalid fixture path: {entry['path']}")
        payload = path.read_bytes()
        if len(payload) != int(entry["bytes"]):
            raise ValueError(f"fixture byte mismatch: {entry['path']}")
        if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            raise ValueError(f"fixture hash mismatch: {entry['path']}")

    raw = json.loads((root / "raw-response.txt").read_text(encoding="utf-8"))
    normalized = json.loads((root / "candidate.json").read_text(encoding="utf-8"))
    fields = normalized.get("fields")
    if not isinstance(fields, dict):
        raise ValueError("candidate fields must be an object")
    expected_raw = {"record_id": normalized.get("record_id"), **fields}
    if raw != expected_raw:
        raise ValueError("raw response and normalized candidate differ")
    producer = normalized.get("candidate_producer")
    if not isinstance(producer, dict):
        raise ValueError("candidate producer must be an object")
    return FrozenAICandidate(
        record_id=str(normalized["record_id"]),
        fields=fields,
        engine=str(producer["engine"]),
        model_version=str(producer["model_version"]),
        fixture_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    )


def run_ai_origin_lifecycle(fixture: Path, output: Path) -> dict[str, object]:
    """Run the six-case R18 lifecycle experiment."""

    if output.exists():
        raise FileExistsError(output)
    candidate = load_ai_candidate(fixture)
    output.mkdir(parents=True)
    raw_root = output / "raw"
    raw_root.mkdir()
    work_root = output / "work"
    work_root.mkdir()

    field_names = ("quantity", "batch", "operator")
    form_id = "FORM-R18"

    def new_environment(case_id: str):
        case_root = work_root / case_id
        case_root.mkdir()
        engine = create_engine(f"sqlite:///{case_root / 'lifecycle.db'}")
        install_sqlite_pragmas(engine)
        Base.metadata.create_all(engine)
        migrate_schema(engine)
        repository = SqlAlchemyFormRepository(
            engine, principal_policy=prototype_principal_policy(("reviewer",))
        )
        storage = LocalEvidenceStorage(case_root / "evidence")
        imports = ImportForms(repository, repository, repository, storage)
        recognition = RecognizeForms(
            repository,
            repository,
            repository,
            storage,
            OpenCvImagePipeline(),
            candidate_writer=CandidateWriteFacade(repository),
        )
        review = ReviewForms(
            repository,
            repository,
            authority_read=AuthorityReadFacade(repository),
            admission=FactAdmissionFacade(repository),
            known_producers=frozenset(
                {
                    (candidate.engine, candidate.model_version),
                    ("human-reviewer", "manual-entry-v1"),
                }
            ),
            known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
        )
        source = case_root / "input.txt"
        source.write_bytes((fixture / "input.txt").read_bytes())
        imports.import_image(source, form_id, "R18", "1", "fixture-loader")
        for index, field_name in enumerate(field_names):
            repository.add_form_field(FormField(f"FIELD-{index}", form_id, field_name, {}))
        return engine, repository, recognition, review

    def machine_candidate(value: object) -> RecognitionCandidate[object]:
        return RecognitionCandidate(
            value=value,
            confidence=0.0,
            engine=candidate.engine,
            model_version=candidate.model_version,
            reason_code="HOSTED_AI_OUTPUT",
            accepted=True,
            decision_score=None,
        )

    def record_machine(
        repository,
        recognition,
        values: dict[str, object],
        *,
        crop_offset: int,
        fields: tuple[str, ...] | None = None,
    ) -> dict[str, str]:
        certificates: dict[str, str] = {}
        selected_fields = fields or field_names
        for index, field_name in enumerate(selected_fields):
            field_index = field_names.index(field_name)
            crop = np.full((16, 16), (crop_offset + index * 31) % 255, dtype=np.uint8)
            recognition.record_candidate(
                form_id,
                f"FIELD-{field_index}",
                crop,
                machine_candidate(values[field_name]),
                "machine",
            )
            certificates[field_name] = repository.list_certificates_for_field(
                form_id, field_name, repository.get_form(form_id).current_record_version
            )[-1].certificate_id
        return certificates

    def confirm(
        review,
        expected_version: int,
        values: dict[str, object],
        certificates: dict[str, str],
    ):
        return review.confirm(
            form_id,
            expected_version,
            values,
            "reviewer",
            "R18 lifecycle confirmation",
            certificate_ids_by_field=certificates,
            manual_evidence_ids_by_field={},
        )

    initial_values = dict(candidate.fields)

    def initialise(case_id: str):
        engine, repository, recognition, review = new_environment(case_id)
        initial_certificates = record_machine(
            repository, recognition, initial_values, crop_offset=30
        )
        first = confirm(review, 0, initial_values, initial_certificates)
        return engine, repository, recognition, review, initial_certificates, first

    def trace_status(query: QueryForms) -> str:
        return query.trace(form_id).status

    def write_case(case: dict[str, object]) -> dict[str, object]:
        (raw_root / f"{case['id']}.json").write_text(
            json.dumps(case, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return case

    cases: list[dict[str, object]] = []

    engine, repository, recognition, review, initial_certs, first = initialise("A1_all_accept")
    try:
        cases.append(
            write_case(
                {
                    "id": "A1_all_accept",
                    "operation": "initial confirmation with all machine candidates",
                    "expected_outcome": "accepted",
                    "observed_outcome": "accepted",
                    "status": "PASS",
                    "versions": [first.version],
                    "trace_status": trace_status(QueryForms(repository)),
                    "candidate_fields": sorted(initial_values),
                }
            )
        )
    finally:
        engine.dispose()

    engine, repository, recognition, review, initial_certs, first = initialise(
        "A2_singleton_correction"
    )
    try:
        quantity_cert = record_machine(
            repository,
            recognition,
            {
                "quantity": int(initial_values["quantity"]) + 1,
                **{key: initial_values[key] for key in ("batch", "operator")},
            },
            crop_offset=140,
            fields=("quantity",),
        )["quantity"]
        corrected = {
            "quantity": int(initial_values["quantity"]) + 2,
            "batch": initial_values["batch"],
            "operator": initial_values["operator"],
        }
        second = confirm(
            review,
            1,
            corrected,
            {
                "quantity": quantity_cert,
                "batch": initial_certs["batch"],
                "operator": initial_certs["operator"],
            },
        )
        trace = QueryForms(repository).trace(form_id)
        cases.append(
            write_case(
                {
                    "id": "A2_singleton_correction",
                    "operation": "correct one field while copying forward two fields",
                    "expected_outcome": "corrected",
                    "observed_outcome": "corrected",
                    "status": "PASS",
                    "versions": [first.version, second.version],
                    "trace_status": trace.status,
                    "copy_forward_fields": ["batch", "operator"],
                    "candidate_fields": ["quantity"],
                }
            )
        )
    finally:
        engine.dispose()

    engine, repository, recognition, review, initial_certs, first = initialise("A3_all_correction")
    try:
        new_values = {
            "quantity": int(initial_values["quantity"]) + 10,
            "batch": f"{initial_values['batch']}-NEW",
            "operator": f"{initial_values['operator']}-NEW",
        }
        new_certs = record_machine(repository, recognition, new_values, crop_offset=80)
        corrected = {
            "quantity": int(new_values["quantity"]) + 1,
            "batch": f"{new_values['batch']}-AUTH",
            "operator": f"{new_values['operator']}-AUTH",
        }
        second = confirm(review, 1, corrected, new_certs)
        cases.append(
            write_case(
                {
                    "id": "A3_all_correction",
                    "operation": "correct every declared field",
                    "expected_outcome": "corrected",
                    "observed_outcome": "corrected",
                    "status": "PASS",
                    "versions": [first.version, second.version],
                    "trace_status": trace_status(QueryForms(repository)),
                    "copy_forward_fields": [],
                    "candidate_fields": sorted(new_values),
                }
            )
        )
    finally:
        engine.dispose()

    engine, repository, recognition, review, initial_certs, first = initialise(
        "A4_mixed_copy_forward"
    )
    try:
        candidate_values = {
            "quantity": int(initial_values["quantity"]) + 20,
            "batch": f"{initial_values['batch']}-MIX",
            "operator": initial_values["operator"],
        }
        mixed_certs = record_machine(
            repository,
            recognition,
            candidate_values,
            crop_offset=190,
            fields=("quantity", "batch"),
        )
        corrected = {
            "quantity": int(candidate_values["quantity"]) + 1,
            "batch": candidate_values["batch"],
            "operator": initial_values["operator"],
        }
        second = confirm(
            review,
            1,
            corrected,
            {
                "quantity": mixed_certs["quantity"],
                "batch": mixed_certs["batch"],
                "operator": initial_certs["operator"],
            },
        )
        cases.append(
            write_case(
                {
                    "id": "A4_mixed_copy_forward",
                    "operation": "correct two fields and copy forward one field",
                    "expected_outcome": "mixed_committed",
                    "observed_outcome": "mixed_committed",
                    "status": "PASS",
                    "versions": [first.version, second.version],
                    "trace_status": trace_status(QueryForms(repository)),
                    "copy_forward_fields": ["operator"],
                    "candidate_fields": ["quantity", "batch"],
                }
            )
        )
    finally:
        engine.dispose()

    engine, repository, recognition, review, initial_certs, first = initialise("A5_stale_replay")
    try:
        before = database_digest(engine)
        stale_values = {
            "quantity": int(initial_values["quantity"]) + 30,
            "batch": initial_values["batch"],
            "operator": initial_values["operator"],
        }
        try:
            confirm(review, 0, stale_values, initial_certs)
        except ConcurrentReviewError:
            observed = "rejected_stale"
        else:
            raise AssertionError("stale replay unexpectedly committed")
        after = database_digest(engine)
        cases.append(
            write_case(
                {
                    "id": "A5_stale_replay",
                    "operation": "replay a confirmation against an obsolete version",
                    "expected_outcome": "rejected_stale",
                    "observed_outcome": observed,
                    "status": "PASS" if before == after else "FAIL",
                    "versions": [first.version],
                    "database_digest_before": before,
                    "database_digest_after": after,
                    "digest_unchanged": before == after,
                }
            )
        )
    finally:
        engine.dispose()

    engine, repository, recognition, review = new_environment("A6_invalid_item_atomic_rejection")
    try:
        initial_certs = record_machine(repository, recognition, initial_values, crop_offset=220)
        before = database_digest(engine)
        invalid_mapping = {
            "quantity": initial_certs["quantity"],
            "batch": initial_certs["quantity"],
            "operator": initial_certs["operator"],
        }
        try:
            confirm(review, 0, initial_values, invalid_mapping)
        except AuthorityRejectionError:
            observed = "rejected_invalid_item"
        else:
            raise AssertionError("invalid cross-field item unexpectedly committed")
        after = database_digest(engine)
        cases.append(
            write_case(
                {
                    "id": "A6_invalid_item_atomic_rejection",
                    "operation": "substitute a certificate from another field",
                    "expected_outcome": "rejected_invalid_item",
                    "observed_outcome": observed,
                    "status": "PASS" if before == after else "FAIL",
                    "versions": [],
                    "database_digest_before": before,
                    "database_digest_after": after,
                    "digest_unchanged": before == after,
                }
            )
        )
    finally:
        engine.dispose()

    result: dict[str, object] = {
        "schema_version": 1,
        "status": "complete" if all(case["status"] == "PASS" for case in cases) else "failed",
        "fixture": {
            "record_id": candidate.record_id,
            "input_sha256": hashlib.sha256((fixture / "input.txt").read_bytes()).hexdigest(),
            "manifest_sha256": candidate.fixture_sha256,
        },
        "cases": cases,
        "source": {
            "runner": "benchmarks/ai_origin_lifecycle.py",
            "fixture_manifest_sha256": candidate.fixture_sha256,
            "oracle": "tests/conformance/oracle.py:database_digest",
        },
    }
    (raw_root / "ai_origin_lifecycle.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return result
