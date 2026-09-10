"""Checkbox OMR recognizer with an explicit ambiguity band."""

import cv2
import numpy as np
from numpy.typing import NDArray

from app.adapters.recognition.candidate import RecognitionCandidate


class OmrRecognizer:
    engine = "opencv-fill-ratio-omr"
    model_version = "fill-ratio-v1"

    def __init__(self, *, unchecked_max: float = 0.15, checked_min: float = 0.35) -> None:
        if not 0 <= unchecked_max < checked_min <= 1:
            raise ValueError("OMR thresholds must define a non-overlapping ambiguity band")
        self._unchecked_max = unchecked_max
        self._checked_min = checked_min

    def recognize(self, image: NDArray[np.uint8]) -> RecognitionCandidate[bool]:
        if image.size == 0:
            raise ValueError("OMR image cannot be empty")
        gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        height, width = binary.shape
        margin_y = max(1, height // 10)
        margin_x = max(1, width // 10)
        interior = binary[margin_y : height - margin_y, margin_x : width - margin_x]
        fill_ratio = float(np.mean(interior > 0))
        if fill_ratio <= self._unchecked_max:
            value: bool | None = False
            reason = "UNCHECKED"
            confidence = 1.0 - fill_ratio / max(self._unchecked_max, 0.01)
        elif fill_ratio >= self._checked_min:
            value = True
            reason = "CHECKED"
            confidence = min(
                1.0, (fill_ratio - self._checked_min) / (1.0 - self._checked_min) + 0.5
            )
        else:
            value = None
            reason = "AMBIGUOUS"
            confidence = 0.0
        return RecognitionCandidate(
            value=value,
            confidence=confidence,
            engine=self.engine,
            model_version=self.model_version,
            reason_code=reason,
            accepted=value is not None,
            decision_score=fill_ratio,
        )
