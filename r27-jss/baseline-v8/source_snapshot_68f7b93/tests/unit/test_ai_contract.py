import pytest
from pydantic import ValidationError

from app.adapters.ai.contracts import AIReview, AISuggestion
from app.adapters.ai.disabled import DisabledAIReview
from app.adapters.ai.provider import StructuredAIReviewProvider
from app.domain.models import AIStatus


def test_disabled_ai_returns_safe_empty_review() -> None:
    review = DisabledAIReview().review("FORM-0001", {"total_quantity": 10})

    assert review.status is AIStatus.NOT_RUN
    assert review.form_id == "FORM-0001"
    assert review.suggestions == ()
    assert review.requires_human_confirmation is True


def test_ai_suggestion_requires_evidence_and_human_confirmation() -> None:
    with pytest.raises(ValidationError):
        AISuggestion(
            field_name="defective_quantity",
            current_candidate=88,
            suggested_value=8,
            confidence=0.91,
            evidence_types=(),
            reason="closure mismatch",
        )


def test_provider_parses_strict_json_and_rejects_unsupported_suggestion() -> None:
    valid = """{
      "form_id":"FORM-0001","status":"SUGGESTED","risk_level":"MEDIUM",
      "summary":"closure mismatch","suggestions":[{
        "field_name":"defective_quantity","current_candidate":88,"suggested_value":8,
        "confidence":0.91,"evidence_types":["RULE"],"reason":"10 - 2 = 8"
      }],"missing_information":[],"requires_human_confirmation":true
    }"""
    review = StructuredAIReviewProvider(lambda _: valid).review("FORM-0001", {"total_quantity": 10})
    assert review.suggestions[0].evidence_types == ("RULE",)

    unsupported = valid.replace('"evidence_types":["RULE"]', '"evidence_types":[]')
    with pytest.raises(ValidationError):
        StructuredAIReviewProvider(lambda _: unsupported).review("FORM-0001", {})

    with pytest.raises(ValidationError):
        AIReview(
            form_id="FORM-0001",
            status=AIStatus.SUGGESTED,
            risk_level="MEDIUM",
            summary="candidate mismatch",
            suggestions=(),
            missing_information=(),
            requires_human_confirmation=False,
        )
