# Auto-Decte ESWA Experiments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible experiment package that measures selective recognition, perturbation robustness, trust-boundary fault resistance, resilience, and latency without using sensitive production records.

**Architecture:** Clone the public Auto-Decte repository below the paper source directory and add a self-contained `benchmarks` package. Each run produces immutable JSON/CSV artifacts plus a manifest containing the code commit, configuration, seeds, environment, and artifact hashes; paper plots and LaTeX tables are generated from those artifacts rather than typed manually.

**Tech Stack:** Python 3.11, uv, pytest, NumPy, OpenCV, SQLAlchemy/SQLite, Matplotlib, scikit-learn, optional local Tesseract, JSON/CSV, SHA-256.

---

## File Structure

Experiment repository: `D:\Claude_Design\auto-decte-paper\experiments\auto-decte`

- `benchmarks/schema.py`: typed benchmark rows, run manifests, and artifact metadata.
- `benchmarks/io.py`: deterministic JSON/CSV writing and SHA-256 manifest finalization.
- `benchmarks/synthetic.py`: seeded digit, OMR, and whole-form generation.
- `benchmarks/perturbations.py`: named, severity-controlled image transformations.
- `benchmarks/metrics.py`: coverage, selective risk, bootstrap intervals, and aggregation.
- `benchmarks/trust_faults.py`: application-path fault injection and invariant checks.
- `benchmarks/baselines.py`: always-predict, HOG+SVM, and optional Tesseract adapters.
- `benchmarks/run_recognition.py`: synthetic recognition and perturbation runner.
- `benchmarks/run_trust.py`: trust-boundary fault runner.
- `benchmarks/run_resilience.py`: AI-off, duplicate, replay, traceability, and latency runner.
- `benchmarks/render_paper_artifacts.py`: Trust Teal plots and generated LaTeX tables.
- `benchmarks/run_all.py`: deterministic orchestration and manifest completion.
- `benchmarks/config/eswa-v1.json`: frozen experiment grid and seeds.
- `tests/benchmarks/`: unit and integration tests for the benchmark package.
- `artifacts/eswa-v1/`: generated outputs; source of all manuscript numbers.
- `docs/eswa-reproducibility.md`: exact environment and rerun instructions.
- `docs/eswa-implementation-inventory.md`: reproducible map from manuscript claims to public code.

Paper repository changes:

- Modify `D:\Claude_Design\auto-decte-paper\.gitignore` to ignore the nested experiment clone.
- Copy finalized paper-facing files to `D:\Claude_Design\auto-decte-paper\eswa\artifacts\` during manuscript integration.

### Task 1: Create the isolated experiment checkout and establish a baseline

**Files:**
- Modify: `D:\Claude_Design\auto-decte-paper\.gitignore`
- Create by clone: `D:\Claude_Design\auto-decte-paper\experiments\auto-decte\`
- Modify: `pyproject.toml`

- [ ] **Step 1: Ignore the nested experiment checkout in the paper repository**

Add this exact line to the paper repository `.gitignore`:

```gitignore
experiments/auto-decte/
```

- [ ] **Step 2: Clone and branch without changing upstream `main`**

Run from `D:\Claude_Design\auto-decte-paper`:

```powershell
git clone https://github.com/lhh666-6/auto-decte.git experiments/auto-decte
Set-Location experiments/auto-decte
git switch -c codex/eswa-experiments
```

Expected: the active branch is `codex/eswa-experiments`; `main` remains unchanged.

- [ ] **Step 3: Run the public baseline quality gates**

```powershell
uv sync --extra dev
uv run python -m pytest -q
uv run ruff check .
uv run mypy app config
```

Expected: all three commands exit 0. If the baseline fails, record the exact failure and stop before adding benchmark code.

- [ ] **Step 4: Record the public implementation baseline before extending it**

Create `docs/eswa-implementation-inventory.md` from direct inspection and command output. It must record the actual UI/backend stack, current test count, implemented recognition entry points, missing or partial features, and every mismatch with the preserved LNCS prose. At minimum, resolve the current FastAPI/React/PWA, ArUco-detection, and “478 tests” claims. A claim is retained only if the checked-out code or a generated artifact supports it; otherwise mark it for removal from ESWA.

- [ ] **Step 5: Add research-only dependencies**

Replace the existing `[project.optional-dependencies]` block in `pyproject.toml` with:

```toml
[project.optional-dependencies]
dev = [
    "mypy>=1.11,<2",
    "pytest>=8.3,<10",
    "ruff>=0.6,<1",
    "types-openpyxl>=3.1.5.20260518",
]
research = [
    "matplotlib>=3.9,<4",
    "scikit-learn>=1.5,<2",
]
```

Run `uv lock` and `uv sync --extra dev --extra research`. Expected: exit 0.

- [ ] **Step 6: Commit the experiment environment and inventory**

```powershell
git add pyproject.toml uv.lock docs/eswa-implementation-inventory.md
git commit -m "build: add reproducible research dependencies"
```

### Task 2: Add typed artifact schemas and deterministic writers

**Files:**
- Create: `benchmarks/__init__.py`
- Create: `benchmarks/schema.py`
- Create: `benchmarks/io.py`
- Create: `tests/benchmarks/test_artifact_io.py`

- [ ] **Step 1: Write the failing artifact round-trip test**

Create `tests/benchmarks/test_artifact_io.py`:

```python
import json
from pathlib import Path

