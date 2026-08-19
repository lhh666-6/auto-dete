from dataclasses import dataclass
from pathlib import Path

import cv2
from sqlalchemy import create_engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.export.xlsx import XlsxExporter
from app.adapters.recognition.candidate import RecognitionCandidate
from app.adapters.recognition.digits import DigitRecognizer
from app.adapters.recognition.omr import OmrRecognizer
from app.adapters.recognition.opencv import FieldRegion, OpenCvImagePipeline
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.export_forms import ExportForms
from app.application.import_forms import ImportForms
from app.application.query_forms import FormFilters, QueryForms
from app.application.recognize_forms import RecognizeForms
from app.application.review_forms import ReviewForms
from app.domain.models import FormField
from benchmarks.baselines import HogSvmBaseline
from benchmarks.synthetic import SyntheticForm


@dataclass(frozen=True, slots=True)
class FormWorkflowOutcome:
    form_id: str
    candidate_count: int
    record_version: int
    export_trace_success: bool
    audit_events: tuple[str, ...]


def run_synthetic_form_workflow(
    form: SyntheticForm,
    root: Path,
    *,
    form_id: str,
    digit_model: HogSvmBaseline | None = None,
    digit_threshold: float = 0.0,
) -> FormWorkflowOutcome:
    root.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{root / 'workflow.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    storage = LocalEvidenceStorage(root / "evidence")
    imports = ImportForms(repository, repository, repository, storage)
    pipeline = OpenCvImagePipeline()
    recognition = RecognizeForms(repository, repository, repository, storage, pipeline)
    reviews = ReviewForms(
        repository,
        repository,
        known_producers=frozenset({("human-reviewer", "manual-entry-v1")}),
        known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
    )
    queries = QueryForms(repository)

    image_path = root / "form.png"
    if not cv2.imwrite(str(image_path), form.image):
        raise RuntimeError("could not persist synthetic form evidence")
    template_id, template_version = form.template_reference.split(":", maxsplit=1)
    original = imports.import_image(
        image_path, form_id, template_id, template_version, "synthetic-generator"
    )
    classification = recognition.classify_image(form_id, form.image)
    if classification.template_reference != form.template_reference:
        raise RuntimeError("synthetic form QR classification failed")

    regions = [
        FieldRegion(f"FIELD-{index:02d}", x, y, width, height)
        for index, (x, y, width, height) in enumerate(form.field_regions)
    ]
    crops = pipeline.crop_fields(form.image, regions)
    digit_recognizer = DigitRecognizer(margin_threshold=0.0)
    omr_recognizer = OmrRecognizer()
    for index, region in enumerate(regions):
        field_name = f"digit_{index}" if index < 10 else f"omr_{index - 10}"
        repository.add_form_field(
            FormField(
                region.field_id,
                form_id,
                field_name,
                {
                    "x": region.x,
                    "y": region.y,
                    "width": region.width,
                    "height": region.height,
                },
            )
        )
        if index < 10 and digit_model is not None:
            prediction = digit_model.predict(crops[region.field_id])
            accepted = prediction.score >= digit_threshold
            candidate = RecognitionCandidate(
                value=prediction.value,
                confidence=max(0.0, min(1.0, prediction.score)),
                engine=digit_model.name,
                model_version="synthetic-training-v1",
                reason_code="OK" if accepted else "AMBIGUOUS",
                accepted=accepted,
                decision_score=prediction.score,
            )
        elif index < 10:
            candidate = digit_recognizer.recognize_cell(crops[region.field_id])
        else:
            candidate = omr_recognizer.recognize(crops[region.field_id])
        recognition.record_candidate(
            form_id, region.field_id, crops[region.field_id], candidate, "machine"
        )

    values = {
        **{f"digit_{index}": value for index, value in enumerate(form.digit_labels)},
        **{f"omr_{index}": value for index, value in enumerate(form.omr_labels)},
    }
    record = reviews.confirm(
        form_id,
        0,
        values,
        "synthetic-reviewer",
        "controlled ground-truth confirmation",
        certificate_ids_by_field={field: None for field in values},
        manual_evidence_ids_by_field={field: original.file_id for field in values},
    )
    batch = ExportForms(repository, XlsxExporter(), queries).export(
        "SYNTHETIC-FORM", FormFilters(form_id=form_id), root / "exports", "finance"
    )
    trace = queries.trace(form_id)
    events = tuple(event.event_type for event in trace.audits)
    success = (
        Path(batch.file_path).exists()
        and record.version == 1
        and len(trace.attempts) == 20
        and trace.versions[-1].values == values
        and {"IMPORT", "CLASSIFY", "RECOGNIZE", "CONFIRM", "EXPORT"}.issubset(events)
    )
    engine.dispose()
    return FormWorkflowOutcome(
        form_id=form_id,
        candidate_count=len(trace.attempts),
        record_version=record.version,
        export_trace_success=success,
        audit_events=events,
    )
