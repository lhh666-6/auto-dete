from dataclasses import dataclass
from typing import Any, cast

import cv2
import numpy as np
from numpy.typing import NDArray

Image = NDArray[np.uint8]
Region = tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class SyntheticForm:
    image: Image
    template_reference: str
    digit_labels: tuple[str, ...]
    omr_labels: tuple[bool, ...]
    field_regions: tuple[Region, ...]


def render_digit(value: str, *, font: int, seed: int) -> Image:
    if len(value) != 1 or value not in "0123456789":
        raise ValueError("value must be one decimal digit")
    rng = np.random.default_rng(seed)
    image = np.full((64, 48), 255, dtype=np.uint8)
    scale = float(rng.uniform(1.65, 1.90))
    thickness = int(rng.integers(2, 4))
    x = int(rng.integers(4, 8))
    y = int(rng.integers(50, 56))
    cv2.putText(image, value, (x, y), font, scale, (0,), thickness, cv2.LINE_AA)
    return image


def render_omr(value: bool, *, seed: int) -> Image:
    rng = np.random.default_rng(seed)
    image = np.full((60, 60), 255, dtype=np.uint8)
    cv2.rectangle(image, (5, 5), (54, 54), 0, 2)
    if value:
        inset = int(rng.integers(10, 15))
        cv2.rectangle(image, (inset, inset), (59 - inset, 59 - inset), 0, -1)
    return image


def _qr_patch(payload: str, size: int) -> Image:
    factory = cast(Any, cv2).QRCodeEncoder_create
    encoder = factory()
    code = encoder.encode(payload)
    return cast(Image, cv2.resize(code, (size, size), interpolation=cv2.INTER_NEAREST))


def render_form(
    digit_values: list[str],
    omr_values: list[bool],
    *,
    seed: int,
    template_id: str = "AUTO-DECTE",
    template_version: str = "ESWA-V1",
    font: int = cv2.FONT_HERSHEY_SIMPLEX,
) -> SyntheticForm:
    if len(digit_values) != 10 or len(omr_values) != 10:
        raise ValueError("a synthetic form requires ten digit and ten OMR labels")
    if not template_id or not template_version or ":" in template_id:
        raise ValueError("template identity and version must define a QR reference")
    template_reference = f"{template_id}:{template_version}"
    image = np.full((1000, 700), 255, dtype=np.uint8)
    image[70:170, 300:400] = _qr_patch(template_reference, 100)

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    placements = ((20, 20), (620, 20), (620, 920), (20, 920))
    for marker_id, (x, y) in zip((10, 11, 12, 13), placements, strict=True):
        marker = cv2.aruco.generateImageMarker(dictionary, marker_id, 60)
        image[y : y + 60, x : x + 60] = marker

    regions: list[Region] = []
    for index, digit_value in enumerate(digit_values):
        row, column = divmod(index, 5)
        x, y = 90 + column * 105, 250 + row * 115
        cell = render_digit(digit_value, font=font, seed=seed * 100 + index)
        image[y : y + 64, x : x + 48] = cell
        regions.append((x, y, 48, 64))
    for index, omr_value in enumerate(omr_values):
        row, column = divmod(index, 5)
        x, y = 85 + column * 105, 570 + row * 115
        cell = render_omr(omr_value, seed=seed * 100 + 50 + index)
        image[y : y + 60, x : x + 60] = cell
        regions.append((x, y, 60, 60))

    return SyntheticForm(
        image=image,
        template_reference=template_reference,
        digit_labels=tuple(digit_values),
        omr_labels=tuple(omr_values),
        field_regions=tuple(regions),
    )