from benchmarks.io import write_json
from benchmarks.schema import PredictionRow


def test_json_artifact_is_stable_and_contains_typed_fields(tmp_path: Path) -> None:
    row = PredictionRow(
        case_id="seed-7-digit-3-clean",
        seed=7,
        target="3",
        prediction="3",
        accepted=True,
        score=0.12,
        perturbation="clean",
        severity=0.0,
        latency_ms=1.25,
    )
    target = tmp_path / "predictions.json"
    digest = write_json(target, [row])
    payload = json.loads(target.read_text(encoding="utf-8"))

    assert payload[0]["case_id"] == "seed-7-digit-3-clean"
    assert payload[0]["accepted"] is True
    assert len(digest) == 64
```

- [ ] **Step 2: Run the test to verify it fails**

Run `uv run pytest tests/benchmarks/test_artifact_io.py -q`.

Expected: FAIL because `benchmarks.io` does not exist.

- [ ] **Step 3: Implement typed rows and stable JSON output**

Create `benchmarks/schema.py`:

```python
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PredictionRow:
    case_id: str
    seed: int
    target: str
    prediction: str | None
    accepted: bool
    score: float
    perturbation: str
    severity: float
    latency_ms: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    relative_path: str
    sha256: str
    rows: int
```

Create `benchmarks/io.py`:

```python
import hashlib
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    return value


