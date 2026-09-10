import argparse
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np

from app.adapters.recognition.omr import OmrRecognizer
from app.adapters.recognition.opencv import FieldRegion, OpenCvImagePipeline
from benchmarks.baselines import HogSvmBaseline, fit_hog_svm
from benchmarks.form_workflow import FormWorkflowOutcome, run_synthetic_form_workflow
from benchmarks.io import write_json
from benchmarks.perturbations import apply_perturbation
from benchmarks.synthetic import Image, SyntheticForm, render_form


@dataclass(frozen=True, slots=True)
class FormBenchmarkRun:
    base_form_count: int
    evaluation_form_count: int
    raw_row_count: int
    workflow_count: int


@dataclass(frozen=True, slots=True)
class FormOutcome:
    base_form_id: str
    seed: int
    split: str
    template_reference: str
    condition: str
    severity: float
    variant: str
    template_identified: bool
    alignment_succeeded: bool
    digit_fields: int
    digit_accepted: int
    digit_correct: int
    omr_fields: int
    omr_accepted: int
    omr_correct: int
    complete_form_correct: bool


def _font(name: str) -> int:
    value = getattr(cv2, name, None)
    if not isinstance(value, int):
        raise ValueError(f"unknown OpenCV font: {name}")
    return value


def _labels(seed: int, template_index: int) -> tuple[list[str], list[bool]]:
    rng = np.random.default_rng(seed * 100 + template_index)
    digits = [str(value) for value in rng.integers(0, 10, size=10)]
    omr = [bool(value) for value in rng.integers(0, 2, size=10)]
    return digits, omr


def _align_to_canonical(image: Image, pipeline: OpenCvImagePipeline) -> tuple[Image, bool]:
    try:
        source = pipeline.detect_aruco_corners(image)
    except ValueError:
        return image, False
    target = np.asarray([[20, 20], [679, 20], [679, 979], [20, 979]], dtype=np.float32)
    transform = cv2.getPerspectiveTransform(source, target)
    aligned = cv2.warpPerspective(image, transform, (700, 1000), borderValue=(255,))
    return cast(Image, aligned), True


def _regions(form: SyntheticForm) -> list[FieldRegion]:
    return [
        FieldRegion(f"field-{index:02d}", x, y, width, height)
        for index, (x, y, width, height) in enumerate(form.field_regions)
    ]


def _evaluate_variant(
    form: SyntheticForm,
    image: Image,
    *,
    seed: int,
    split: str,
    condition: str,
    severity: float,
    variant: str,
    digit_threshold: float,
    digit_model: HogSvmBaseline,
    pipeline: OpenCvImagePipeline,
) -> FormOutcome:
    template_identified = (
        False
        if variant == "without_qr"
        else pipeline.read_template_qr(image) == form.template_reference
    )
    if variant == "without_aruco":
        aligned, alignment_succeeded = image, False
    else:
        aligned, alignment_succeeded = _align_to_canonical(image, pipeline)
    crops = pipeline.crop_fields(aligned, _regions(form))
    omr = OmrRecognizer()
    digit_candidates = [digit_model.predict(crops[f"field-{index:02d}"]) for index in range(10)]
    omr_candidates = [omr.recognize(crops[f"field-{index:02d}"]) for index in range(10, 20)]
    digit_accepted = sum(candidate.score >= digit_threshold for candidate in digit_candidates)
    digit_correct = sum(
        candidate.value == label
        for candidate, label in zip(digit_candidates, form.digit_labels, strict=True)
    )
    omr_accepted = sum(candidate.accepted for candidate in omr_candidates)
    omr_correct = sum(
        candidate.value == label
        for candidate, label in zip(omr_candidates, form.omr_labels, strict=True)
    )
    complete = (
        template_identified
        and alignment_succeeded
        and digit_accepted == 10
        and digit_correct == 10
        and omr_accepted == 10
        and omr_correct == 10
    )
    return FormOutcome(
        base_form_id=f"s{seed}-{form.template_reference}",
        seed=seed,
        split=split,
        template_reference=form.template_reference,
        condition=condition,
        severity=severity,
        variant=variant,
        template_identified=template_identified,
        alignment_succeeded=alignment_succeeded,
        digit_fields=10,
        digit_accepted=digit_accepted,
        digit_correct=digit_correct,
        omr_fields=10,
        omr_accepted=omr_accepted,
        omr_correct=omr_correct,
        complete_form_correct=complete,
    )


