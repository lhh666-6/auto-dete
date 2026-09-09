import cv2
import numpy as np

from benchmarks.perturbations import apply_perturbation
from benchmarks.synthetic import render_digit, render_form, render_omr


def test_digit_generation_is_seeded() -> None:
    first = render_digit("7", font=cv2.FONT_HERSHEY_SIMPLEX, seed=13)
    second = render_digit("7", font=cv2.FONT_HERSHEY_SIMPLEX, seed=13)
    assert np.array_equal(first, second)


def test_noise_severity_zero_is_identity() -> None:
    image = render_digit("4", font=cv2.FONT_HERSHEY_SIMPLEX, seed=3)
    changed = apply_perturbation(image, "gaussian_noise", 0.0, seed=99)
    assert np.array_equal(image, changed)
    assert changed is not image


def test_omr_labels_have_distinct_fill() -> None:
    unchecked = render_omr(False, seed=1)
    checked = render_omr(True, seed=1)
    assert float(np.mean(checked < 128)) > float(np.mean(unchecked < 128))


def test_form_regions_match_labels_and_are_inside_canvas() -> None:
    form = render_form([str(i) for i in range(10)], [i % 2 == 0 for i in range(10)], seed=7)
    assert len(form.field_regions) == len(form.digit_labels) + len(form.omr_labels)
    height, width = form.image.shape[:2]
    for x, y, region_width, region_height in form.field_regions:
        assert 0 <= x < x + region_width <= width
        assert 0 <= y < y + region_height <= height


def test_form_renderer_supports_declared_template_variants() -> None:
    values = [str(i) for i in range(10)]
    omr = [i % 2 == 0 for i in range(10)]
    first = render_form(
        values,
        omr,
        seed=7,
        template_id="TEMPLATE-A",
        template_version="1",
        font=cv2.FONT_HERSHEY_SIMPLEX,
    )
    second = render_form(
        values,
        omr,
        seed=7,
        template_id="TEMPLATE-B",
        template_version="2",
        font=cv2.FONT_HERSHEY_DUPLEX,
    )

    detector = cv2.QRCodeDetector()
    assert detector.detectAndDecode(first.image)[0] == "TEMPLATE-A:1"
    assert detector.detectAndDecode(second.image)[0] == "TEMPLATE-B:2"
    assert first.template_reference == "TEMPLATE-A:1"
    assert second.template_reference == "TEMPLATE-B:2"
    assert not np.array_equal(first.image, second.image)


def test_unknown_perturbation_is_rejected() -> None:
    image = render_digit("1", font=cv2.FONT_HERSHEY_SIMPLEX, seed=1)
    with np.testing.assert_raises_regex(ValueError, "Unknown perturbation"):
        apply_perturbation(image, "invented", 0.5, seed=1)
