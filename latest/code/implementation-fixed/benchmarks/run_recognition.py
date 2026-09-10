import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np
from numpy.typing import NDArray

from app.adapters.recognition.digits import DigitRecognizer
from benchmarks.baselines import (
    AlwaysPredictBaseline,
    BaselinePrediction,
    TesseractBaseline,
    fit_hog_svm,
)
from benchmarks.io import write_json
from benchmarks.metrics import (
    binomial_wilson_interval,
    bootstrap_interval,
    choose_threshold,
    cluster_bootstrap_interval,
    selective_metrics,
)
from benchmarks.perturbations import apply_perturbation
from benchmarks.schema import PredictionRow
from benchmarks.synthetic import Image, render_digit


@dataclass(frozen=True, slots=True)
class RecognitionRun:
    case_count: int
    raw_row_count: int
    model_count: int


def _font(name: str) -> int:
    value = getattr(cv2, name, None)
    if not isinstance(value, int):
        raise ValueError(f"unknown OpenCV font: {name}")
    return value


def _timed_predict(model: Any, image: Image) -> tuple[BaselinePrediction, float]:
    started = time.perf_counter_ns()
    prediction = cast(BaselinePrediction, model.predict(image))
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
    return prediction, elapsed_ms


def _base_unit_id(case_id: str) -> str:
    return "-".join(case_id.split("-")[:3])


def _cluster_intervals(
    rows: list[PredictionRow],
    accepted: list[bool],
    *,
    seed: int,
    replicates: int,
) -> dict[str, dict[str, float]]:
    correct = [row.prediction == row.target for row in rows]
    clusters = [_base_unit_id(row.case_id) for row in rows]

    def accepted_accuracy(values: NDArray[np.float64]) -> float:
        observed = values[~np.isnan(values)]
        return float(np.mean(observed)) if observed.size else 0.0

    coverage = cluster_bootstrap_interval(
        values=[float(value) for value in accepted],
        clusters=clusters,
        statistic=lambda values: float(np.mean(values)),
        seed=seed,
        replicates=replicates,
    )
    conditional_correct = [
        float(ok) if use else float("nan") for ok, use in zip(correct, accepted, strict=True)
    ]
    accuracy = cluster_bootstrap_interval(
        values=conditional_correct,
        clusters=clusters,
        statistic=accepted_accuracy,
        seed=seed + 1,
        replicates=replicates,
    )
    risk = cluster_bootstrap_interval(
        values=conditional_correct,
        clusters=clusters,
        statistic=lambda values: 1.0 - accepted_accuracy(values),
        seed=seed + 2,
        replicates=replicates,
    )
    return {
        "coverage": asdict(coverage),
        "accepted_accuracy": asdict(accuracy),
        "selective_risk": asdict(risk),
    }


def _selective_model_summary(
    model_name: str,
    rows: list[PredictionRow],
    config: dict[str, Any],
) -> dict[str, Any]:
    calibration_seeds = config.get("calibration_seeds")
    evaluation_seeds = config.get("evaluation_seeds")
    calibration = (
        [row for row in rows if row.seed in cast(list[int], calibration_seeds)]
        if calibration_seeds is not None
        else rows
    )
    evaluation = (
        [row for row in rows if row.seed in cast(list[int], evaluation_seeds)]
        if evaluation_seeds is not None
        else rows
    )
    thresholds = cast(list[float], config["thresholds"])
    if "selection_risk_target" in config:
        threshold = choose_threshold(
            scores=[row.score if row.prediction is not None else -1.0 for row in calibration],
            correct=[row.prediction == row.target for row in calibration],
            thresholds=thresholds,
            target_risk=float(config["selection_risk_target"]),
        )
        selection_method = "calibration-risk-target"
    else:
        threshold = float(config["selected_threshold"])
        selection_method = "fixed-config"
    accepted = [row.prediction is not None and row.score >= threshold for row in evaluation]
    metrics = selective_metrics(
        correct=[row.prediction == row.target for row in evaluation], accepted=accepted
    )
    return {
        "model": model_name,
        "selected_threshold": threshold,
        "selection_method": selection_method,
        "selection_risk_target": config.get("selection_risk_target"),
        "calibration_case_count": len(calibration),
        "evaluation_case_count": len(evaluation),
        "base_unit_count": len({_base_unit_id(row.case_id) for row in evaluation}),
        "selected_metrics": asdict(metrics),
        "cluster_bootstrap_ci95": _cluster_intervals(
            evaluation,
            accepted,
            seed=int(config["bootstrap_seed"]),
            replicates=int(config["bootstrap_replicates"]),
        ),
    }


