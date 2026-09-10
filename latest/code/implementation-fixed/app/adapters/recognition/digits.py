"""Lightweight one-cell-one-digit template recognizer."""

from typing import cast

import cv2
import numpy as np
from numpy.typing import NDArray

from app.adapters.recognition.candidate import RecognitionCandidate


class DigitRecognizer:
    engine = "opencv-template-digit"
    model_version = "synthetic-font-v1"

    def __init__(self, *, margin_threshold: float = 0.02) -> None:
        if margin_threshold < 0:
            raise ValueError("margin_threshold must be non-negative")
        self._margin_threshold = margin_threshold
        self._templates = {str(value): self._normalize(self._render(value)) for value in range(10)}

    def recognize_cell(self, image: NDArray[np.uint8]) -> RecognitionCandidate[str]:
        normalized = self._normalize(image)
        ink_ratio = float(np.mean(normalized > 0))
        if ink_ratio < 0.01:
            return RecognitionCandidate(
                value=None,
                confidence=1.0,
                engine=self.engine,
                model_version=self.model_version,
                reason_code="BLANK",
                accepted=False,
                decision_score=0.0,
            )
        scores = {
            value: float(np.mean(cv2.absdiff(normalized, template))) / 255.0
            for value, template in self._templates.items()
        }
        ordered = sorted(scores.items(), key=lambda item: item[1])
        value, distance = ordered[0]
        margin = max(0.0, ordered[1][1] - distance)
        confidence = max(0.0, min(1.0, (1.0 - distance) * (0.5 + min(0.5, margin * 4))))
        accepted = margin >= self._margin_threshold
        return RecognitionCandidate(
            value=value if accepted else None,
            confidence=confidence,
            engine=self.engine,
            model_version=self.model_version,
            reason_code="OK" if accepted else "AMBIGUOUS",
            accepted=accepted,
            decision_score=margin,
        )

    @staticmethod
    def _render(value: int) -> NDArray[np.uint8]:
        image = np.full((64, 48), 255, dtype=np.uint8)
        cv2.putText(
            image,
            str(value),
            (6, 53),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.8,
            (0,),
            3,
            cv2.LINE_AA,
        )
        return image

    @staticmethod
    def _normalize(image: NDArray[np.uint8]) -> NDArray[np.uint8]:
        if image.size == 0:
            raise ValueError("Digit cell image cannot be empty")
        gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (48, 64), interpolation=cv2.INTER_AREA)
        return cast(
            NDArray[np.uint8],
            cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1],
        )
