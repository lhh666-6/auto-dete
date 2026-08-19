"""Deterministic OpenCV image quality and geometry operations."""

from dataclasses import dataclass
from typing import cast

import cv2
import numpy as np
from numpy.typing import NDArray

Image = NDArray[np.uint8]


@dataclass(frozen=True, slots=True)
class QualityAssessment:
    acceptable: bool
    reason_codes: tuple[str, ...]
    laplacian_variance: float
    dark_ratio: float
    bright_ratio: float


@dataclass(frozen=True, slots=True)
class FieldRegion:
    field_id: str
    x: int
    y: int
    width: int
    height: int


class OpenCvImagePipeline:
    def __init__(
        self,
        *,
        min_laplacian_variance: float = 60.0,
        max_dark_ratio: float = 0.95,
        max_bright_ratio: float = 0.98,
    ) -> None:
        self._min_laplacian_variance = min_laplacian_variance
        self._max_dark_ratio = max_dark_ratio
        self._max_bright_ratio = max_bright_ratio

    def assess_quality(self, image: Image) -> QualityAssessment:
        self._require_image(image)
        gray = self._gray(image)
        variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        dark_ratio = float(np.mean(gray < 20))
        bright_ratio = float(np.mean(gray > 245))
        reasons: list[str] = []
        if variance < self._min_laplacian_variance:
            reasons.append("BLURRY")
        if dark_ratio > self._max_dark_ratio:
            reasons.append("TOO_DARK")
        if bright_ratio > self._max_bright_ratio:
            reasons.append("GLARE_OR_BLANK")
        return QualityAssessment(
            acceptable=not reasons,
            reason_codes=tuple(reasons),
            laplacian_variance=variance,
            dark_ratio=dark_ratio,
            bright_ratio=bright_ratio,
        )

    def read_template_qr(self, image: Image) -> str | None:
        self._require_image(image)
        candidate = image
        if min(image.shape[:2]) < 100:
            scale = max(4, 200 // min(image.shape[:2]))
            candidate = cast(
                Image,
                cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST),
            )
        value, _, _ = cv2.QRCodeDetector().detectAndDecode(candidate)
        return value or None

    def detect_aruco_corners(
        self,
        image: Image,
        *,
        marker_ids: tuple[int, int, int, int] = (10, 11, 12, 13),
    ) -> NDArray[np.float32]:
        """Return page corners ordered TL, TR, BR, BL from four ArUco markers."""
        self._require_image(image)
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        detector = cv2.aruco.ArucoDetector(dictionary)
        detected, ids, _ = detector.detectMarkers(self._gray(image))
        if ids is None:
            raise ValueError("required ArUco markers were not detected")
        by_id = {
            int(marker_id): np.asarray(corners, dtype=np.float32).reshape(4, 2)
            for corners, marker_id in zip(detected, ids.flatten(), strict=True)
        }
        missing = [marker_id for marker_id in marker_ids if marker_id not in by_id]
        if missing:
            raise ValueError(f"required ArUco markers missing: {missing}")
        page_corners = np.asarray(
            [by_id[marker_ids[index]][index] for index in range(4)], dtype=np.float32
        )
        return page_corners

    def correct_perspective(
        self,
        image: Image,
        corners: NDArray[np.float32],
        *,
        width: int,
        height: int,
    ) -> Image:
        self._require_image(image)
        source = np.asarray(corners, dtype=np.float32)
        if source.shape != (4, 2):
            raise ValueError("corners must contain top-left, top-right, bottom-right, bottom-left")
        target = np.asarray(
            [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
            dtype=np.float32,
        )
        transform = cv2.getPerspectiveTransform(source, target)
        return cast(Image, cv2.warpPerspective(image, transform, (width, height)))

    def crop_fields(self, image: Image, regions: list[FieldRegion]) -> dict[str, Image]:
        self._require_image(image)
        image_height, image_width = image.shape[:2]
        crops: dict[str, Image] = {}
        for region in regions:
            if (
                region.x < 0
                or region.y < 0
                or region.width <= 0
                or region.height <= 0
                or region.x + region.width > image_width
                or region.y + region.height > image_height
            ):
                raise ValueError(f"Field region outside image: {region.field_id}")
            crops[region.field_id] = image[
                region.y : region.y + region.height,
                region.x : region.x + region.width,
            ].copy()
        return crops

    @staticmethod
    def _gray(image: Image) -> Image:
        return image if image.ndim == 2 else cast(Image, cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))

    @staticmethod
    def _require_image(image: Image) -> None:
        if image.size == 0 or image.ndim not in (2, 3):
            raise ValueError("A non-empty grayscale or BGR image is required")
