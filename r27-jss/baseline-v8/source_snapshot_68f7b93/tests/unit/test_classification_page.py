import cv2
import numpy as np
import pytest

from app.ui.pages.classification import InvalidImageError, decode_image


def test_decode_image_returns_bgr_pixels() -> None:
    source = np.full((20, 30, 3), (10, 20, 30), dtype=np.uint8)
    encoded, buffer = cv2.imencode(".png", source)
    assert encoded

    restored = decode_image(buffer.tobytes())
    assert restored.shape == (20, 30, 3)


def test_decode_image_rejects_non_image_bytes() -> None:
    with pytest.raises(InvalidImageError):
        decode_image(b"not-an-image")
