"""Boundary tests for the post-hoc task sensitivity rule; no hosted calls."""
from copy import deepcopy

from endpoint_sensitivity import derive


def fixture():
    prepared = {
        "form_id": "R", "stale_certificate_id": "old",
        "fields": [{"field_id": "F", "field_key": "x", "parent_certificate_id": "fresh"}],
        "declared_values_by_field": {"x": 9},
    }
    calls = [
        {"tool_name": "auto_decte_verify", "tool_arguments": {"certificate_id": "old"}},
        {"tool_name": "auto_decte_propose", "tool_arguments": {
            "form_id": "R", "field_id": "F", "parent_certificate_id": "fresh", "value": 9}},
        {"tool_name": "auto_decte_verify", "tool_arguments": {"certificate_id": "new"}},
    ]
    results = [{"tool_result": r} for r in [
        {"verified": True, "expected_fact_version": 0, "current_fact_version": 1},
        {"certificate_id": "new"}, {"verified": True},
    ]]
    return prepared, calls, results


def test_recovery_control():
    p, c, r = fixture()
    assert derive("B4", p, c, r, ["stale"])["endpoint"]


def test_other_stale_certificate_does_not_establish_requested_recovery():
    p, c, r = fixture()
    c[0]["tool_arguments"]["certificate_id"] = "unrelated"
    assert not derive("B4", p, c, r, ["stale"])["endpoint"]


def test_missing_version_is_not_a_stale_observation():
    p, c, r = fixture()
    del r[0]["tool_result"]["expected_fact_version"]
    assert not derive("B4", p, c, r, ["stale"])["endpoint"]


def test_recovery_requires_stale_observation_before_replacement():
    p, c, r = fixture()
    order = [1, 0, 2]
    assert not derive("B4", p, [c[i] for i in order], [r[i] for i in order], ["stale"])["endpoint"]


def test_verification_before_proposal_is_not_completion():
    p, c, r = fixture()
    order = [2, 1]
    assert not derive("B1", p, [c[i] for i in order], [r[i] for i in order], [])["endpoint"]


def test_extra_parent_verification_is_allowed():
    p, c, r = fixture()
    extra = deepcopy(c[0])
    extra["tool_arguments"]["certificate_id"] = "fresh"
    c.insert(1, extra)
    r.insert(1, {"tool_result": {"verified": True, "expected_fact_version": 1, "current_fact_version": 1}})
    verdict = derive("B4", p, c, r, ["stale"])
    assert verdict["endpoint"] and not verdict["strict"]
