"""Executable comparison runner for the two declared SQLite policies.

Implements the fixed-case execution, independent raw-SQLite inspection, record
export, and LaTeX table derivation specified in
``docs/executable-checklist-design.md`` (the Codex design document).  The two
policies under test are Codex's ``value_audit_demo.py``; this runner drives
their public API and does not modify them.

Every run writes, for one policy and one fixed case:

* the external requested action (never read back from the database),
* the complete pre- and post-run SQL state read through a *fresh* SQLite
  connection (independent of the ``Demo`` object), and
* a measured outcome plus case-specific observations.

Nine cases are declared in ``CASE_SPECS`` before execution.  The derived LaTeX
table reports the observed outcomes; the expected outcomes are checked by
``run_all`` so a changed policy fails loudly.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

from value_audit_demo import Demo

POLICIES = ("value_audit", "candidate_bound")

# Declared before execution.  ``label``/``request``/``expected`` are fixed
# external facts; the outcome columns of the derived table come from records.
CASE_SPECS = {
    "legal-correction": {
        "label": "Legal correction",
        "request": "approve q100a; submit q100a (101)",
        "expected": "both accept a complete successor",
    },
    "equal-value-substitution": {
        "label": "Equal-valued substitution",
        "request": "approve q100a; submit q100b (101)",
        "expected": "value-audit accepts; candidate-bound rejects",
    },
    "cross-record-candidate": {
        "label": "Cross-record candidate",
        "request": "approve q100a; submit other100",
        "expected": "both reject; state unchanged",
    },
    "stale-version": {
        "label": "Stale expected version",
        "request": "submit review-1 after intervening commit",
        "expected": "both reject; state unchanged",
    },
    "wrong-value": {
        "label": "Wrong submitted value",
        "request": "approve 101; submit 102",
        "expected": "both reject; state unchanged",
    },
    "partial-batch": {
        "label": "Partial approved batch",
        "request": "approve quantity+batch; submit quantity",
        "expected": "both reject; state unchanged",
    },
    "injected-failure": {
        "label": "Injected failure after writes",
        "request": "submit with failure after writes",
        "expected": "both roll back every table",
    },
    "two-step-copy-forward": {
        "label": "Two-step copy-forward",
        "request": "commit quantity 101; then batch B",
        "expected": "both reconstruct exact sources",
    },
    "paired-reviewed-candidate": {
        "label": "Paired reviewed-candidate histories",
        "request": "review q100a vs q101; both commit 101",
        "expected": "value-audit states identical; candidate-bound differ",
    },
}


# --------------------------------------------------------------------------
# Independent raw-SQLite inspection
# --------------------------------------------------------------------------

def raw_state(db_path):
    """Read every user table through a fresh connection, independent of Demo."""
    with closing(sqlite3.connect(db_path)) as con:
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        state = {}
        for table in tables:
            columns = [r[1] for r in con.execute(f'PRAGMA table_info("{table}")')]
            rows = [list(r) for r in con.execute(
                f'SELECT * FROM "{table}" ORDER BY rowid')]
            state[table] = {"columns": columns, "rows": rows}
        triggers = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name")]
    return {"tables": state, "triggers": triggers}


def rows_as_dicts(state, table):
    spec = state["tables"][table]
    return [dict(zip(spec["columns"], row)) for row in spec["rows"]]


def reconstruct_sources(state):
    """Rebuild per-field sources from the complete audit history alone."""
    sources = {"quantity": "v0:quantity", "batch": "v0:batch"}
    for row in rows_as_dicts(state, "audits"):
        before = json.loads(row["before_json"])
        after = json.loads(row["after_json"])
        for field in before:
            if _canonical(before[field]) != _canonical(after[field]):
                sources[field] = f"v{row['version']}:{field}"
    return sources


def dual_value_view(state):
    """Join the approval to the immutable candidate to expose both value roles."""
    approvals = rows_as_dicts(state, "approvals")
    if not approvals:
        return None
    approval = approvals[0]
    authorized = json.loads(approval["values_json"])
    binding_raw = approval["reviewed_candidates_json"]
    if binding_raw is None:
        return {
            "reviewed_candidate": None,
            "proposed_value": None,
            "authorized_value": authorized,
            "proposal_reconstructable_by_join": False,
        }
    binding = json.loads(binding_raw)
    candidates = {d["candidate_id"]: d for d in rows_as_dicts(state, "candidates")}
    proposed = {field: json.loads(candidates[cid]["proposed_json"])
                for field, cid in binding.items()}
    return {
        "reviewed_candidate": binding,
        "proposed_value": proposed,
        "authorized_value": authorized,
        "proposal_reconstructable_by_join": True,
    }


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


# --------------------------------------------------------------------------
# Run plumbing
# --------------------------------------------------------------------------

@contextmanager
def fresh_demo(out_dir, case_id, policy, suffix=""):
    path = Path(out_dir) / "db" / f"{case_id}__{policy}{suffix}.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to replace prior evidence: {path}")
    demo = Demo(path, policy)
    try:
        yield demo, path
    finally:
        demo.close()


def _relative(path, out_dir):
    try:
        return path.relative_to(Path(out_dir)).as_posix()
    except ValueError:
        return path.as_posix()


def _record(case_id, policy, requested_action, result, pre, post, path, out_dir,
            observations):
    spec = CASE_SPECS[case_id]
    return {
        "case_id": case_id,
        "policy": policy,
        "requested_action": requested_action,
        "expected": spec["expected"],
        "observed": {
            "accepted": bool(result["accepted"]),
            "reason": result.get("reason"),
        },
        "state_unchanged": pre["tables"] == post["tables"],
        "observations": observations,
        "database_file": _relative(path, out_dir),
        "pre_state": pre,
        "post_state": post,
    }


def _approve_quantity(demo, candidate="q100a", approval_id="review-1"):
    demo.approve(approval_id, {"quantity": candidate}, {"quantity": 101})


def _submit_quantity(demo, candidate="q100a", approval_id="review-1", **kw):
    return demo.submit(approval_id, {"quantity": candidate}, {"quantity": 101}, **kw)


# --------------------------------------------------------------------------
# The nine fixed cases
# --------------------------------------------------------------------------

def _case_legal_correction(out_dir, policy):
    case_id = "legal-correction"
    with fresh_demo(out_dir, case_id, policy) as (demo, path):
        _approve_quantity(demo)
        pre = raw_state(path)
        result = _submit_quantity(demo)
        post = raw_state(path)
        record = rows_as_dicts(post, "records")[0]
        candidates = {d["candidate_id"]: d for d in rows_as_dicts(post, "candidates")}
        observations = {
            "successor_values": json.loads(record["values_json"]),
            "candidate_retained": (
                "q100a" in candidates
                and candidates["q100a"]["proposed_json"] == "100"
            ),
            "audit_rows": len(rows_as_dicts(post, "audits")),
            "reconstructed_sources": reconstruct_sources(post),
            "dual_value": dual_value_view(post),
            "immutability_triggers": len(post["triggers"]),
        }
        return _record(case_id, policy, [
            {"action": "approve", "candidate": {"quantity": "q100a"},
             "values": {"quantity": 101}},
            {"action": "submit", "candidate": {"quantity": "q100a"},
             "values": {"quantity": 101}},
        ], result, pre, post, path, out_dir, observations)


def _case_equal_value_substitution(out_dir, policy):
    case_id = "equal-value-substitution"
    with fresh_demo(out_dir, case_id, policy) as (demo, path):
        _approve_quantity(demo)
        pre = raw_state(path)
        result = _submit_quantity(demo, candidate="q100b")
        post = raw_state(path)
        observations = {
            "reviewed_candidate": "q100a",
            "submitted_candidate": "q100b",
            "same_record_and_field": True,
            "candidate_proposed_value": 100,
            "authorized_value": 101,
            "reviewed_candidate_persisted": (
                rows_as_dicts(post, "approvals")[0]["reviewed_candidates_json"]
                is not None
            ),
        }
        return _record(case_id, policy, [
            {"action": "approve", "candidate": {"quantity": "q100a"},
             "values": {"quantity": 101}},
            {"action": "submit", "candidate": {"quantity": "q100b"},
             "values": {"quantity": 101}},
        ], result, pre, post, path, out_dir, observations)


def _case_cross_record_candidate(out_dir, policy):
    case_id = "cross-record-candidate"
    with fresh_demo(out_dir, case_id, policy) as (demo, path):
        _approve_quantity(demo)
        pre = raw_state(path)
        result = _submit_quantity(demo, candidate="other100")
        post = raw_state(path)
        observations = {
            "reviewed_candidate": "q100a",
            "submitted_candidate": "other100",
            "submitted_record": "R2",
        }
        return _record(case_id, policy, [
            {"action": "approve", "candidate": {"quantity": "q100a"},
             "values": {"quantity": 101}},
            {"action": "submit", "candidate": {"quantity": "other100"},
             "values": {"quantity": 101}},
        ], result, pre, post, path, out_dir, observations)


def _case_stale_version(out_dir, policy):
    case_id = "stale-version"
    with fresh_demo(out_dir, case_id, policy) as (demo, path):
        _approve_quantity(demo)
        demo.approve("intervening", {"batch": "batchB"}, {"batch": "B"})
        first = demo.submit("intervening", {"batch": "batchB"}, {"batch": "B"})
        pre = raw_state(path)
        result = _submit_quantity(demo)
        post = raw_state(path)
        observations = {
            "intervening_commit_accepted": bool(first["accepted"]),
            "expected_version": 0,
            "current_values": json.loads(rows_as_dicts(post, "records")[0]["values_json"]),
            "version_after_intervening": rows_as_dicts(post, "records")[0]["version"],
        }
        return _record(case_id, policy, [
            {"action": "approve", "candidate": {"quantity": "q100a"},
             "values": {"quantity": 101}},
            {"action": "intervening commit", "candidate": {"batch": "batchB"},
             "values": {"batch": "B"}},
            {"action": "submit", "candidate": {"quantity": "q100a"},
             "values": {"quantity": 101}, "note": "approved at version 0"},
        ], result, pre, post, path, out_dir, observations)


def _case_wrong_value(out_dir, policy):
    case_id = "wrong-value"
    with fresh_demo(out_dir, case_id, policy) as (demo, path):
        _approve_quantity(demo)
        pre = raw_state(path)
        result = demo.submit("review-1", {"quantity": "q100a"}, {"quantity": 102})
        post = raw_state(path)
        observations = {
            "approved_value": 101,
            "submitted_value": 102,
        }
        return _record(case_id, policy, [
            {"action": "approve", "candidate": {"quantity": "q100a"},
             "values": {"quantity": 101}},
            {"action": "submit", "candidate": {"quantity": "q100a"},
             "values": {"quantity": 102}},
        ], result, pre, post, path, out_dir, observations)


def _case_partial_batch(out_dir, policy):
    case_id = "partial-batch"
    with fresh_demo(out_dir, case_id, policy) as (demo, path):
        demo.approve("review-1", {"quantity": "q100a", "batch": "batchB"},
                     {"quantity": 101, "batch": "B"})
        pre = raw_state(path)
        result = demo.submit("review-1", {"quantity": "q100a"}, {"quantity": 101})
        post = raw_state(path)
        observations = {
            "approved_fields": ["quantity", "batch"],
            "submitted_fields": ["quantity"],
            "omitted_field": "batch",
        }
        return _record(case_id, policy, [
            {"action": "approve",
             "candidate": {"quantity": "q100a", "batch": "batchB"},
             "values": {"quantity": 101, "batch": "B"}},
            {"action": "submit", "candidate": {"quantity": "q100a"},
             "values": {"quantity": 101}},
        ], result, pre, post, path, out_dir, observations)


def _case_injected_failure(out_dir, policy):
    case_id = "injected-failure"
    with fresh_demo(out_dir, case_id, policy) as (demo, path):
        _approve_quantity(demo)
        pre = raw_state(path)
        result = _submit_quantity(demo, fail_after_writes=True)
        post = raw_state(path)
        observations = {
            "injected_after": "CAS update, version insert, and audit insert",
            "tables_compared": sorted(pre["tables"]),
        }
        return _record(case_id, policy, [
            {"action": "approve", "candidate": {"quantity": "q100a"},
             "values": {"quantity": 101}},
            {"action": "submit", "candidate": {"quantity": "q100a"},
             "values": {"quantity": 101},
             "note": "injected failure after writes, before commit"},
        ], result, pre, post, path, out_dir, observations)


def _case_two_step_copy_forward(out_dir, policy):
    case_id = "two-step-copy-forward"
    with fresh_demo(out_dir, case_id, policy) as (demo, path):
        _approve_quantity(demo)
        first = _submit_quantity(demo)
        demo.approve("review-2", {"batch": "batchB"}, {"batch": "B"})
        pre = raw_state(path)
        second = demo.submit("review-2", {"batch": "batchB"}, {"batch": "B"})
        post = raw_state(path)
        reconstructed = reconstruct_sources(post)
        stored = None
        versions = rows_as_dicts(post, "versions")
        if versions and versions[-1]["sources_json"] is not None:
            stored = json.loads(versions[-1]["sources_json"])
        observations = {
            "first_step_accepted": bool(first["accepted"]),
            "second_step_accepted": bool(second["accepted"]),
            "reconstructed_sources": reconstructed,
            "stored_sources": stored,
            "stored_matches_reconstruction": (
                stored == reconstructed if stored is not None else None
            ),
            "successor_versions": [v["version"] for v in versions],
        }
        return _record(case_id, policy, [
            {"action": "commit", "candidate": {"quantity": "q100a"},
             "values": {"quantity": 101}},
            {"action": "commit", "candidate": {"batch": "batchB"},
             "values": {"batch": "B"},
             "note": "quantity is unchanged and must copy forward"},
        ], second, pre, post, path, out_dir, observations)


def _case_paired_reviewed_candidate(out_dir, policy):
    case_id = "paired-reviewed-candidate"
    runs = {}
    for candidate in ("q100a", "q101"):
        with fresh_demo(out_dir, case_id, policy, suffix=f"-{candidate}") as (demo, path):
            _approve_quantity(demo, candidate=candidate)
            result = _submit_quantity(demo, candidate=candidate)
            runs[candidate] = {
                "observed": {"accepted": bool(result["accepted"]),
                             "reason": result.get("reason")},
                "state": raw_state(path),
                "database_file": _relative(path, out_dir),
            }
    left, right = runs["q100a"]["state"], runs["q101"]["state"]
    differing = [table for table in sorted(left["tables"])
                 if left["tables"][table] != right["tables"][table]]
    states_equal = not differing
    observations = {
        "reviewed_candidates": ["q100a", "q101"],
        "candidate_proposed_values": {"q100a": 100, "q101": 101},
        "authorized_value": 101,
        "differing_tables": differing,
        "reviewed_candidate_persisted": any(
            row["reviewed_candidates_json"] is not None
            for row in rows_as_dicts(left, "approvals")
        ),
    }
    return {
        "case_id": case_id,
        "policy": policy,
        "requested_action": [
            {"action": "approve+submit", "candidate": "q100a", "values": {"quantity": 101}},
            {"action": "approve+submit", "candidate": "q101", "values": {"quantity": 101}},
            {"note": "identical candidate pools, values, actor, and expected version"},
        ],
        "expected": CASE_SPECS[case_id]["expected"],
        "observed": {"states_equal": states_equal, "differing_tables": differing},
        "state_unchanged": None,
        "observations": observations,
        "database_file": [runs[c]["database_file"] for c in ("q100a", "q101")],
        "runs": runs,
    }


CASE_RUNNERS = {
    "legal-correction": _case_legal_correction,
    "equal-value-substitution": _case_equal_value_substitution,
    "cross-record-candidate": _case_cross_record_candidate,
    "stale-version": _case_stale_version,
    "wrong-value": _case_wrong_value,
    "partial-batch": _case_partial_batch,
    "injected-failure": _case_injected_failure,
    "two-step-copy-forward": _case_two_step_copy_forward,
    "paired-reviewed-candidate": _case_paired_reviewed_candidate,
}


# --------------------------------------------------------------------------
# Expected-outcome checks and summary
# --------------------------------------------------------------------------

def _expect(record, accepted=None, reason=None, unchanged=None, states_equal=None):
    observed = record["observed"]
    if accepted is not None and observed.get("accepted") is not accepted:
        raise AssertionError(f"{record['case_id']}/{record['policy']}: accepted={observed.get('accepted')}, expected {accepted}")
    if reason is not None and observed.get("reason") != reason:
        raise AssertionError(f"{record['case_id']}/{record['policy']}: reason={observed.get('reason')!r}, expected {reason!r}")
    if unchanged is not None and record.get("state_unchanged") is not unchanged:
        raise AssertionError(f"{record['case_id']}/{record['policy']}: state_unchanged={record.get('state_unchanged')}, expected {unchanged}")
    if states_equal is not None and observed.get("states_equal") is not states_equal:
        raise AssertionError(f"{record['case_id']}/{record['policy']}: states_equal={observed.get('states_equal')}, expected {states_equal}")


def check_expected_outcomes(records):
    """Fail loudly if any policy departs from the declared expectations."""
    def require(condition, message):
        if not condition:
            raise AssertionError(message)

    keys = [(r["case_id"], r["policy"]) for r in records]
    required_keys = {(case, policy) for case in CASE_SPECS for policy in POLICIES}
    require(len(keys) == len(set(keys)) and set(keys) == required_keys,
            "Missing, duplicate, or unexpected case/policy records")
    by_key = {(r["case_id"], r["policy"]): r for r in records}
    for case_id in CASE_SPECS:
        va = by_key[(case_id, "value_audit")]
        cb = by_key[(case_id, "candidate_bound")]
        if case_id == "legal-correction":
            _expect(va, accepted=True, unchanged=False)
            _expect(cb, accepted=True, unchanged=False)
            for record in (va, cb):
                obs = record["observations"]
                persisted = rows_as_dicts(record["post_state"], "records")[0]
                require(obs["successor_values"] == {"quantity": 101, "batch": "A"},
                        "Wrong legal-correction value observation")
                require(json.loads(persisted["values_json"]) == obs["successor_values"]
                        and persisted["version"] == 1,
                        "Legal successor does not match persisted state")
                require(obs["candidate_retained"] and obs["audit_rows"] == 1,
                        "Candidate or legal audit missing")
            require(cb["observations"]["dual_value"]["proposed_value"] == {"quantity": 100}
                    and cb["observations"]["dual_value"]["authorized_value"] == {"quantity": 101},
                    "Candidate-bound legal correction lost its value roles")
        elif case_id == "equal-value-substitution":
            _expect(va, accepted=True)
            _expect(cb, accepted=False, reason="candidate_binding", unchanged=True)
        elif case_id == "cross-record-candidate":
            _expect(va, accepted=False, reason="candidate_context", unchanged=True)
            _expect(cb, accepted=False, reason="candidate_context", unchanged=True)
        elif case_id == "stale-version":
            _expect(va, accepted=False, reason="stale_version", unchanged=True)
            _expect(cb, accepted=False, reason="stale_version", unchanged=True)
        elif case_id == "wrong-value":
            _expect(va, accepted=False, reason="approved_values", unchanged=True)
            _expect(cb, accepted=False, reason="approved_values", unchanged=True)
        elif case_id == "partial-batch":
            _expect(va, accepted=False, reason="approved_values", unchanged=True)
            _expect(cb, accepted=False, reason="approved_values", unchanged=True)
        elif case_id == "injected-failure":
            _expect(va, accepted=False, reason="injected_failure", unchanged=True)
            _expect(cb, accepted=False, reason="injected_failure", unchanged=True)
        elif case_id == "two-step-copy-forward":
            _expect(va, accepted=True)
            _expect(cb, accepted=True)
            for record in (va, cb):
                obs = record["observations"]
                require(obs["first_step_accepted"] and obs["second_step_accepted"],
                        "Copy-forward setup or successor failed")
                require(obs["successor_versions"] == [0, 1, 2],
                        "Copy-forward history is incomplete")
                if obs["reconstructed_sources"] != {"quantity": "v1:quantity",
                                                    "batch": "v2:batch"}:
                    raise AssertionError(f"{record['case_id']}/{record['policy']}: bad reconstruction {obs['reconstructed_sources']}")
            if cb["observations"]["stored_sources"] != cb["observations"]["reconstructed_sources"]:
                raise AssertionError("candidate_bound stored sources do not match reconstruction")
            if va["observations"]["stored_sources"] is not None:
                raise AssertionError("value_audit unexpectedly stores per-field sources")
        elif case_id == "paired-reviewed-candidate":
            for record in (va, cb):
                for run in record["runs"].values():
                    require(run["observed"]["accepted"] is True
                            and run["observed"]["reason"] == "committed",
                            "Paired history branch did not commit")
                    current = rows_as_dicts(run["state"], "records")[0]
                    require(current["version"] == 1
                            and json.loads(current["values_json"]) == {"quantity": 101, "batch": "A"},
                            "Paired history branch has wrong terminal state")
                left, right = (record["runs"][c]["state"]["tables"] for c in ("q100a", "q101"))
                require(record["observed"]["states_equal"] == (left == right),
                        "Paired equality disagrees with persisted observations")
            _expect(va, states_equal=True)
            _expect(cb, states_equal=False)
            if cb["observations"]["differing_tables"] != ["approvals"]:
                raise AssertionError(f"unexpected differing tables: {cb['observations']['differing_tables']}")
    return True


def summarise(records):
    by_key = {(r["case_id"], r["policy"]): r for r in records}
    outcome_divergent = []
    for case_id in CASE_SPECS:
        if case_id == "paired-reviewed-candidate":
            continue
        va = by_key[(case_id, "value_audit")]["observed"]
        cb = by_key[(case_id, "candidate_bound")]["observed"]
        if (va.get("accepted"), va.get("reason")) != (cb.get("accepted"), cb.get("reason")):
            outcome_divergent.append(case_id)
    accepted = {(c, p): by_key[(c, p)]["observed"].get("accepted")
                for c in CASE_SPECS for p in POLICIES
                if c != "paired-reviewed-candidate"}
    paired = {
        policy: by_key[("paired-reviewed-candidate", policy)]["observed"]["states_equal"]
        for policy in POLICIES
    }
    return {
        "cases": len(CASE_SPECS),
        "policies": list(POLICIES),
        "runs": len(records),
        "run_definition": "case/policy records; each paired-history record contains two database executions",
        "single_history_records": len(accepted),
        "paired_history_records": len(paired),
        "database_executions": len(accepted) + 2 * len(paired),
        "outcome_divergent_cases": outcome_divergent,
        "outcome_agreement_cases": [
            c for c in CASE_SPECS
            if c not in outcome_divergent and c != "paired-reviewed-candidate"
        ],
        "paired_history_states_equal": paired,
        "capability_notes": {
            "reviewed_candidate_persisted": {
                policy: by_key[("legal-correction", policy)]["observations"]["dual_value"]["reviewed_candidate"] is not None
                for policy in POLICIES},
            "per_field_sources_stored": {
                policy: by_key[("two-step-copy-forward", policy)]["observations"]["stored_sources"] is not None
                for policy in POLICIES},
        },
        "accepted_runs": sum(1 for v in accepted.values() if v is True),
        "rejected_runs": sum(1 for v in accepted.values() if v is False),
        "all_expected_outcomes_met": check_expected_outcomes(records),
    }


# --------------------------------------------------------------------------
# LaTeX table derivation
# --------------------------------------------------------------------------

def _code(text):
    return r"\code{" + str(text) + "}"


def _outcome_cell(record):
    """Render one observed outcome as a short LaTeX cell."""
    case_id = record["case_id"]
    observed = record["observed"]
    if case_id == "paired-reviewed-candidate":
        if observed["states_equal"]:
            return "logical table state identical"
        return ("logical table state differs in "
                + ", ".join(_code(t) for t in observed["differing_tables"]))
    if observed["accepted"]:
        if case_id == "legal-correction":
            value = record["observations"]["successor_values"]["quantity"]
            return f"accept; v1 quantity={value}"
        if case_id == "two-step-copy-forward":
            sources = record["observations"]["reconstructed_sources"]
            stored = record["observations"]["stored_sources"]
            text = ("accept; sources "
                    + ", ".join(f"{k}={v}" for k, v in sorted(sources.items())))
            if stored is not None:
                text += "; stored"
            return text
        if case_id == "equal-value-substitution":
            return "accept; committed 101"
        return "accept"
    return "reject " + _code(observed["reason"]) + "; unchanged"


def derive_table(records):
    by_key = {(r["case_id"], r["policy"]): r for r in records}
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3.5pt}",
        (r"\caption{Executable comparison of two declared SQLite policies over nine cases fixed "
         r"before execution. Both share immutable candidates, complete version snapshots, "
         r"value/domain/version-bound approvals, atomic CAS, and complete before/after audits. "
         r"$\dagger$ marks the only accept/reject divergence; $\ddagger$ the paired-history "
         r"observation. The demonstrator is illustrative, not a production implementation or a "
         r"statistical comparison.}"),
        r"\label{tab:executable-checklist}",
        (r"\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{0.20\textwidth}"
         r">{\raggedright\arraybackslash}p{0.22\textwidth}"
         r">{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}X@{}}"),
        r"\toprule",
        (r"Case (fixed before execution) & Requested action & Value-audit policy "
         r"& Candidate-bound policy \\"),
        r"\midrule",
    ]
    outcome_divergent = set(summarise(records)["outcome_divergent_cases"])
    for index, (case_id, spec) in enumerate(CASE_SPECS.items()):
        va = by_key[(case_id, "value_audit")]
        cb = by_key[(case_id, "candidate_bound")]
        label = spec["label"]
        if case_id in outcome_divergent:
            label += r"$^\dagger$"
        elif case_id == "paired-reviewed-candidate":
            label += r"$^\ddagger$"
        lines.append(f"{label} & {spec['request']} & {_outcome_cell(va)} & "
                     f"{_outcome_cell(cb)} \\\\")
        if index != len(CASE_SPECS) - 1:
            lines.append(r"\addlinespace[2pt]")
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\end{table}",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def run_all(out_dir):
    """Execute all fixed cases, write records, and return them."""
    out_dir = Path(out_dir)
    if out_dir.exists():
        raise FileExistsError(f"Choose a new output directory; prior evidence exists: {out_dir}")
    (out_dir / "db").mkdir(parents=True, exist_ok=False)
    records = []
    for case_id, runner in CASE_RUNNERS.items():
        for policy in POLICIES:
            records.append(runner(out_dir, policy))
    summary = summarise(records)
    (out_dir / "runs.json").write_text(
        json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return records, summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="../../evidence/checklist-runs",
                        help="directory for database files and JSON records")
    parser.add_argument("--table", default=None,
                        help="optional path for the derived LaTeX table")
    args = parser.parse_args(argv)
    records, summary = run_all(args.out)
    if args.table:
        Path(args.table).parent.mkdir(parents=True, exist_ok=True)
        Path(args.table).write_text(derive_table(records), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
