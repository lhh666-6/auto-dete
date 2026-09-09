"""Safe default AI adapter that performs no external calls."""

from collections.abc import Mapping
from typing import Any

from app.adapters.ai.contracts import AIReview
from app.domain.models import AIStatus


class DisabledAIReview:
    def review(self, form_id: str, context: Mapping[str, Any]) -> AIReview:
        del context
        return AIReview(
            form_id=form_id,
            status=AIStatus.NOT_RUN,
            risk_level="UNKNOWN",
            summary="AI 功能已关闭，使用确定性规则和人工复核。",
            suggestions=(),
            missing_information=(),
            requires_human_confirmation=True,
        )
