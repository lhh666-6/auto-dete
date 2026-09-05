"""Opt-in structured AI provider wrapper with strict validation."""

import json
from collections.abc import Callable, Mapping
from typing import Any

from app.adapters.ai.contracts import AIReview


class StructuredAIReviewProvider:
    def __init__(self, completion: Callable[[str], str]) -> None:
        self._completion = completion

    def review(self, form_id: str, context: Mapping[str, Any]) -> AIReview:
        prompt = json.dumps(
            {
                "task": "Return evidence-backed review JSON; never modify business facts.",
                "form_id": form_id,
                "context": context,
                "requires_human_confirmation": True,
            },
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
        review = AIReview.model_validate_json(self._completion(prompt))
        if review.form_id != form_id:
            raise ValueError("AI response form_id does not match the requested form")
        return review
