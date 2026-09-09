from pathlib import Path

import cv2
import numpy as np
from sqlalchemy import create_engine

from app.adapters.ai.disabled import DisabledAIReview
from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.export.xlsx import XlsxExporter
from app.adapters.recognition.digits import DigitRecognizer
from app.adapters.recognition.opencv import OpenCvImagePipeline
from app.adapters.storage.local import LocalEvidenceStorage
from app.adapters.vector.local import LocalVectorIndex, VectorDocument
from app.application.export_forms import ExportForms
from app.application.import_forms import ImportForms
from app.application.query_forms import FormFilters, QueryForms
from app.application.recognize_forms import RecognizeForms
from app.application.review_forms import ReviewForms
from app.domain.models import AIStatus, ExportStatus, FormField, ReviewStatus
from app.domain.rules import RuleContext, validate


def test_combined_demo_flow_preserves_human_fact_and_reverse_trace(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'demo.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    storage = LocalEvidenceStorage(tmp_path / "evidence")
    imports = ImportForms(repository, repository, repository, storage)
    recognition = RecognizeForms(
        repository,
        repository,
        repository,
        storage,
        OpenCvImagePipeline(),
        candidate_writer=repository,
    )
    queries = QueryForms(repository)
    image_path = tmp_path / "form.png"
    image_path.write_bytes(b"immutable-original")
    original = imports.import_image(image_path, "FORM-0001", "UNKNOWN", "1", "operator")

    qr = cv2.QRCodeEncoder_create().encode("OUTPUT:1")
    classification = recognition.classify_image("FORM-0001", qr)
    assert classification.template_reference == "OUTPUT:1"
    assert repository.get_form("FORM-0001").review_status is ReviewStatus.CLASSIFIED  # type: ignore[union-attr]

    repository.add_form_field(
        FormField(
            "FIELD-TOTAL",
            "FORM-0001",
            "total_quantity",
            {"x": 0, "y": 0, "width": 48, "height": 64},
        )
    )
    digit_crop = np.full((64, 48), 255, dtype=np.uint8)
    cv2.putText(digit_crop, "7", (6, 53), cv2.FONT_HERSHEY_SIMPLEX, 1.8, 0, 3, cv2.LINE_AA)
    candidate = DigitRecognizer().recognize_cell(digit_crop)
    recognition.record_candidate("FORM-0001", "FIELD-TOTAL", digit_crop, candidate, "ocr")

    values = {
        "employee_id": "E001",
        "work_order_id": "WO-1",
        "total_quantity": 7,
        "qualified_quantity": 6,
        "defective_quantity": 1,
    }
    for index, field_name in enumerate(values, start=1):
        if field_name == "total_quantity":
            continue
        repository.add_form_field(
            FormField(
                f"FIELD-{index}",
                "FORM-0001",
                field_name,
                {"x": 0, "y": 0, "width": 48, "height": 64},
            )
        )
    rule_failures = validate(
        RuleContext(
            values=values,
            required_fields=frozenset({"employee_id", "work_order_id", "total_quantity"}),
            ranges={"total_quantity": (0, 99999)},
            valid_employee_ids=frozenset({"E001"}),
            valid_work_order_ids=frozenset({"WO-1"}),
            is_duplicate_form=False,
            expected_version=0,
            current_version=0,
            export_status=ExportStatus.NOT_EXPORTED,
            required_export_fields=frozenset({"employee_id", "total_quantity"}),
            export_mapping={"employee_id": "员工", "total_quantity": "总产量"},
        )
    )
    assert rule_failures == []
    ReviewForms(
        repository,
        repository,
        authority_read=repository,
        admission=repository,
        known_producers=frozenset({("human-reviewer", "manual-entry-v1")}),
        known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
    ).confirm(
        "FORM-0001",
        0,
        values,
        "reviewer",
        "human confirmed",
        certificate_ids_by_field={field: None for field in values},
        manual_evidence_ids_by_field={field: original.file_id for field in values},
    )
    assert repository.list_record_versions("FORM-0001")[-1].values["total_quantity"] == 7

    ai_review = DisabledAIReview().review("FORM-0001", values)
    assert ai_review.status is AIStatus.NOT_RUN
    index = LocalVectorIndex()
    index.add(VectorDocument("V1", "FORM-0001", "EXCEPTION", "数量闭合已人工确认"))
    assert index.search("数量确认")[0].document.form_id == "FORM-0001"

    batch = ExportForms(repository, XlsxExporter(), queries).export(
        "OUTPUT", FormFilters(), tmp_path / "exports", "finance"
    )
    trace = queries.trace("FORM-0001")
    assert Path(batch.file_path).exists()
    assert trace.versions[-1].values["total_quantity"] == 7
    assert trace.attempts[0].candidate_value == "7"
    assert original.sha256 == storage.hash_path(image_path)
    assert {event.event_type for event in trace.audits} >= {
        "IMPORT",
        "CLASSIFY",
        "RECOGNIZE",
        "CONFIRM",
        "EXPORT",
    }
