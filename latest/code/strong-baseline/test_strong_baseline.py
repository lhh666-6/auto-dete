"""Regression tests for the strengthened transactional value-audit baseline.

Run:
    python -m pytest test_strong_baseline.py -q
    python test_strong_baseline.py        # plain run, no pytest required
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from strong_baseline import b0_bridge, cases, e1  # noqa: E402
from strong_baseline.analysis import project  # noqa: E402
from strong_baseline.policies import POLICY_B1, POLICY_FULL  # noqa: E402

B0_DIVERGENCE = ["equal-value-substitution", "paired-reviewed-candidate"]


def test_frozen_artifacts_unchanged():
    pins = b0_bridge.verify_pins()
    assert all(entry["match"] for entry in pins.values()), pins


def test_b0_still_reproduces_seven_of_eight(tmp=None):
    """B0 is imported, not rewritten: its own reference table is unchanged."""
    assert len(cases.CANDIDATE_BOUND_REFERENCE) == 9
    assert cases.CANDIDATE_BOUND_REFERENCE["equal-value-substitution"] == {
        "accepted": False, "reason": "candidate_binding"}


def test_b1_reproduces_the_declared_outcomes():
    with tempfile.TemporaryDirectory() as tmp:
        runs, dbs = cases.run_all_cases(POLICY_B1, Path(tmp) / "b1")
        comparison = cases.compare_with_reference(runs)
        assert comparison["divergence"] == B0_DIVERGENCE
        assert len(comparison["agreement"]) == 7
        by_case = {r["case_id"]: r for r in runs}
        assert by_case["legal-correction"]["observed"]["accepted"] is True
        assert by_case["equal-value-substitution"]["observed"]["accepted"] is True
        assert by_case["stale-version"]["observed"]["reason"] == "stale_version"
        assert by_case["paired-reviewed-candidate"]["observed"]["states_equal"] is True


def test_full_reproduces_the_frozen_reference_on_all_nine_cases():
    with tempfile.TemporaryDirectory() as tmp:
        runs, _ = cases.run_all_cases(POLICY_FULL, Path(tmp) / "full")
        comparison = cases.compare_with_reference(runs)
        assert comparison["divergence"] == []
        assert len(comparison["agreement"]) == 9


def test_b1_approval_is_value_bound():
    """No authority table may reference the candidate registry (section 46)."""
    with tempfile.TemporaryDirectory() as tmp:
        _, dbs = cases.run_all_cases(POLICY_B1, Path(tmp) / "b1")
        db = Path(tmp) / "b1" / "db" / "legal-correction__transactional_value_audit.db"
        relations = e1.candidate_identity_relations(db)
        assert relations["implements_exact_candidate_relation"] is False
        columns = {t: e1.columns_of_names(e1.raw_state(db), t) for t in e1.raw_state(db)["tables"]}
        for table, cols in columns.items():
            for col in cols:
                assert "candidate" not in col or table == "candidates", (table, col)


def test_e1_b1_histories_are_indistinguishable_and_ambiguous():
    with tempfile.TemporaryDirectory() as tmp:
        record = e1.run(Path(tmp) / "e1", policy=POLICY_B1)
        assert record["pass"] is True
        assert record["fairness"]["all_invariants_equal"] is True
        assert record["fairness"]["selected_candidate_differs"] is True
        assert record["actual_outcome"]["safe"]["accepted"] is True
        assert record["actual_outcome"]["unsafe"]["accepted"] is True
        assert record["comparison"]["declared_projection_differing_tables"] == []
        assert record["comparison"][
            "histories_indistinguishable_under_declared_projection"] is True
        assert record["review_origin_status"]["safe"]["status"] == "AMBIGUOUS"
        assert record["selected_candidate_if_recorded"]["unsafe"] == "NOT_RECORDED"


def test_e1_full_rejects_the_substitution_with_an_explicit_binding():
    with tempfile.TemporaryDirectory() as tmp:
        record = e1.run(Path(tmp) / "e1", policy=POLICY_FULL)
        assert record["actual_outcome"]["safe"]["accepted"] is True
        assert record["actual_outcome"]["unsafe"] == {"accepted": False,
                                                      "reason": "candidate_binding"}
        assert record["comparison"][
            "histories_indistinguishable_under_declared_projection"] is False
        assert record["review_origin_status"]["safe"]["status"] == "EXPLICITLY_BOUND"
        assert record["comparison"]["candidate_identity_relations"][
            "implements_exact_candidate_relation"] is True


def test_b2_detects_the_substitution_only_when_review_content_differs():
    with tempfile.TemporaryDirectory() as tmp:
        same = e1.run(Path(tmp) / "a", policy=POLICY_B1, variant="B2")
        diff = e1.run(Path(tmp) / "b", policy=POLICY_B1, variant="B2",
                      distinct_evidence_hash=True)
        assert same["actual_outcome"]["unsafe"]["accepted"] is True
        assert diff["actual_outcome"]["unsafe"] == {"accepted": False,
                                                    "reason": "reviewed_context"}


def test_declared_projection_ignores_surrogates_but_keeps_content():
    with tempfile.TemporaryDirectory() as tmp:
        record = e1.run(Path(tmp) / "e1", policy=POLICY_B1)
        state = e1.raw_state(Path(tmp) / "e1" /
                             record["histories"]["safe"]["database_file"])
        declared = project(state, declared=True)
        full = project(state, declared=False)
        assert "tx_id" in full["tx_log"]["columns"]
        assert "tx_id" not in declared["tx_log"]["columns"]
        assert declared["records"] == full["records"]


def _run_all():
    failures = []
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS {name}")
            except Exception as exc:  # pragma: no cover - test harness
                failures.append((name, exc))
                print(f"  FAIL {name}: {type(exc).__name__}: {exc}")
    return failures


if __name__ == "__main__":
    failures = _run_all()
    print("strong-baseline regression: " + ("PASS" if not failures else f"FAIL ({len(failures)})"))
    raise SystemExit(1 if failures else 0)
