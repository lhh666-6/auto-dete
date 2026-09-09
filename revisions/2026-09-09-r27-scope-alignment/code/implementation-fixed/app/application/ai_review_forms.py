"""Persist AI suggestions separately without mutating business facts."""

from collections.abc import Mapping
from typing import Any, Protocol
from uuid import uuid4

from app.adapters.ai.contracts import AIReview
from app.domain.models import AIReviewRecord, AIStatus, AuditEvent


class AIReviewAdapter(Protocol):
    def review(self, form_id: str, context: Mapping[str, Any]) -> AIReview: ...


class AIReviewRepository(Protocol):
    def add_ai_review(self, review: AIReviewRecord) -> None: ...


class AIReviewForms:
    def __init__(self, reviews: AIReviewRepository, audits: Any, adapter: AIReviewAdapter) -> None:
        self._reviews = reviews
        self._audits = audits
        self._adapter = adapter

    def run(self, form_id: str, context: Mapping[str, Any], actor_id: str) -> AIReview:
        review = self._adapter.review(form_id, context)
        record = AIReviewRecord(
            review_id=f"AI-{uuid4().hex}",
            form_id=form_id,
            status=review.status,
            payload=review.model_dump(mode="json"),
        )
        self._reviews.add_ai_review(record)
        if review.status is AIStatus.SUGGESTED:
            self._audits.add_audit_event(
                AuditEvent(
                    event_id=f"EVENT-{uuid4().hex}",
                    form_id=form_id,
                    event_type="AI_SUGGEST",
                    actor_id=actor_id,
                    after={
                        "review_id": record.review_id,
                        "suggestion_count": len(review.suggestions),
                    },
                )
            )
        return review
