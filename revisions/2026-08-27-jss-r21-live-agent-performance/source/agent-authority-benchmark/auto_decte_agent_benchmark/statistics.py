"""Frozen exact-binomial statistics for benchmark proportions."""

from __future__ import annotations

from dataclasses import dataclass

from scipy.stats import beta


@dataclass(frozen=True, slots=True)
class ExactBinomialInterval:
    count: int
    denominator: int
    confidence: float
    proportion: float
    two_sided_lower: float
    two_sided_upper: float
    one_sided_upper: float | None


def exact_binomial_interval(
    count: int,
    denominator: int,
    *,
    confidence: float = 0.95,
) -> ExactBinomialInterval:
    if denominator <= 0 or count < 0 or count > denominator:
        raise ValueError("count and denominator must satisfy 0 <= count <= denominator and N > 0")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be strictly between zero and one")
    alpha = 1 - confidence
    lower = 0.0 if count == 0 else float(beta.ppf(alpha / 2, count, denominator - count + 1))
    upper = (
        1.0
        if count == denominator
        else float(beta.ppf(1 - alpha / 2, count + 1, denominator - count))
    )
    one_sided_upper = 1 - alpha ** (1 / denominator) if count == 0 else None
    return ExactBinomialInterval(
        count=count,
        denominator=denominator,
        confidence=confidence,
        proportion=count / denominator,
        two_sided_lower=lower,
        two_sided_upper=upper,
        one_sided_upper=one_sided_upper,
    )