def _aggregate(rows: list[FormOutcome], variant: str) -> dict[str, Any]:
    selected = [row for row in rows if row.variant == variant and row.split == "evaluation"]
    digit_fields = sum(row.digit_fields for row in selected)
    omr_fields = sum(row.omr_fields for row in selected)
    return {
        "variant": variant,
        "condition_rows": len(selected),
        "template_identification_rate": sum(row.template_identified for row in selected)
        / len(selected),
        "alignment_success_rate": sum(row.alignment_succeeded for row in selected) / len(selected),
        "digit_fields": digit_fields,
        "digit_coverage": sum(row.digit_accepted for row in selected) / digit_fields,
        "digit_accuracy": sum(row.digit_correct for row in selected) / digit_fields,
        "omr_fields": omr_fields,
        "omr_coverage": sum(row.omr_accepted for row in selected) / omr_fields,
        "omr_accuracy": sum(row.omr_correct for row in selected) / omr_fields,
        "complete_form_success_rate": sum(row.complete_form_correct for row in selected)
        / len(selected),
    }


def _run_evaluation_workflows(
    templates: list[dict[str, Any]],
    evaluation_seeds: list[int],
    digit_model: HogSvmBaseline,
    digit_threshold: float,
) -> list[FormWorkflowOutcome]:
    outcomes: list[FormWorkflowOutcome] = []
    with tempfile.TemporaryDirectory(prefix="auto-decte-form-workflows-") as temporary:
        root = Path(temporary)
        for seed in evaluation_seeds:
            for template_index, template in enumerate(templates):
                digits, omr = _labels(seed, template_index)
                form = render_form(
                    digits,
                    omr,
                    seed=seed,
                    template_id=str(template["template_id"]),
                    template_version=str(template["template_version"]),
                    font=_font(str(template["font"])),
                )
                outcomes.append(
                    run_synthetic_form_workflow(
                        form,
                        root / f"s{seed}-t{template_index}",
                        form_id=f"FORM-{seed}-{template_index}",
                        digit_model=digit_model,
                        digit_threshold=digit_threshold,
                    )
                )
    return outcomes


def run_form_benchmark(config_path: Path, output: Path) -> FormBenchmarkRun:
    config = cast(dict[str, Any], json.loads(config_path.read_text(encoding="utf-8")))
    templates = cast(list[dict[str, Any]], config["form_templates"])
    conditions = cast(list[dict[str, Any]], config["form_conditions"])
    calibration_seeds = cast(list[int], config["form_calibration_seeds"])
    evaluation_seeds = cast(list[int], config["form_evaluation_seeds"])
    digit_threshold = float(config["form_digit_threshold"])
    digit_model = fit_hog_svm(
        cast(list[int], config["training_seeds"]),
        cast(list[str], config["fonts"]),
    )
    pipeline = OpenCvImagePipeline()
    rows: list[FormOutcome] = []
    for split, seeds in (
        ("calibration", calibration_seeds),
        ("evaluation", evaluation_seeds),
    ):
        for seed in seeds:
            for template_index, template in enumerate(templates):
                digits, omr = _labels(seed, template_index)
                form = render_form(
                    digits,
                    omr,
                    seed=seed,
                    template_id=str(template["template_id"]),
                    template_version=str(template["template_version"]),
                    font=_font(str(template["font"])),
                )
                for condition_index, condition in enumerate(conditions):
                    name = str(condition["name"])
                    severity = float(condition["severity"])
                    image = apply_perturbation(
                        form.image,
                        name,
                        severity,
                        seed=seed * 1000 + template_index * 100 + condition_index,
                    )
                    for variant in ("full_pipeline", "without_qr", "without_aruco"):
                        rows.append(
                            _evaluate_variant(
                                form,
                                image,
                                seed=seed,
                                split=split,
                                condition=name,
                                severity=severity,
                                variant=variant,
                                digit_threshold=digit_threshold,
                                digit_model=digit_model,
                                pipeline=pipeline,
                            )
                        )
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "form_raw.json", rows)
    workflows = _run_evaluation_workflows(templates, evaluation_seeds, digit_model, digit_threshold)
    write_json(output / "form_workflow.json", workflows)
    evaluation_condition_rows = len(evaluation_seeds) * len(templates) * len(conditions)
    summary = {
        "benchmark_id": config["benchmark_id"],
        "base_calibration_forms": len(calibration_seeds) * len(templates),
        "base_evaluation_forms": len(evaluation_seeds) * len(templates),
        "evaluation_condition_rows": evaluation_condition_rows,
        "digit_recognizer": digit_model.name,
        "digit_threshold": digit_threshold,
        "workflow": {
            "forms": len(workflows),
            "candidate_count": sum(item.candidate_count for item in workflows),
            "versioned_fact_rate": sum(item.record_version == 1 for item in workflows)
            / len(workflows),
            "export_trace_success_rate": sum(item.export_trace_success for item in workflows)
            / len(workflows),
        },
        "ablations": [
            _aggregate(rows, variant)
            for variant in ("full_pipeline", "without_qr", "without_aruco")
        ],
    }
    write_json(output / "form_summary.json", [summary])
    return FormBenchmarkRun(
        base_form_count=(len(calibration_seeds) + len(evaluation_seeds)) * len(templates),
        evaluation_form_count=evaluation_condition_rows,
        raw_row_count=len(rows),
        workflow_count=len(workflows),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the synthetic whole-form benchmark")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_form_benchmark(args.config, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
