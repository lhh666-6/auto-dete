import numpy as np

from benchmarks.metrics import (
    binomial_wilson_interval,
    bootstrap_interval,
    choose_threshold,
    cluster_bootstrap_interval,
    selective_metrics,
)


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


def test_identical_bootstrap_values_have_degenerate_interval() -> None:
    interval = bootstrap_interval(
        [3.0, 3.0, 3.0], statistic=lambda values: float(np.mean(values)), seed=7
    )
    assert interval.lower == interval.estimate == interval.upper == 3.0


def test_threshold_is_selected_on_calibration_risk_target() -> None:
    selected = choose_threshold(
        scores=[0.01, 0.02, 0.03],
        correct=[False, True, True],
        thresholds=[0.0, 0.02, 0.03],
        target_risk=0.0,
    )
    assert selected == 0.02


def test_wilson_interval_retains_uncertainty_after_zero_errors() -> None:
    interval = binomial_wilson_interval(successes=10, trials=10)
    assert interval.estimate == 1.0
    assert 0.7 < interval.lower < 1.0
    assert interval.upper == 1.0


def test_cluster_bootstrap_resamples_base_units_not_rows() -> None:
    interval = cluster_bootstrap_interval(
        values=[1.0, 1.0, 0.0, 0.0],
        clusters=["form-a", "form-a", "form-b", "form-b"],
        statistic=lambda values: float(values.mean()),
        seed=19,
        replicates=200,
    )

    assert interval.estimate == 0.5
    assert interval.lower == 0.0
    assert interval.upper == 1.0