def run_recognition(config_path: Path, output: Path) -> RecognitionRun:
    config = cast(dict[str, Any], json.loads(config_path.read_text(encoding="utf-8")))
    output.mkdir(parents=True, exist_ok=True)
    auto = DigitRecognizer(margin_threshold=0.0)
    always = AlwaysPredictBaseline()
    hog = fit_hog_svm(
        cast(list[int], config["training_seeds"]),
        cast(list[str], config["fonts"]),
    )
    tesseract = TesseractBaseline()
    models: list[tuple[str, Any]] = [("auto-decte", auto), (always.name, always), (hog.name, hog)]
    if bool(config.get("run_tesseract")) and tesseract.available:
        models.append((tesseract.name, tesseract))

    rows: list[PredictionRow] = []
    case_count = 0
    conditions = cast(list[dict[str, Any]], config["conditions"])
    for seed in cast(list[int], config["seeds"]):
        for font_index, font_name in enumerate(cast(list[str], config["fonts"])):
            for digit in cast(list[str], config["digits"]):
                source = render_digit(
                    digit,
                    font=_font(font_name),
                    seed=seed * 100 + font_index * 10 + int(digit),
                )
                for condition_index, condition in enumerate(conditions):
                    name = str(condition["name"])
                    for severity in cast(list[float], condition["severities"]):
                        case_count += 1
                        image = apply_perturbation(
                            source,
                            name,
                            float(severity),
                            seed=seed * 1000 + condition_index * 100 + int(digit),
                        )
                        case_id = f"s{seed}-f{font_index}-d{digit}-{name}-{severity:.3f}"
                        for model_name, model in models:
                            if model_name == "auto-decte":
                                started = time.perf_counter_ns()
                                candidate = auto.recognize_cell(image)
                                latency = (time.perf_counter_ns() - started) / 1_000_000
                                prediction = BaselinePrediction(
                                    value=candidate.value,
                                    accepted=candidate.accepted,
                                    score=float(candidate.decision_score or 0.0),
                                )
                            else:
                                prediction, latency = _timed_predict(model, image)
                            rows.append(
                                PredictionRow(
                                    case_id=case_id,
                                    seed=seed,
                                    target=digit,
                                    prediction=prediction.value,
                                    accepted=prediction.accepted,
                                    score=prediction.score,
                                    perturbation=name,
                                    severity=float(severity),
                                    latency_ms=latency,
                                    model=model_name,
                                )
                            )

    write_json(output / "recognition_raw.json", rows)
    auto_rows = [row for row in rows if row.model == "auto-decte"]
    selective_models = [
        _selective_model_summary(
            model_name,
            [row for row in rows if row.model == model_name],
            config,
        )
        for model_name in ("auto-decte", hog.name)
    ]
    auto_selective = selective_models[0]
    calibration_seed_values = config.get("calibration_seeds")
    evaluation_seed_values = config.get("evaluation_seeds")
    calibration_rows = (
        [row for row in auto_rows if row.seed in cast(list[int], calibration_seed_values)]
        if calibration_seed_values is not None
        else auto_rows
    )
    evaluation_rows = (
        [row for row in auto_rows if row.seed in cast(list[int], evaluation_seed_values)]
        if evaluation_seed_values is not None
        else auto_rows
    )
    thresholds = cast(list[float], config["thresholds"])
    selected_threshold = float(auto_selective["selected_threshold"])
    selection_method = str(auto_selective["selection_method"])

    sweep: list[dict[str, Any]] = []
    for threshold in thresholds:
        accepted = [
            row.prediction is not None and row.score >= threshold for row in evaluation_rows
        ]
        metrics = selective_metrics(
            correct=[row.prediction == row.target for row in evaluation_rows], accepted=accepted
        )
        sweep.append({"threshold": threshold, **asdict(metrics)})

    selected_accepted = [
        row.prediction is not None and row.score >= selected_threshold for row in evaluation_rows
    ]
    selected_metrics = selective_metrics(
        correct=[row.prediction == row.target for row in evaluation_rows],
        accepted=selected_accepted,
    )
    accepted_correct = [
        float(row.prediction == row.target)
        for row, accepted in zip(evaluation_rows, selected_accepted, strict=True)
        if accepted
    ]
    if not accepted_correct:
        accepted_correct = [0.0]
    interval = bootstrap_interval(
        accepted_correct,
        statistic=lambda values: float(np.mean(values)),
        seed=int(config["bootstrap_seed"]),
        replicates=int(config["bootstrap_replicates"]),
    )
    wilson_interval = binomial_wilson_interval(
        successes=int(sum(accepted_correct)), trials=len(accepted_correct)
    )

    robustness: list[dict[str, Any]] = []
    for condition in conditions:
        name = str(condition["name"])
        for severity in cast(list[float], condition["severities"]):
            group = [
                row
                for row in evaluation_rows
                if row.perturbation == name and row.severity == float(severity)
            ]
            group_accepted = [
                row.prediction is not None and row.score >= selected_threshold for row in group
            ]
            robustness.append(
                {
                    "perturbation": name,
                    "severity": float(severity),
                    **asdict(
                        selective_metrics(
                            correct=[row.prediction == row.target for row in group],
                            accepted=group_accepted,
                        )
                    ),
                }
            )

    baseline_summary: list[dict[str, Any]] = []
    for model_name, _ in models:
        evaluation_seeds = {row.seed for row in evaluation_rows}
        group = [row for row in rows if row.model == model_name and row.seed in evaluation_seeds]
        baseline_summary.append(
            {
                "model": model_name,
                "accuracy": sum(row.prediction == row.target for row in group) / len(group),
                "coverage": sum(row.accepted for row in group) / len(group),
                "cases": len(group),
            }
        )
    summary = {
        "benchmark_id": config["benchmark_id"],
        "case_count": case_count,
        "calibration_case_count": len(calibration_rows),
        "evaluation_case_count": len(evaluation_rows),
        "model_count": len(models),
        "tesseract_available": tesseract.available,
        "tesseract_version": tesseract.version,
        "selected_threshold": selected_threshold,
        "selection_method": selection_method,
        "selection_risk_target": config.get("selection_risk_target"),
        "selected_metrics": asdict(selected_metrics),
        "accepted_accuracy_ci95": asdict(interval),
        "accepted_accuracy_wilson_ci95": asdict(wilson_interval),
        "selective_models": selective_models,
        "threshold_sweep": sweep,
        "robustness": robustness,
        "baselines": baseline_summary,
    }
    write_json(output / "recognition_summary.json", [summary])
    return RecognitionRun(case_count=case_count, raw_row_count=len(rows), model_count=len(models))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run selective recognition benchmark")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_recognition(args.config, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
