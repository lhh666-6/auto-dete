"""E6 one-command illustrative document admission lifecycle."""

from __future__ import annotations

import argparse
import hashlib
import json
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
from app.adapters.export.xlsx import XlsxExporter
from app.adapters.recognition.candidate import RecognitionCandidate
from app.adapters.recognition.opencv import OpenCvImagePipeline
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.export_forms import ExportForms
from app.application.import_forms import ImportForms
from app.application.query_forms import FormFilters, QueryForms
from app.application.recognize_forms import RecognizeForms
from app.application.review_forms import ReviewForms
from app.domain.evidence_identity import locator_from_evidence
from app.domain.models import FormField
from app.domain.principal import prototype_principal_policy


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _candidate(value: object) -> RecognitionCandidate[object]:
    return RecognitionCandidate(
        value=value,
        confidence=0.99,
        engine="lifecycle-recognizer",
        model_version="1",
        reason_code="OK",
        accepted=True,
        decision_score=0.99,
    )


def run_lifecycle(output: Path) -> dict[str, object]:
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    raw = output / "raw"
    raw.mkdir()
    work = output / "work"
    work.mkdir()
    engine = create_engine(f"sqlite:///{work / 'lifecycle.db'}")
    install_sqlite_pragmas(engine)
    Base.metadata.create_all(engine)
    migrate_schema(engine)
    repository = SqlAlchemyFormRepository(
        engine, principal_policy=prototype_principal_policy(("reviewer",))
    )
    storage = LocalEvidenceStorage(work / "evidence")
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
            {("lifecycle-recognizer", "1"), ("human-reviewer", "manual-entry-v1")}
        ),
        known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
    )
    image = work / "synthetic-form.png"
    image.write_bytes(b"authorized synthetic form lifecycle v1")
    original = imports.import_image(image, "FORM-LIFE", "T1", "1", "generator")
    fields = ("quantity", "batch", "operator")
    initial_values: dict[str, object] = {"quantity": 10, "batch": "B-1", "operator": "OP-7"}
    initial_certificates: dict[str, str] = {}
    for index, field_name in enumerate(fields):
        field_id = f"FIELD-{index}"
        repository.add_form_field(FormField(field_id, "FORM-LIFE", field_name, {}))
        crop = np.full((16, 16), index * 40 + 30, dtype=np.uint8)
        recognition.record_candidate(
            "FORM-LIFE", field_id, crop, _candidate(initial_values[field_name]), "machine"
        )
        certificate = repository.list_certificates_for_field("FORM-LIFE", field_name, 0)[0]
        initial_certificates[field_name] = certificate.certificate_id
    review.confirm(
        "FORM-LIFE",
        0,
        initial_values,
        "reviewer",
        "accept initial machine batch",
        certificate_ids_by_field=initial_certificates,
        manual_evidence_ids_by_field={},
    )
    version1 = repository.list_record_versions("FORM-LIFE")[-1]
    recognition.record_candidate(
        "FORM-LIFE",
        "FIELD-0",
        np.full((16, 16), 200, dtype=np.uint8),
        _candidate(100),
        "machine",
    )
    correction_certificate = repository.list_certificates_for_field("FORM-LIFE", "quantity", 1)[0]
    correction_values: dict[str, object] = {"quantity": 101, "batch": "B-1", "operator": "OP-7"}
    review.confirm(
        "FORM-LIFE",
        1,
        correction_values,
        "reviewer",
        "correct machine quantity",
        certificate_ids_by_field={
            "quantity": correction_certificate.certificate_id,
            "batch": initial_certificates["batch"],
            "operator": initial_certificates["operator"],
        },
        manual_evidence_ids_by_field={},
    )
    version2 = repository.list_record_versions("FORM-LIFE")[-1]
    query = QueryForms(repository)
    trace = query.trace("FORM-LIFE")
    assert trace.status == "complete"
    export = ExportForms(repository, XlsxExporter(), query).export(
        "LIFECYCLE", FormFilters(form_id="FORM-LIFE"), work / "exports", "reviewer"
    )
    transition = repository.get_fact_transition(version2.fact_sources["quantity"])
    assert transition is not None
    binding = next(
        item
        for item in repository.list_authorization_bindings_for_form("FORM-LIFE")
        if item.decision_id == transition.decision_id
    )
    result: dict[str, object] = {
        "schema_version": 1,
        "status": "complete",
        "input_sha256": _sha256(image),
        "input_evidence_locator": locator_from_evidence(original),
        "versions": [version1.version, version2.version],
        "initial_values": initial_values,
        "final_values": correction_values,
        "correction": {
            "certificate_id": correction_certificate.certificate_id,
            "machine_candidate": correction_certificate.value,
            "authorized_value": binding.value,
            "transition_id": transition.transition_id,
        },
        "copy_forward_fields": sorted(
            field
            for field in fields
            if version1.fact_sources[field] == version2.fact_sources[field]
        ),
        "trace_status": trace.status,
        "export_sha256": export.file_sha256,
        "export_values_equal_final": trace.versions[-1].values == correction_values,
    }
    (raw / "lifecycle.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    engine.dispose()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_lifecycle(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
