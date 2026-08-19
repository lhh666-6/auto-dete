import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from numpy.typing import NDArray
from sklearn.svm import LinearSVC  # type: ignore[import-untyped]

from app.adapters.recognition.digits import DigitRecognizer
from benchmarks.synthetic import render_digit

Image = NDArray[np.uint8]


@dataclass(frozen=True, slots=True)
class BaselinePrediction:
    value: str | None
    accepted: bool
    score: float


class AlwaysPredictBaseline:
    name = "always-predict-template"

    def __init__(self) -> None:
        self._recognizer = DigitRecognizer(margin_threshold=0.0)

    def predict(self, image: Image) -> BaselinePrediction:
        candidate = self._recognizer.recognize_cell(image)
        return BaselinePrediction(
            value=candidate.value,
            accepted=True,
            score=float(candidate.decision_score or 0.0),
        )


class HogSvmBaseline:
    name = "hog-linear-svm"

    def __init__(self, *, seed: int, declared_training_split: str) -> None:
        self._declared_training_split = declared_training_split
        self._model = LinearSVC(random_state=seed, dual="auto")
        self._fitted = False
        self._hog = cv2.HOGDescriptor((48, 64), (16, 16), (8, 8), (8, 8), 9)

    def _features(self, image: Image) -> NDArray[np.float32]:
        gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (48, 64), interpolation=cv2.INTER_AREA)
        computed = np.asarray(self._hog.compute(resized), dtype=np.float32)
        return computed.reshape(-1)

    def fit(self, images: list[Image], labels: list[str], *, split_name: str) -> None:
        if split_name != self._declared_training_split:
            raise ValueError("training split does not match the declared training split")
        if not images or len(images) != len(labels):
            raise ValueError("training images and labels must be non-empty and equally sized")
        features = np.stack([self._features(image) for image in images])
        self._model.fit(features, labels)
        self._fitted = True

    def predict(self, image: Image) -> BaselinePrediction:
        if not self._fitted:
            raise RuntimeError("HOG+SVM baseline must be fitted before prediction")
        features = self._features(image).reshape(1, -1)
        value = str(self._model.predict(features)[0])
        scores = np.sort(np.asarray(self._model.decision_function(features)).reshape(-1))
        margin = float(scores[-1] - scores[-2]) if scores.size > 1 else float(scores[-1])
        return BaselinePrediction(value=value, accepted=True, score=margin)


def fit_hog_svm(
    training_seeds: list[int], font_names: list[str], *, seed: int = 17
) -> HogSvmBaseline:
    """Fit the shared HOG-SVM used by cell and whole-form experiments."""
    model = HogSvmBaseline(seed=seed, declared_training_split="synthetic-train")
    images: list[Image] = []
    labels: list[str] = []
    for training_seed in training_seeds:
        for font_name in font_names:
            font = getattr(cv2, font_name, None)
            if not isinstance(font, int):
                raise ValueError(f"unknown OpenCV font: {font_name}")
            for digit in [str(value) for value in range(10)]:
                images.append(
                    render_digit(digit, font=font, seed=training_seed + int(digit))
                )
                labels.append(digit)
    model.fit(images, labels, split_name="synthetic-train")
    return model


class TesseractBaseline:
    name = "tesseract-psm10"

    def __init__(self) -> None:
        executable = shutil.which("tesseract")
        self._executable = Path(executable) if executable else None
        self.version: str | None = None
        if self._executable is not None:
            completed = subprocess.run(
                [str(self._executable), "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if completed.returncode == 0:
                self.version = completed.stdout.splitlines()[0].strip()

    @property
    def available(self) -> bool:
        return self._executable is not None and self.version is not None

    def predict(self, image: Image) -> BaselinePrediction:
        if not self.available or self._executable is None:
            return BaselinePrediction(value=None, accepted=False, score=0.0)
        ok, encoded = cv2.imencode(".png", image)
        if not ok:
            raise RuntimeError("could not encode Tesseract input")
        completed = subprocess.run(
            [
                str(self._executable),
                "stdin",
                "stdout",
                "--psm",
                "10",
                "-c",
                "tessedit_char_whitelist=0123456789",
            ],
            input=encoded.tobytes(),
            check=False,
            capture_output=True,
            timeout=20,
        )
        text = completed.stdout.decode(errors="ignore").strip()
        digit = next((character for character in text if character.isdigit()), None)
        return BaselinePrediction(
            value=digit, accepted=digit is not None, score=1.0 if digit else 0.0
        )
