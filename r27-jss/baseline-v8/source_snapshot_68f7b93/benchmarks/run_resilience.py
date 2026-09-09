import argparse
import os
import platform
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from sqlalchemy import create_engine

from app.adapters.ai.disabled import DisabledAIReview
from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.export.xlsx import XlsxExporter
from app.adapters.recognition.digits import DigitRecognizer
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.ai_review_forms import AIReviewForms
from app.application.export_forms import ExportForms
from app.application.import_forms import DuplicateEvidenceError, ImportForms
from app.application.query_forms import FormFilters, QueryForms
from app.application.review_forms import ConcurrentReviewError, ReviewForms
from app.domain.models import AIStatus
from benchmarks.io import write_json
from benchmarks.synthetic import render_digit


@dataclass(frozen=True, slots=True)
class ResilienceResult:
    checks: dict[str, bool]
    latency: dict[str, list[float]]
    latency_summary: dict[str, dict[str, float]]
    environment: dict[str, str | int | None]
    repetitions: int
    warmups: int


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "median_ms": float(np.median(values)),
        "iqr_ms": float(np.percentile(values, 75) - np.percentile(values, 25)),
        "p95_ms": float(np.percentile(values, 95)),
    }


def _measure_latency(repetitions: int, warmups: int) -> dict[str, list[float]]:
    image = render_digit("7", font=cv2.FONT_HERSHEY_SIMPLEX, seed=77)
    warm_model = DigitRecognizer()
    for _ in range(warmups):
        warm_model.recognize_cell(image)
    warm: list[float] = []
    cold: list[float] = []
    for _ in range(repetitions):
        started = time.perf_counter_ns()
        warm_model.recognize_cell(image)
        warm.append((time.perf_counter_ns() - started) / 1_000_000)

        started = time.perf_counter_ns()
        DigitRecognizer().recognize_cell(image)
        cold.append((time.perf_counter_ns() - started) / 1_000_000)
    return {"warm_ms": warm, "cold_ms": cold}


def run_resilience(output: Path, *, repetitions: int = 30, warmups: int = 5) -> ResilienceResult:
    if repetitions <= 0 or warmups < 0:
        raise ValueError("repetitions must be positive and warmups non-negative")
    with tempfile.TemporaryDirectory(prefix="auto-decte-resilience-") as temporary:
        root = Path(temporary)
        engine = create_engine(f"sqlite:///{root / 'demo.db'}")
        Base.metadata.create_all(engine)
        repository = SqlAlchemyFormRepository(engine)
        storage = LocalEvidenceStorage(root / "evidence")
        imports = ImportForms(repository, repository, repository, storage)
        reviews = ReviewForms(
            repository,
            repository,
            known_producers=frozenset({("human-reviewer", "manual-entry-v1")}),
            known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
        )
        queries = QueryForms(repository)
        image_path = root / "form.png"
        image_path.write_bytes(b"controlled synthetic evidence")
        evidence = imports.import_image(image_path, "FORM-1", "T1", "1", "operator")
        confirm_values = {"employee_id": "SYNTH-001", "total_quantity": 7}
        reviews.confirm(
            "FORM-1",
            0,
            confirm_values,
            "reviewer",
            "controlled benchmark",
            certificate_ids_by_field={field: None for field in confirm_values},
            manual_evidence_ids_by_field={field: evidence.file_id for field in confirm_values},
        )

        ai_result = AIReviewForms(repository, repository, DisabledAIReview()).run(
            "FORM-1", {"total_quantity": 7}, "reviewer"
        )
        duplicate_rejected = False
        try:
            imports.import_image(image_path, "FORM-2", "T1", "1", "operator")
        except DuplicateEvidenceError:
            duplicate_rejected = True
        stale_rejected = False
        try:
            reviews.confirm(
                "FORM-1", 0, {"total_quantity": 8}, "reviewer-2", "stale",
                certificate_ids_by_field={"total_quantity": None},
                manual_evidence_ids_by_field={"total_quantity": evidence.file_id},
            )
        except ConcurrentReviewError:
            stale_rejected = True

        batch = ExportForms(repository, XlsxExporter(), queries).export(
            "CONTROLLED", FormFilters(), root / "exports", "finance"
        )
        trace = queries.trace("FORM-1")
        reverse_trace = (
            Path(batch.file_path).exists()
            and len(trace.versions) == 1
            and trace.versions[0].values["total_quantity"] == 7
            and evidence.file_id in {item.file_id for item in trace.evidence}
            and {"IMPORT", "CONFIRM", "EXPORT"}.issubset(
                {event.event_type for event in trace.audits}
            )
        )
        checks = {
            "ai_disabled": ai_result.status is AIStatus.NOT_RUN,
            "duplicate_rejected": duplicate_rejected,
            "stale_rejected": stale_rejected,
            "reverse_trace": reverse_trace,
        }
        engine.dispose()

    latency = _measure_latency(repetitions, warmups)
    result = ResilienceResult(
        checks=checks,
        latency=latency,
        latency_summary={name: _summary(values) for name, values in latency.items()},
        environment={
            "platform": platform.platform(),
            "processor": platform.processor() or None,
            "logical_cpus": os.cpu_count(),
            "python": platform.python_version(),
        },
        repetitions=repetitions,
        warmups=warmups,
    )
    write_json(output, [result])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run operational resilience checks")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=30)
    parser.add_argument("--warmups", type=int, default=5)
    args = parser.parse_args()
    result = run_resilience(args.output, repetitions=args.repetitions, warmups=args.warmups)
    return 0 if all(result.checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
