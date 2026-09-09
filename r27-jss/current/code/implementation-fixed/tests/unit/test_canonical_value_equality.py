"""Regression tests for the single canonical value-equality relation.

Review finding R1: the admission planner used Python equality while the trace,
oracle, and projection used canonical JSON equality.  Python treats
``2 == 2.0`` and ``1 == True`` as true, so a legal submission could commit a
new value while reusing the previous source and then be reported as an
incomplete trace.  These tests pin the unified relation at every boundary.
"""

from __future__ import annotations

import pytest

from app.domain.admission import AdmissionShapeError, derive_admission_plan
from app.domain.authority import canonical_values_equal


def test_canonical_values_equal_separates_python_equal_distinct_json() -> None:
    assert canonical_values_equal(2, 2.0) is False
    assert canonical_values_equal(1, True) is False
    assert canonical_values_equal(0, False) is False
    assert canonical_values_equal({"k": 1}, {"k": 1.0}) is False
    assert canonical_values_equal([1, 2], [1.0, 2]) is False


def test_canonical_values_equal_accepts_same_json_payload() -> None:
    assert canonical_values_equal(2, 2) is True
    assert canonical_values_equal(2.0, 2.0) is True
    assert canonical_values_equal(True, True) is True
    assert canonical_values_equal({"b": 2, "a": 1}, {"a": 1, "b": 2}) is True
    assert canonical_values_equal([1, {"a": 2}], [1, {"a": 2}]) is True


def _plan(previous_b: object, proposed_b: object, previous_a: object = 1,
          proposed_a: object = 1) -> object:
    return derive_admission_plan(
        declared_fields=frozenset({"a", "b"}),
        previous_values={"a": previous_a, "b": previous_b},
        previous_fact_sources={"a": "T-a", "b": "T-b"},
        proposed_values={"a": proposed_a, "b": proposed_b},
    )


def test_planner_treats_integer_to_float_as_a_change() -> None:
    plan = _plan(2, 2.0, previous_a=1, proposed_a=1)
    assert plan.admission_fields == frozenset({"b"})
    assert plan.complete_values == {"a": 1, "b": 2.0}


def test_planner_treats_integer_to_boolean_as_a_change() -> None:
    plan = _plan(1, True, previous_a=1, proposed_a=1)
    assert plan.admission_fields == frozenset({"b"})
    assert plan.complete_values == {"a": 1, "b": True}


def test_planner_treats_nested_numeric_change_as_a_change() -> None:
    plan = _plan({"k": 1}, {"k": 1.0}, previous_a=1, proposed_a=1)
    assert plan.admission_fields == frozenset({"b"})


def test_planner_accepts_identical_canonical_value_without_change() -> None:
    plan = _plan(2, 2, previous_a=1, proposed_a=3)
    assert plan.admission_fields == frozenset({"a"})


def test_planner_rejects_pure_noop_under_canonical_equality() -> None:
    with pytest.raises(AdmissionShapeError) as excinfo:
        _plan(2, 2, previous_a=1, proposed_a=1)
    assert excinfo.value.code == "NO_CHANGED_FIELDS"
