from typing import cast

import cv2
import numpy as np
from numpy.typing import NDArray

Image = NDArray[np.uint8]


def apply_perturbation(image: Image, name: str, severity: float, *, seed: int) -> Image:
    if not 0.0 <= severity <= 1.0:
        raise ValueError("severity must be in [0, 1]")
    if name == "clean" or severity == 0.0:
        return image.copy()
    rng = np.random.default_rng(seed)
    if name == "gaussian_blur":
        radius = 1 + 2 * int(round(3 * severity))
        return cast(Image, cv2.GaussianBlur(image, (radius, radius), 0))
    if name == "gaussian_noise":
        noise = rng.normal(0.0, 35.0 * severity, image.shape)
        return np.clip(image.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    if name == "brightness":
        factor = 1.0 - 0.65 * severity
        return np.clip(image.astype(np.float32) * factor, 0, 255).astype(np.uint8)
    if name == "rotation":
        angle = 7.0 * severity
        center = (image.shape[1] / 2.0, image.shape[0] / 2.0)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cast(
            Image,
            cv2.warpAffine(image, matrix, (image.shape[1], image.shape[0]), borderValue=(255,)),
        )
    if name == "jpeg":
        quality = max(20, int(round(100 - 75 * severity)))
        ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not ok:
            raise RuntimeError("JPEG encoding failed")
        decoded = cv2.imdecode(encoded, cv2.IMREAD_GRAYSCALE)
        if decoded is None:
            raise RuntimeError("JPEG decoding failed")
        return cast(Image, decoded)
    if name == "occlusion":
        result = image.copy()
        width = max(1, int(round(image.shape[1] * 0.25 * severity)))
        start = int(rng.integers(0, max(1, image.shape[1] - width + 1)))
        result[:, start : start + width] = 255
        return result
    if name == "perspective":
        height, width = image.shape[:2]
        delta = float(min(height, width) * 0.12 * severity)
        source = np.asarray(
            [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
            dtype=np.float32,
        )
        target = np.asarray(
            [
                [delta, 0],
                [width - 1, delta],
                [width - 1 - delta, height - 1],
                [0, height - 1 - delta],
            ],
            dtype=np.float32,
        )
        matrix = cv2.getPerspectiveTransform(source, target)
        return cast(
            Image,
            cv2.warpPerspective(image, matrix, (width, height), borderValue=(255,)),
        )
    raise ValueError(f"Unknown perturbation: {name}")
