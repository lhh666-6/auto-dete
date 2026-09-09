import cv2
import numpy as np

from app.adapters.recognition.digits import DigitRecognizer
from app.adapters.recognition.omr import OmrRecognizer


def digit_image(value: int) -> np.ndarray:
    image = np.full((64, 48), 255, dtype=np.uint8)
    cv2.putText(image, str(value), (6, 53), cv2.FONT_HERSHEY_SIMPLEX, 1.8, 0, 3, cv2.LINE_AA)
    return image


def test_digit_recognizer_returns_one_digit_with_model_metadata() -> None:
    candidate = DigitRecognizer().recognize_cell(digit_image(7))

    assert candidate.value == "7"
    assert 0.0 <= candidate.confidence <= 1.0
    assert candidate.engine == "opencv-template-digit"
    assert candidate.model_version == "synthetic-font-v1"


def test_blank_digit_cell_is_not_invented() -> None:
    candidate = DigitRecognizer().recognize_cell(np.full((64, 48), 255, dtype=np.uint8))
    assert candidate.value is None
    assert candidate.reason_code == "BLANK"


def checkbox(fill_ratio: float) -> np.ndarray:
    image = np.full((60, 60), 255, dtype=np.uint8)
    cv2.rectangle(image, (5, 5), (54, 54), 0, 2)
    if fill_ratio > 0:
        side = int(40 * fill_ratio**0.5)
        start = 30 - side // 2
        cv2.rectangle(image, (start, start), (start + side, start + side), 0, -1)
    return image


def test_omr_distinguishes_checked_unchecked_and_ambiguous() -> None:
    recognizer = OmrRecognizer(unchecked_max=0.15, checked_min=0.35)

    assert recognizer.recognize(checkbox(0.0)).value is False
    assert recognizer.recognize(checkbox(0.8)).value is True
    ambiguous = recognizer.recognize(checkbox(0.25))
    assert ambiguous.value is None
    assert ambiguous.reason_code == "AMBIGUOUS"
    assert ambiguous.accepted is False


def test_digit_margin_threshold_controls_abstention() -> None:
    image = digit_image(7)
    permissive = DigitRecognizer(margin_threshold=0.0).recognize_cell(image)
    conservative = DigitRecognizer(margin_threshold=1.0).recognize_cell(image)

    assert permissive.value == "7"
    assert permissive.accepted is True
    assert conservative.value is None
    assert conservative.accepted is False
    assert permissive.decision_score == conservative.decision_score
