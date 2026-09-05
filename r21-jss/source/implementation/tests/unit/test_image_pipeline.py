import cv2
import numpy as np

from app.adapters.recognition.opencv import FieldRegion, OpenCvImagePipeline


def checkerboard(size: int = 240) -> np.ndarray:
    image = np.full((size, size, 3), 255, dtype=np.uint8)
    step = 20
    for row in range(0, size, step):
        for column in range(0, size, step):
            if (row // step + column // step) % 2 == 0:
                image[row : row + step, column : column + step] = 0
    return image


def test_quality_detection_rejects_blur_and_accepts_sharp_content() -> None:
    pipeline = OpenCvImagePipeline(min_laplacian_variance=100.0)
    sharp = checkerboard()
    blurred = cv2.GaussianBlur(sharp, (31, 31), 0)

    assert pipeline.assess_quality(sharp).acceptable is True
    assessment = pipeline.assess_quality(blurred)
    assert assessment.acceptable is False
    assert "BLURRY" in assessment.reason_codes


def test_qr_code_is_the_primary_template_identifier() -> None:
    qr = cv2.QRCodeEncoder_create().encode("TEMPLATE-A:1")
    pipeline = OpenCvImagePipeline()

    assert pipeline.read_template_qr(qr) == "TEMPLATE-A:1"


def test_perspective_correction_and_field_crop_have_requested_dimensions() -> None:
    image = checkerboard(300)
    corners = np.float32([[20, 30], [280, 10], [290, 290], [10, 270]])
    pipeline = OpenCvImagePipeline()

    corrected = pipeline.correct_perspective(image, corners, width=200, height=100)
    crops = pipeline.crop_fields(
        corrected,
        [FieldRegion("total_quantity", x=10, y=20, width=50, height=30)],
    )

    assert corrected.shape == (100, 200, 3)
    assert crops["total_quantity"].shape == (30, 50, 3)


def test_aruco_detection_returns_ordered_page_corners() -> None:
    canvas = np.full((500, 700), 255, dtype=np.uint8)
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    placements = ((30, 30), (590, 30), (590, 390), (30, 390))
    for marker_id, (x, y) in zip((10, 11, 12, 13), placements, strict=True):
        marker = cv2.aruco.generateImageMarker(dictionary, marker_id, 80)
        canvas[y : y + 80, x : x + 80] = marker

    corners = OpenCvImagePipeline().detect_aruco_corners(canvas)

    assert corners.shape == (4, 2)
    assert np.allclose(corners, [[30, 30], [669, 30], [669, 469], [30, 469]], atol=2)
