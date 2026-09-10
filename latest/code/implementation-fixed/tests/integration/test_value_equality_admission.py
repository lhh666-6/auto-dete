"""End-to-end regression tests for unified value-equality semantics (R1).

Each case drives the public recognition/review/query surface with no database
tampering: a candidate is persisted, a human confirmation is submitted, and the
resulting version, transitions, sources, and reverse trace are checked.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from sqlalchemy import create_engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.adapters.recognition.candidate import RecognitionCandidate
from app.adapters.recognition.opencv import OpenCvImagePipeline
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.query_forms import QueryForms
from app.application.recognize_forms import RecognizeForms
from app.application.review_forms import AuthorityRejectionError, ReviewForms
from app.domain.models import Form, FormField


class Harness:
    def __init__(self, root: Path) -> None:
        self.engine = create_engine(f"sqlite:///{root / 'case.db'}")
        Base.metadata.create_all(self.engine)
        self.repo = SqlAlchemyFormRepository(self.engine)
        self.repo.add_form(Form(form_id="FORM-1", template_id="T1", template_version="1"))
        for field in ("a", "b"):
            self.repo.add_form_field(
                FormField(f"FIELD-{field}", "FORM-1", field, {"x": 0, "y": 0, "w": 8, "h": 8})
            )
        self.recognition = RecognizeForms(
            self.repo,
            self.repo,
            self.repo,
            LocalEvidenceStorage(root / "evidence"),
            OpenCvImagePipeline(),
            candidate_writer=self.repo,
        )
        self.review = ReviewForms(
            self.repo,
            self.repo,
            authority_read=self.repo,
            admission=self.repo,
            known_producers=frozenset({("recognizer-a", "1.0")}),
            known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
        )

    def confirm(self, version: int, values: dict[str, object]) -> None:
        certificates: dict[str, str] = {}
        for field, value in values.items():
            self.recognition.record_candidate(
                "FORM-1",
                f"FIELD-{field}",
                np.full((64, 48), 255, dtype=np.uint8),
                RecognitionCandidate(value, 0.9, "recognizer-a", "1.0", "OK"),
                "machine",
            )
            certificates[field] = self.repo.list_certificates_for_form("FORM-1")[
                -1
            ].certificate_id
        self.review.confirm(
            "FORM-1",
            version,
            values,
            "reviewer-1",
            "ordinary human review",
            certificate_ids_by_field=certificates,
            manual_evidence_ids_by_field={},
        )

    def latest(self):
        return self.repo.list_record_versions("FORM-1")[-1]

    def close(self) -> None:
        self.engine.dispose()


@pytest.fixture()
def harness(tmp_path: Path):
    built = Harness(tmp_path)
    try:
        yield built
    finally:
        built.close()


def _drive(harness: Harness, first_b: object, second_b: object) -> dict[str, object]:
    harness.confirm(0, {"a": 1, "b": first_b})
    harness.confirm(1, {"a": 3, "b": second_b})
    latest = harness.latest()
    trace = QueryForms(harness.repo).trace("FORM-1")
    return {
        "committed": latest.values,
        "transitions": [
            transition.field_key
            for transition in harness.repo.list_transitions_for_version("FORM-1", 2)
        ],
        "sources": latest.fact_sources,
        "trace_status": trace.status,
    }


def test_unchanged_equal_value_copies_source_forward(harness: Harness) -> None:
    result = _drive(harness, 2, 2)
    assert result["committed"] == {"a": 3, "b": 2}
    assert result["transitions"] == ["a"]
    assert result["sources"]["b"] == "FORM-1:1:b"
    assert result["trace_status"] == "complete"


def test_integer_to_float_change_gets_new_transition_and_complete_trace(
    harness: Harness,
) -> None:
    result = _drive(harness, 2, 2.0)
    assert result["committed"] == {"a": 3, "b": 2.0}
    assert set(result["transitions"]) == {"a", "b"}
    assert result["sources"]["b"] == "FORM-1:2:b"
    assert result["trace_status"] == "complete"


def test_integer_to_boolean_change_gets_new_transition_and_complete_trace(
    harness: Harness,
) -> None:
    result = _drive(harness, 1, True)
    assert result["committed"] == {"a": 3, "b": True}
    assert set(result["transitions"]) == {"a", "b"}
    assert result["sources"]["b"] == "FORM-1:2:b"
    assert result["trace_status"] == "complete"


def test_single_field_numeric_change_commits_alone(harness: Harness) -> None:
    harness.confirm(0, {"a": 1, "b": 2})
    harness.confirm(1, {"a": 1, "b": 2.0})
    latest = harness.latest()
    assert latest.values == {"a": 1, "b": 2.0}
    assert [t.field_key for t in harness.repo.list_transitions_for_version("FORM-1", 2)] == ["b"]
    assert QueryForms(harness.repo).trace("FORM-1").status == "complete"


def test_nested_numeric_change_commits_with_complete_trace(harness: Harness) -> None:
    result = _drive(harness, {"k": 1}, {"k": 1.0})
    assert result["committed"] == {"a": 3, "b": {"k": 1.0}}
    assert set(result["transitions"]) == {"a", "b"}
    assert result["trace_status"] == "complete"


def test_pure_canonical_noop_is_rejected_fail_closed(harness: Harness) -> None:
    harness.confirm(0, {"a": 1, "b": 2})
    with pytest.raises(AuthorityRejectionError) as excinfo:
        harness.confirm(1, {"a": 1, "b": 2})
    assert [failure.code for failure in excinfo.value.failures] == ["NO_CHANGED_FIELDS"]
    assert harness.latest().version == 1
    assert QueryForms(harness.repo).trace("FORM-1").status == "complete"