def write_json(path: Path, rows: Iterable[Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [_jsonable(row) for row in rows]
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(encoded)
    return hashlib.sha256(encoded).hexdigest()
```

Create an empty `benchmarks/__init__.py`.

- [ ] **Step 4: Run tests and static checks**

```powershell
uv run pytest tests/benchmarks/test_artifact_io.py -q
uv run ruff check benchmarks tests/benchmarks
uv run mypy benchmarks
```

Expected: all commands exit 0.

- [ ] **Step 5: Commit**

```powershell
git add benchmarks tests/benchmarks
git commit -m "feat: add deterministic benchmark artifact schema"
```

### Task 3: Build seeded synthetic generators and perturbations

**Files:**
- Create: `benchmarks/synthetic.py`
- Create: `benchmarks/perturbations.py`
- Create: `tests/benchmarks/test_synthetic.py`

- [ ] **Step 1: Write deterministic generation tests**

Create `tests/benchmarks/test_synthetic.py`:

```python
import numpy as np

from benchmarks.perturbations import apply_perturbation
from benchmarks.synthetic import render_digit, render_omr


def test_digit_generation_is_seeded() -> None:
    first = render_digit("7", font=cv2_font(), seed=13)
    second = render_digit("7", font=cv2_font(), seed=13)
    assert np.array_equal(first, second)


def test_noise_severity_zero_is_identity() -> None:
    image = render_digit("4", font=cv2_font(), seed=3)
    changed = apply_perturbation(image, "gaussian_noise", 0.0, seed=99)
    assert np.array_equal(image, changed)


def test_omr_labels_have_distinct_fill() -> None:
    unchecked = render_omr(False, seed=1)
    checked = render_omr(True, seed=1)
    assert float(np.mean(checked < 128)) > float(np.mean(unchecked < 128))


def cv2_font() -> int:
    import cv2

    return cv2.FONT_HERSHEY_SIMPLEX
```

- [ ] **Step 2: Run to verify failure**

Run `uv run pytest tests/benchmarks/test_synthetic.py -q`.

Expected: FAIL because the generator modules do not exist.

- [ ] **Step 3: Implement the seeded cell generators**

Create `benchmarks/synthetic.py` with these public functions:

```python
import cv2
import numpy as np
from numpy.typing import NDArray

Image = NDArray[np.uint8]


def render_digit(value: str, *, font: int, seed: int) -> Image:
    rng = np.random.default_rng(seed)
    image = np.full((64, 48), 255, dtype=np.uint8)
    scale = float(rng.uniform(1.65, 1.90))
    thickness = int(rng.integers(2, 4))
    x = int(rng.integers(4, 8))
    y = int(rng.integers(50, 56))
    cv2.putText(image, value, (x, y), font, scale, 0, thickness, cv2.LINE_AA)
    return image


def render_omr(value: bool, *, seed: int) -> Image:
    rng = np.random.default_rng(seed)
    image = np.full((60, 60), 255, dtype=np.uint8)
    cv2.rectangle(image, (5, 5), (54, 54), 0, 2)
    if value:
        inset = int(rng.integers(10, 15))
        cv2.rectangle(image, (inset, inset), (59 - inset, 59 - inset), 0, -1)
    return image
```

Also define `SyntheticForm(image, digit_labels, omr_labels, field_regions)` and `render_form(digit_values, omr_values, seed)`. The form renderer must place a QR code containing template identity, four visually distinct corner fiducials, ten digit cells, and ten OMR cells on a canonical white canvas and return exact field rectangles with the labels. Add a test that the returned region count equals the label count and all regions lie within the image.

- [ ] **Step 4: Implement named perturbations with declared severity ranges**

Create `benchmarks/perturbations.py` with `clean`, `gaussian_blur`, `gaussian_noise`, `brightness`, `rotation`, `perspective`, `jpeg`, and `occlusion`. The dispatch must reject unknown names and must return an identical copy when severity is zero:

```python
import cv2
import numpy as np
from numpy.typing import NDArray

Image = NDArray[np.uint8]


def apply_perturbation(image: Image, name: str, severity: float, *, seed: int) -> Image:
    if not 0.0 <= severity <= 1.0:
        raise ValueError("severity must be in [0, 1]")
    if severity == 0.0 or name == "clean":
        return image.copy()
    rng = np.random.default_rng(seed)
    if name == "gaussian_blur":
        radius = 1 + 2 * int(round(3 * severity))
        return cv2.GaussianBlur(image, (radius, radius), 0)
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
        return cv2.warpAffine(image, matrix, (image.shape[1], image.shape[0]), borderValue=255)
    if name == "jpeg":
        quality = max(20, int(round(100 - 75 * severity)))
        ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not ok:
            raise RuntimeError("JPEG encoding failed")
        decoded = cv2.imdecode(encoded, cv2.IMREAD_GRAYSCALE)
        if decoded is None:
            raise RuntimeError("JPEG decoding failed")
        return decoded
    if name == "occlusion":
        result = image.copy()
        width = max(1, int(round(image.shape[1] * 0.25 * severity)))
        start = int(rng.integers(0, max(1, image.shape[1] - width + 1)))
        result[:, start : start + width] = 255
        return result
    if name == "perspective":
        h, w = image.shape[:2]
        delta = float(min(h, w) * 0.12 * severity)
        source = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
        target = np.float32([[delta, 0], [w - 1, delta], [w - 1 - delta, h - 1], [0, h - 1 - delta]])
        matrix = cv2.getPerspectiveTransform(source, target)
        return cv2.warpPerspective(image, matrix, (w, h), borderValue=255)
    raise ValueError(f"Unknown perturbation: {name}")
```

- [ ] **Step 5: Verify and commit**

Run the targeted tests, Ruff, and mypy. Expected: exit 0.

```powershell
git add benchmarks/synthetic.py benchmarks/perturbations.py tests/benchmarks/test_synthetic.py
git commit -m "feat: add seeded synthetic document perturbations"
```

### Task 4: Close recognition instrumentation gaps

**Files:**
- Modify: `app/adapters/recognition/digits.py`
- Modify: `app/adapters/recognition/candidate.py`
- Modify: `app/adapters/recognition/opencv.py`
- Modify: `tests/unit/test_digit_and_omr.py`
- Modify: `tests/unit/test_image_pipeline.py`

- [ ] **Step 1: Add a failing threshold-behavior test**

Append to `tests/unit/test_digit_and_omr.py`:

```python
def test_digit_margin_threshold_controls_abstention() -> None:
    image = digit_image(7)
    permissive = DigitRecognizer(margin_threshold=0.0).recognize_cell(image)
    conservative = DigitRecognizer(margin_threshold=1.0).recognize_cell(image)

    assert permissive.value == "7"
    assert permissive.accepted is True
    assert conservative.value is None
    assert conservative.accepted is False
    assert permissive.decision_score == conservative.decision_score
```

- [ ] **Step 2: Run to verify failure**

Run `uv run pytest tests/unit/test_digit_and_omr.py::test_digit_margin_threshold_controls_abstention -q`.

Expected: FAIL because the candidate has no `accepted` or `decision_score` fields and the recognizer has no threshold argument.

- [ ] **Step 3: Extend the candidate contract without breaking existing callers**

Add defaulted fields to `RecognitionCandidate`:

```python
@dataclass(frozen=True, slots=True)
class RecognitionCandidate(Generic[T]):
    value: T | None
    confidence: float
    engine: str
    model_version: str
    reason_code: str
    accepted: bool = True
    decision_score: float | None = None
```

Update `DigitRecognizer.__init__` to accept `margin_threshold: float = 0.02`, reject negative values, store it, and return `value=None`, `accepted=False`, `reason_code="AMBIGUOUS"`, and `decision_score=margin` when the margin is below the threshold. Preserve the top-class score through `decision_score` in accepted cases.

Update `OmrRecognizer` so unchecked and checked candidates set `accepted=True`, while the ambiguity band sets `accepted=False`. Extend the OMR unit test to assert these flags.

- [ ] **Step 4: Add and verify an explicit fiducial-detection entry point**

Before claiming ArUco detection in the journal paper, add a failing unit test that renders markers 10--13 from `DICT_4X4_50`, places them in the four canvas corners, and expects `OpenCvImagePipeline.detect_aruco_corners()` to return four ordered page corners. Implement the method with `cv2.aruco.ArucoDetector`; if the installed OpenCV build lacks `aruco`, replace `opencv-python-headless` with the version-matched `opencv-contrib-python-headless` package and regenerate `uv.lock`. If this test cannot be made reproducible, remove ArUco detection from the ESWA method and inventory rather than retaining an unimplemented claim.

- [ ] **Step 5: Verify compatibility**

```powershell
uv run pytest tests/unit/test_digit_and_omr.py tests/integration/test_recognition_attempts.py -q
uv run ruff check app/adapters/recognition tests/unit/test_digit_and_omr.py
uv run mypy app
```

Expected: all commands exit 0.

- [ ] **Step 6: Commit**

```powershell
git add app/adapters/recognition tests/unit/test_digit_and_omr.py
git commit -m "feat: expose configurable selective digit decisions"
```

### Task 5: Implement selective metrics and bootstrap intervals

**Files:**
- Create: `benchmarks/metrics.py`
- Create: `tests/benchmarks/test_metrics.py`

- [ ] **Step 1: Write tests with analytically known metrics**

Create `tests/benchmarks/test_metrics.py`:

```python
from benchmarks.metrics import selective_metrics


def test_selective_metrics_use_accepted_denominator() -> None:
    result = selective_metrics(
        correct=[True, False, True, False],
        accepted=[True, True, False, False],
    )
    assert result.total == 4
    assert result.accepted == 2
    assert result.coverage == 0.5
    assert result.accepted_accuracy == 0.5
    assert result.selective_risk == 0.5
    assert result.erroneous_auto_pass_rate == 0.25
    assert result.routing_rate == 0.5
```

- [ ] **Step 2: Run to verify failure**

Run `uv run pytest tests/benchmarks/test_metrics.py -q`.

Expected: FAIL because `benchmarks.metrics` does not exist.

- [ ] **Step 3: Implement the metric contract**

Create `benchmarks/metrics.py`:

```python
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class SelectiveMetrics:
    total: int
    accepted: int
    coverage: float
    accepted_accuracy: float
    selective_risk: float
    erroneous_auto_pass_rate: float
    routing_rate: float


def selective_metrics(*, correct: Sequence[bool], accepted: Sequence[bool]) -> SelectiveMetrics:
    if len(correct) != len(accepted) or not correct:
        raise ValueError("correct and accepted must be non-empty and equally sized")
    total = len(correct)
    accepted_count = sum(accepted)
    accepted_correct = sum(ok and use for ok, use in zip(correct, accepted, strict=True))
    accepted_errors = accepted_count - accepted_correct
    accepted_accuracy = accepted_correct / accepted_count if accepted_count else 0.0
    return SelectiveMetrics(
        total=total,
        accepted=accepted_count,
        coverage=accepted_count / total,
        accepted_accuracy=accepted_accuracy,
        selective_risk=1.0 - accepted_accuracy if accepted_count else 0.0,
        erroneous_auto_pass_rate=accepted_errors / total,
        routing_rate=1.0 - accepted_count / total,
    )
```

Add a `bootstrap_interval(values, statistic, seed, replicates=2000)` helper using `numpy.random.default_rng(seed)` and percentile bounds `[2.5, 97.5]`. Test identical values produce a degenerate interval.

- [ ] **Step 4: Verify and commit**

Run targeted tests, Ruff, and mypy. Expected: exit 0.

```powershell
git add benchmarks/metrics.py tests/benchmarks/test_metrics.py
git commit -m "feat: add selective-risk metrics and confidence intervals"
```

### Task 6: Add trust-boundary fault injection

**Files:**
- Create: `benchmarks/trust_faults.py`
- Create: `benchmarks/run_trust.py`
- Create: `tests/benchmarks/test_trust_faults.py`

- [ ] **Step 1: Write a failing machine-path isolation test**

Create `tests/benchmarks/test_trust_faults.py`:

```python
from pathlib import Path

from benchmarks.trust_faults import run_fault_matrix


def test_machine_faults_do_not_change_confirmed_fact(tmp_path: Path) -> None:
    outcomes = run_fault_matrix(tmp_path)
    assert {item.fault for item in outcomes} == {
        "wrong_recognition",
        "wrong_llm_suggestion",
        "irrelevant_retrieval",
        "stale_human_replay",
        "duplicate_evidence",
    }
    assert all(item.fact_unchanged for item in outcomes if item.machine_originated)
    assert all(item.audit_complete for item in outcomes)
```

- [ ] **Step 2: Run to verify failure**

Run `uv run pytest tests/benchmarks/test_trust_faults.py -q`.

Expected: FAIL because the fault matrix does not exist.

- [ ] **Step 3: Implement the fault outcome contract**

In `benchmarks/trust_faults.py`, define:

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FaultOutcome:
    fault: str
    machine_originated: bool
    fact_unchanged: bool
    audit_complete: bool
    expected_exception: str | None
```

`run_fault_matrix(root)` must create a fresh SQLite database for every case, confirm one human fact, snapshot all `RecordVersion` rows, invoke the existing recognition, AI-review, retrieval, import, or stale-review path, and compare the post-fault versions with the snapshot. The stale human replay must expect `ConcurrentReviewError`; duplicate evidence must expect the existing duplicate rejection. Do not directly mutate SQL rows because the paper claim concerns exposed application paths, not resistance to a database administrator.

- [ ] **Step 4: Add a JSON-producing CLI**

`benchmarks/run_trust.py` must accept `--output`, run the matrix inside a temporary working directory, serialize every `FaultOutcome`, and exit nonzero if a machine-originated case changes a fact or any case loses required audit lineage.

- [ ] **Step 5: Verify and commit**

```powershell
uv run pytest tests/benchmarks/test_trust_faults.py tests/integration/test_ai_review_persistence.py tests/unit/test_review_service.py -q
uv run python -m benchmarks.run_trust --output artifacts/eswa-v1/trust_faults.json
git add benchmarks tests/benchmarks/test_trust_faults.py
git commit -m "test: add trust-boundary fault injection matrix"
```

Expected: tests and CLI exit 0; the JSON contains five named outcomes.

### Task 7: Add baselines and the recognition runner

**Files:**
- Create: `benchmarks/baselines.py`
- Create: `benchmarks/run_recognition.py`
- Create: `benchmarks/config/eswa-v1.json`
- Create: `tests/benchmarks/test_baselines.py`
- Create: `tests/benchmarks/test_recognition_runner.py`

- [ ] **Step 1: Freeze the experiment grid**

Create `benchmarks/config/eswa-v1.json` with seeds `[101, 202, 303, 404, 505]`, digits `0` through `9`, fonts `FONT_HERSHEY_SIMPLEX`, `FONT_HERSHEY_DUPLEX`, and `FONT_HERSHEY_COMPLEX`, `clean` at severity `0.0`, the perturbations `gaussian_blur`, `gaussian_noise`, `brightness`, `rotation`, `perspective`, `jpeg`, and `occlusion` at severities `[0.25, 0.5, 0.75, 1.0]`, and thresholds from `0.0` through `0.10` in increments of `0.005`.

- [ ] **Step 2: Write baseline contract tests**

Test that the always-predict adapter never abstains; the HOG+SVM adapter fits only its declared training split; and the Tesseract adapter returns `available=False` rather than fabricating a result when `tesseract --version` is unavailable.

- [ ] **Step 3: Implement the baselines**

`benchmarks/baselines.py` must expose `AlwaysPredictBaseline`, `HogSvmBaseline`, and `TesseractBaseline`. Use `skimage`-free HOG through `cv2.HOGDescriptor` and `sklearn.svm.LinearSVC(random_state=seed)`. Invoke Tesseract using `subprocess.run` with `--psm 10` and a digit whitelist; record the executable version in metadata.

- [ ] **Step 4: Implement the runner**

`run_recognition.py` must load the frozen JSON config, generate every case deterministically, execute the Auto-Decte recognizer and available baselines, time each call with `time.perf_counter_ns`, and write raw prediction rows before any aggregation. It must then compute threshold sweeps and bootstrap intervals from raw rows.

- [ ] **Step 5: Verify a reduced smoke configuration**

Run a test configuration containing two digits, one seed, two perturbations, and two thresholds. Assert the exact raw-row count equals the Cartesian product and that rerunning produces identical predictions and metrics, excluding latency fields.

- [ ] **Step 6: Commit**

```powershell
uv run pytest tests/benchmarks/test_baselines.py tests/benchmarks/test_recognition_runner.py -q
git add benchmarks tests/benchmarks
git commit -m "feat: add reproducible recognition baselines and runner"
```

### Task 8: Add resilience, latency, plots, tables, and the master run

**Files:**
- Create: `benchmarks/run_resilience.py`
- Create: `benchmarks/render_paper_artifacts.py`
- Create: `benchmarks/run_all.py`
- Create: `tests/benchmarks/test_rendering.py`
- Create: `docs/eswa-reproducibility.md`
- Generate: `artifacts/eswa-v1/`

- [ ] **Step 1: Implement operational checks**

`run_resilience.py` must measure AI-disabled completion, duplicate import rejection, stale-version rejection, export reverse trace, and warm/cold latency. Record environment, hardware summary, repetitions, median, interquartile range, and 95th percentile. Use a minimum of 30 timed repetitions after five warm-up calls.

- [ ] **Step 2: Implement Trust Teal paper rendering**

Use these constants in `render_paper_artifacts.py`:

```python
TEAL = "#16796F"
CHARCOAL = "#243746"
AMBER = "#C06B19"
PALE_TEAL = "#E1F2EF"
PALE_AMBER = "#FFF0DC"
```

Generate vector PDF/SVG plots for coverage--risk, robustness by perturbation severity, fault outcomes, and latency distributions. Different series must also use distinct markers or line styles. Generate booktabs LaTeX tables from JSON summaries with aligned decimal columns.

- [ ] **Step 3: Test rendering from a fixed miniature fixture**

The test must render into `tmp_path`, assert every expected PDF/SVG/TEX file exists and is non-empty, and verify the LaTeX table contains `\\toprule`, `\\midrule`, and `\\bottomrule` but no vertical `|` column rules.

- [ ] **Step 4: Implement the master orchestrator and manifest**

`run_all.py` must run trust, recognition, resilience, and rendering in order; stop on any nonzero child status; record the current Git commit, dirty state, Python and dependency versions, config SHA-256, seeds, commands, artifact hashes, and start/end timestamps in `artifacts/eswa-v1/manifest.json`.

- [ ] **Step 5: Execute the full experiment package**

```powershell
uv run python -m benchmarks.run_all --config benchmarks/config/eswa-v1.json --output artifacts/eswa-v1
uv run python -m pytest -q
uv run ruff check .
uv run mypy app config benchmarks
```

Expected: every command exits 0; `manifest.json` reports a clean experiment commit; every manuscript-facing number has a raw or summarized artifact.

- [ ] **Step 6: Write reproducibility instructions and commit**

Document exact Windows and cross-platform commands, optional Tesseract behavior, expected artifact names, and the data-sensitivity boundary in `docs/eswa-reproducibility.md`.

```powershell
git add benchmarks tests/benchmarks docs/eswa-reproducibility.md pyproject.toml uv.lock artifacts/eswa-v1
git commit -m "research: publish ESWA reproducibility package"
```

### Task 9: Copy the verified paper-facing artifacts into the paper source directory

**Files:**
- Create: `D:\Claude_Design\auto-decte-paper\eswa\artifacts\manifest.json`
- Create: `D:\Claude_Design\auto-decte-paper\eswa\artifacts\results\`
- Create: `D:\Claude_Design\auto-decte-paper\eswa\figures\generated\`
- Create: `D:\Claude_Design\auto-decte-paper\eswa\tables\generated\`

- [ ] **Step 1: Verify the experiment repository is clean**

Run `git status --short` and `git log -1 --oneline` in the experiment repository. Expected: no status output and a recorded experiment commit.

- [ ] **Step 2: Copy only manifest-listed artifacts**

Use the manifest as the allow-list. Copy JSON/CSV summaries, vector plots, and LaTeX tables to their corresponding paper directories. Do not copy raw sensitive data because none is used; do not copy virtual environments or temporary images.

- [ ] **Step 3: Verify hashes after copying**

Recompute SHA-256 for every copied file and compare with `manifest.json`. Expected: zero mismatches.

- [ ] **Step 4: Commit the paper-facing experiment evidence on the paper branch**

```powershell
git add eswa/artifacts eswa/figures/generated eswa/tables/generated
git commit -m "research: add verified ESWA experiment artifacts"
```
