import shutil

import cv2
import pytest

from benchmarks.baselines import AlwaysPredictBaseline, HogSvmBaseline, TesseractBaseline
from benchmarks.synthetic import render_digit


def test_always_predict_never_abstains() -> None:
    result = AlwaysPredictBaseline().predict(
        render_digit("3", font=cv2.FONT_HERSHEY_SIMPLEX, seed=1)
    )
    assert result.accepted is True


def test_hog_svm_rejects_an_undeclared_training_split() -> None:
    model = HogSvmBaseline(seed=7, declared_training_split="synthetic-train")
    with pytest.raises(ValueError, match="training split"):
        model.fit([], [], split_name="test")


def test_tesseract_reports_unavailable_without_executable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda _: None)
    adapter = TesseractBaseline()
    assert adapter.available is False
    assert adapter.version is None
