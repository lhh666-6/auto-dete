from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import create_engine

from app.adapters.ai.contracts import AIReview, AISuggestion
from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.application.ai_review_forms import AIReviewForms
from app.domain.models import AIStatus, Form
from tests.helpers.legacy_fixtures import add_legacy_record_version

NOW = datetime(2026, 1, 1, 9, 0, tzinfo=UTC)


class SuggestedAdapter:
    def review(self, form_id: str, context: dict[str, object]) -> AIReview:
        del context
        return AIReview(
            form_id=form_id,
            status=AIStatus.SUGGESTED,
            risk_level="MEDIUM",
            summary="数量闭合异常",
            suggestions=(
                AISuggestion(
                    field_name="defective_quantity",
                    current_candidate=88,
                    suggested_value=8,
                    confidence=0.91,
                    evidence_types=("RULE",),
                    reason="总数减合格数等于 8",
                ),
            ),
            missing_information=(),
            requires_human_confirmation=True,
        )


def test_ai_review_is_stored_separately_and_does_not_mutate_record(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'demo.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    repository.add_form(Form("FORM-0001", "T1", "1"))
    add_legacy_record_version(
        engine,
        form_id="FORM-0001",
        version=1,
        values={"total_quantity": 10, "defective_quantity": 88},
        confirmed_by="reviewer-old",
        created_at=NOW,
        record_id="RECORD-1",
    )
    before = repository.list_record_versions("FORM-0001")

    result = AIReviewForms(repository, repository, SuggestedAdapter()).run(
        "FORM-0001", {"total_quantity": 10}, "reviewer"
    )

    assert result.status is AIStatus.SUGGESTED
    assert repository.list_record_versions("FORM-0001") == before
    stored = repository.list_ai_reviews("FORM-0001")
    assert stored[0].payload["suggestions"][0]["suggested_value"] == 8
    assert repository.list_audit_events("FORM-0001")[-1].event_type == "AI_SUGGEST"
