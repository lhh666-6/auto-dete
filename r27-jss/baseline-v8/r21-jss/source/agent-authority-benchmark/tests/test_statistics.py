import pytest

from auto_decte_agent_benchmark.statistics import exact_binomial_interval


def test_zero_event_interval_reports_exact_one_sided_upper_bound() -> None:
    interval = exact_binomial_interval(0, 900, confidence=0.95)

    assert interval.count == 0
    assert interval.denominator == 900
    assert interval.proportion == 0
    assert interval.two_sided_lower == 0
    assert interval.one_sided_upper == pytest.approx(1 - 0.05 ** (1 / 900), rel=1e-12)
    assert interval.one_sided_upper == pytest.approx(0.003323, rel=1e-3)


def test_exact_interval_handles_interior_count_and_rejects_invalid_inputs() -> None:
    interval = exact_binomial_interval(5, 10, confidence=0.95)

    assert interval.proportion == 0.5
    assert interval.two_sided_lower == pytest.approx(0.187086, rel=1e-5)
    assert interval.two_sided_upper == pytest.approx(0.812914, rel=1e-5)
    assert interval.one_sided_upper is None
    with pytest.raises(ValueError):
        exact_binomial_interval(2, 1)
    with pytest.raises(ValueError):
        exact_binomial_interval(0, 0)
