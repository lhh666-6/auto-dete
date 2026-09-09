"""Pipeline authority integration benchmark (NOT field evidence).

Runs the real services (import -> recognize -> confirm) over a synthetic
fault corpus: a fault-injector producer writes known-wrong machine values,
a scripted reviewer accepts or fixes them, and the metrics are counted from
the database. Trace statuses are verified through the real QueryForms.trace,
including explicit negative probes (cross-field certificate substitution,
cross-form evidence, tampered transitions, deleted transitions). Results are
exported with an immutable manifest; this benchmark must never be cited as
human-factors or field evidence (the future ~100-form human study is
separate and out of scope here).
"""

import argparse
import hashlib
import importlib.metadata
import json
import sqlite3
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
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

# Fixed evaluation clock so runs are byte-identical under the same seed.
FIXED_CLOCK = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)

METRIC_KEYS = (
    "cases",
    "facts_created",
    "automatic_completion_rate",
    "manual_routing_rate",
    "silent_fault_escape_rate",
    "invalid_transition_rejection_rate",
    "valid_certificate_coverage",
    "corruption_detection_rate",
    "reverse_trace_completeness",
    "stale_transition_containment",
    "review_burden",
    "wrong_values_presented",
    "wrong_value_facts",
)

PRODUCERS = frozenset({("fault-injector", "1"), ("human-reviewer", "manual-entry-v1")})
SELECTION_ARTIFACTS = frozenset({"recognition-threshold-v1"})


