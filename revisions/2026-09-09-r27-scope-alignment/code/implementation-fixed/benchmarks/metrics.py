from collections.abc import Callable, Sequence
from dataclasses import dataclass
from math import sqrt

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class SelectiveMetrics:
    total: int
    accepted: int
    coverage: float
    accepted_accuracy: float
    selective_risk: float
    erroneous_auto_pass_rate: float
    routing_rate: float


@dataclass(frozen=True, slots=True)
class ConfidenceInterval:
    estimate: float
    lower: float
    upper: float


def binomial_wilson_interval(
    *, successes: int, trials: int, z: float = 1.959963984540054
) -> ConfidenceInterval:
    if trials <= 0 or successes < 0 or successes > trials or z <= 0:
        raise ValueError("successes/trials and z must define a valid binomial sample")
    estimate = successes / trials
    denominator = 1.0 + z * z / trials
    center = (estimate + z * z / (2.0 * trials)) / denominator
    half_width = (
        z
        * sqrt(estimate * (1.0 - estimate) / trials + z * z / (4.0 * trials * trials))
        / denominator
    )
    return ConfidenceInterval(
        estimate=estimate,
        lower=0.0 if successes == 0 else max(0.0, center - half_width),
        upper=1.0 if successes == trials else min(1.0, center + half_width),
    )


def choose_threshold(
    *,
    scores: Sequence[float],
    correct: Sequence[bool],
    thresholds: Sequence[float],
    target_risk: float,
) -> float:
    if len(scores) != len(correct) or not scores or not thresholds:
        raise ValueError("scores/correct and thresholds must be non-empty")
    if not 0.0 <= target_risk <= 1.0:
        raise ValueError("target_risk must be in [0, 1]")
    ordered = sorted(thresholds)
    for threshold in ordered:
        accepted = [score >= threshold for score in scores]
        if not any(accepted):
            continue
        metrics = selective_metrics(correct=correct, accepted=accepted)
        if metrics.selective_risk <= target_risk:
            return threshold
    return ordered[-1]


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


def bootstrap_interval(
    values: Sequence[float],
    *,
    statistic: Callable[[NDArray[np.float64]], float],
    seed: int,
    replicates: int = 2000,
) -> ConfidenceInterval:
    if not values or replicates <= 0:
        raise ValueError("values must be non-empty and replicates positive")
    sample = np.asarray(values, dtype=np.float64)
    estimate = float(statistic(sample))
    rng = np.random.default_rng(seed)
    statistics = np.empty(replicates, dtype=np.float64)
    for index in range(replicates):
        draw = rng.choice(sample, size=sample.size, replace=True)
        statistics[index] = statistic(draw)
    lower, upper = np.percentile(statistics, [2.5, 97.5])
    return ConfidenceInterval(estimate=estimate, lower=float(lower), upper=float(upper))


def cluster_bootstrap_interval(
    *,
    values: Sequence[float],
    clusters: Sequence[str],
    statistic: Callable[[NDArray[np.float64]], float],
    seed: int,
    replicates: int = 2000,
) -> ConfidenceInterval:
    """Bootstrap whole base units while retaining every row within each sampled unit."""
    if len(values) != len(clusters) or not values or replicates <= 0:
        raise ValueError(
            "values/clusters must be non-empty, equally sized, and replicates positive"
        )
    unique_clusters = tuple(dict.fromkeys(clusters))
    sample = np.asarray(values, dtype=np.float64)
    cluster_array = np.asarray(clusters, dtype=object)
    estimate = float(statistic(sample))
    rng = np.random.default_rng(seed)
    statistics = np.empty(replicates, dtype=np.float64)
    for index in range(replicates):
        selected = rng.choice(unique_clusters, size=len(unique_clusters), replace=True)
        draw = np.concatenate([sample[cluster_array == cluster] for cluster in selected])
        statistics[index] = statistic(draw)
    lower, upper = np.percentile(statistics, [2.5, 97.5])
    return ConfidenceInterval(estimate=estimate, lower=float(lower), upper=float(upper))