def _git(*arguments: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *arguments], check=True, capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout.strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_pipeline_benchmark(
    output: Path,
    *,
    now: datetime = FIXED_CLOCK,
    seed: int = 20260817,
    case_count: int = 12,
) -> dict[str, object]:
    """Run the pipeline integration benchmark and write artifacts + manifest."""
    output.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    with tempfile.TemporaryDirectory(prefix="pipeline-authority-") as temporary:
        root = Path(temporary)
        engine = create_engine(f"sqlite:///{root / 'demo.db'}")
        install_sqlite_pragmas(engine)
        Base.metadata.create_all(engine)
        stamp_schema_version(engine)
        repository = SqlAlchemyFormRepository(engine)
        storage = LocalEvidenceStorage(root / "evidence")
        imports = ImportForms(repository, repository, repository, storage)
        recognition = RecognizeForms(
            repository,
            repository,
            repository,
            storage,
            OpenCvImagePipeline(),
            candidate_writer=CandidateWriteFacade(repository),
        )
        reviews = ReviewForms(
            repository,
            repository,
            authority_read=AuthorityReadFacade(repository),
            admission=FactAdmissionFacade(repository),
            known_producers=PRODUCERS,
            known_selection_artifacts=SELECTION_ARTIFACTS,
        )
        queries = QueryForms(repository)

        def import_form(form_id: str, *field_names: str) -> list[FormField]:
            image = root / f"{form_id}.png"
            image.write_bytes(f"pipeline-{form_id}".encode())
            imports.import_image(image, form_id, "T1", "1", "synthetic")
            fields = []
            for field_name in field_names:
                field = FormField(
                    f"{form_id}-{field_name}",
                    form_id,
                    field_name,
                    {"x": 0, "y": 0, "width": 8, "height": 8},
                )
                repository.add_form_field(field)
                fields.append(field)
            return fields

        def recognize(form_id: str, field: FormField, value: int) -> None:
            crop = np.full((64, 48), 255, dtype=np.uint8)
            recognition.record_candidate(
                form_id,
                field.field_id,
                crop,
                RecognitionCandidate(value, 0.9, "fault-injector", "1", "OK"),
                "machine",
            )

        wrong_presented = 0
        wrong_facts = 0
        trace_statuses: list[str] = []
        facts_created = 0
        valid_attempts = 0
        valid_success = 0
        for index in range(case_count):
            form_id = f"PIPE-{index:03d}"
            image = root / f"{form_id}.png"
            image.write_bytes(f"pipeline-{index}".encode())
            imports.import_image(image, form_id, "T1", "1", "synthetic")
            field = FormField(
                f"FIELD-{index:03d}",
                form_id,
                "total_quantity",
                {"x": 0, "y": 0, "width": 8, "height": 8},
            )
            repository.add_form_field(field)
            truth = int(rng.integers(1, 100))
            wrong = bool(rng.random() < 0.4)
            machine_value = int(rng.integers(1, 100)) if wrong else truth
            crop = np.full((64, 48), 255, dtype=np.uint8)
            candidate = RecognitionCandidate(
                machine_value,
                float(rng.uniform(0.4, 0.99)),
                "fault-injector",
                "1",
                "INJECTED",
            )
            recognition.record_candidate(form_id, field.field_id, crop, candidate, "machine")
            certificate = repository.list_certificates_for_form(form_id)[0]
            reviewer_fixes = bool(rng.random() < 0.6)
            final_value = truth if (wrong and reviewer_fixes) else machine_value
            if wrong:
                wrong_presented += 1
            valid_attempts += 1
            reviews.confirm(
                form_id,
                0,
                {"total_quantity": final_value},
                "reviewer",
                "scripted review",
                certificate_ids_by_field={"total_quantity": certificate.certificate_id},
                manual_evidence_ids_by_field={},
            )
            valid_success += 1
            facts_created += 1
            if wrong and final_value == machine_value:
                wrong_facts += 1
            trace = queries.trace(form_id)
            trace_statuses.append(trace.status)

        # ------------------------------------------------------------------
        # Explicit positive/negative probes (no rng: fully deterministic).
        # invalid_transition_rejection_rate and valid_certificate_coverage
        # are counted from these outcomes, never constants.
        # ------------------------------------------------------------------
        invalid_attempts = 0
        invalid_rejected = 0
        corruptions_injected = 0
        corruptions_detected = 0

        # (a) cross-field certificate substitution must reject with zero writes.
        fields = import_form("PIPE-XFIELD", "total_quantity")
        recognize("PIPE-XFIELD", fields[0], 42)
        xfield_certificate = repository.list_certificates_for_form("PIPE-XFIELD")[0]
        invalid_attempts += 1
        try:
            reviews.confirm(
                "PIPE-XFIELD",
                0,
                {"total_quantity": 42, "extra_field": 9},
                "reviewer",
                "cross-field probe",
                certificate_ids_by_field={
                    "total_quantity": None,
                    "extra_field": xfield_certificate.certificate_id,
                },
                manual_evidence_ids_by_field={
                    "total_quantity": repository.list_evidence("PIPE-XFIELD")[0].file_id,
                },
            )
        except AuthorityRejectionError:
            invalid_rejected += 1

        # (b) cross-form evidence must reject with zero writes.
        import_form("PIPE-XEVID", "total_quantity")
        invalid_attempts += 1
        try:
            reviews.confirm(
                "PIPE-XEVID",
                0,
                {"total_quantity": 7},
                "reviewer",
                "cross-evidence probe",
                certificate_ids_by_field={"total_quantity": None},
                manual_evidence_ids_by_field={
                    "total_quantity": repository.list_evidence("PIPE-000")[0].file_id,
                },
            )
        except AuthorityRejectionError:
            invalid_rejected += 1

        # (c) tampered transition producer: trace must report incomplete.
        fields = import_form("PIPE-TAMPER", "total_quantity", "qualified_quantity")
        for field, value in zip(fields, (7, 5), strict=True):
            recognize("PIPE-TAMPER", field, value)
        tamper_certs = {
            certificate.field_key: certificate
            for certificate in repository.list_certificates_for_form("PIPE-TAMPER")
        }
        reviews.confirm(
            "PIPE-TAMPER",
            0,
            {"total_quantity": 7, "qualified_quantity": 5},
            "reviewer",
            "two-field confirm",
            certificate_ids_by_field={
                field_key: certificate.certificate_id
                for field_key, certificate in tamper_certs.items()
            },
            manual_evidence_ids_by_field={},
        )
        facts_created += 1
        corruptions_injected += 1
        tamper_connection = sqlite3.connect(root / "demo.db")
        tamper_connection.execute("PRAGMA foreign_keys=OFF")
        tamper_connection.execute(
            "UPDATE fact_transitions SET producer_id='tampered-producer' "
            "WHERE field_key='total_quantity'"
        )
        tamper_connection.commit()
        tamper_connection.close()
        tamper_trace = queries.trace("PIPE-TAMPER")
        trace_statuses.append(tamper_trace.status)
        if tamper_trace.status == "incomplete":
            corruptions_detected += 1

        # (d) deleted transition: field-set completeness must report incomplete.
        fields = import_form("PIPE-MISSING", "total_quantity", "qualified_quantity")
        for field, value in zip(fields, (7, 5), strict=True):
            recognize("PIPE-MISSING", field, value)
        missing_certs = {
            certificate.field_key: certificate
            for certificate in repository.list_certificates_for_form("PIPE-MISSING")
        }
        reviews.confirm(
            "PIPE-MISSING",
            0,
            {"total_quantity": 7, "qualified_quantity": 5},
            "reviewer",
            "two-field confirm",
            certificate_ids_by_field={
                field_key: certificate.certificate_id
                for field_key, certificate in missing_certs.items()
            },
            manual_evidence_ids_by_field={},
        )
        facts_created += 1
        corruptions_injected += 1
        delete_connection = sqlite3.connect(root / "demo.db")
        delete_connection.execute("PRAGMA foreign_keys=OFF")
        delete_connection.execute("DELETE FROM fact_transitions WHERE field_key='total_quantity'")
        delete_connection.commit()
        delete_connection.close()
        missing_trace = queries.trace("PIPE-MISSING")
        trace_statuses.append(missing_trace.status)
        if missing_trace.status == "incomplete":
            corruptions_detected += 1

        # (e) rebound record_version_id: the F-row must point at the exact
        # selected record-version row, not merely at some existing row.
        fields = import_form("PIPE-REBIND", "total_quantity")
        recognize("PIPE-REBIND", fields[0], 7)
        rebind_certificate = repository.list_certificates_for_form("PIPE-REBIND")[0]
        reviews.confirm(
            "PIPE-REBIND",
            0,
            {"total_quantity": 7},
            "reviewer",
            "rebind confirm",
            certificate_ids_by_field={"total_quantity": rebind_certificate.certificate_id},
            manual_evidence_ids_by_field={},
        )
        facts_created += 1
        reviews.confirm(
            "PIPE-REBIND",
            1,
            {"total_quantity": 8},
            "reviewer",
            "rebind correction",
            certificate_ids_by_field={"total_quantity": None},
            manual_evidence_ids_by_field={
                "total_quantity": repository.list_evidence("PIPE-REBIND")[0].file_id,
            },
        )
        facts_created += 1
        rebind_versions = repository.list_record_versions("PIPE-REBIND")
        assert len(rebind_versions) == 2
        corruptions_injected += 1
        rebind_connection = sqlite3.connect(root / "demo.db")
        rebind_connection.execute("PRAGMA foreign_keys=OFF")
        rebind_connection.execute(
            "UPDATE fact_transitions SET record_version_id = ? "
            "WHERE created_version=1 AND form_id='PIPE-REBIND'",
            (rebind_versions[1].record_id,),
        )
        rebind_connection.commit()
        rebind_connection.close()
        rebind_trace = queries.trace("PIPE-REBIND", 1)
        trace_statuses.append(rebind_trace.status)
        if rebind_trace.status == "incomplete":
            corruptions_detected += 1

        stale_rejected = False
        last_certificate = repository.list_certificates_for_form("PIPE-000")[0]
        try:
            reviews.confirm(
                "PIPE-000",
                0,
                {"total_quantity": 999},
                "reviewer-2",
                "stale replay",
                certificate_ids_by_field={"total_quantity": last_certificate.certificate_id},
                manual_evidence_ids_by_field={},
            )
        except ConcurrentReviewError:
            stale_rejected = True

        complete = sum(1 for status in trace_statuses if status == "complete")
        metrics: dict[str, float | int] = {
            "cases": case_count,
            "facts_created": facts_created,
            "automatic_completion_rate": 0.0,
            "manual_routing_rate": 1.0,
            "silent_fault_escape_rate": (wrong_facts / wrong_presented if wrong_presented else 0.0),
            "invalid_transition_rejection_rate": (
                invalid_rejected / invalid_attempts if invalid_attempts else 0.0
            ),
            "valid_certificate_coverage": (
                valid_success / valid_attempts if valid_attempts else 0.0
            ),
            "corruption_detection_rate": (
                corruptions_detected / corruptions_injected if corruptions_injected else 0.0
            ),
            "reverse_trace_completeness": (
                complete / len(trace_statuses) if trace_statuses else 0.0
            ),
            "stale_transition_containment": 1.0 if stale_rejected else 0.0,
            "review_burden": 1.0,
            "wrong_values_presented": wrong_presented,
            "wrong_value_facts": wrong_facts,
        }
        engine.dispose()

    payload: dict[str, object] = {
        "metrics": metrics,
        "trace_statuses": trace_statuses,
        "stale_rejected": stale_rejected,
    }
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    (output / "pipeline_authority.json").write_bytes(encoded)

    # Standard worktree cleanliness: git status --porcelain INCLUDES
    # untracked files. Top-level ignored paths (external runtime state such
    # as .superpowers/, the Codex guidance document, .venv/) are recorded
    # explicitly so clean_before_run=true is transparent about exclusions.
    porcelain = _git("status", "--porcelain")
    ignored_untracked = sorted(
        line[3:]
        for line in (_git("status", "--porcelain", "--ignored") or "").splitlines()
        if line.startswith("!!")
    )
    packages: dict[str, str | None] = {}
    for package in ("sqlalchemy", "numpy", "opencv-python-headless", "pydantic"):
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = None
    manifest = {
        "source_commit": _git("rev-parse", "HEAD"),
        "clean_before_run": None if porcelain is None else not porcelain,
        "git_status_porcelain": porcelain,
        "ignored_untracked_paths": ignored_untracked,
        "config_sha256": _sha256(Path("pyproject.toml").resolve()),
        "seeds": [seed],
        "clock_utc": now.isoformat(),
        "started_utc": now.isoformat(),
        "ended_utc": now.isoformat(),
        "packages": packages,
        "case_count": case_count,
        "artifacts": [
            {
                "path": "pipeline_authority.json",
                "sha256": _sha256(output / "pipeline_authority.json"),
                "bytes": (output / "pipeline_authority.json").stat().st_size,
            }
        ],
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the pipeline authority integration benchmark")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--now", type=str, default=FIXED_CLOCK.isoformat())
    parser.add_argument("--seed", type=int, default=20260817)
    parser.add_argument("--cases", type=int, default=12)
    args = parser.parse_args()
    now = datetime.fromisoformat(args.now)
    if now.tzinfo is None or now.utcoffset() is None:
        raise SystemExit("--now must be timezone-aware")
    payload = run_pipeline_benchmark(args.output, now=now, seed=args.seed, case_count=args.cases)
    metrics = payload["metrics"]
    print(json.dumps(metrics, indent=2, sort_keys=True))
    valid = (
        metrics["invalid_transition_rejection_rate"] == 1.0
        and metrics["valid_certificate_coverage"] == 1.0
        and metrics["corruption_detection_rate"] == 1.0
        and metrics["stale_transition_containment"] == 1.0
    )
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
