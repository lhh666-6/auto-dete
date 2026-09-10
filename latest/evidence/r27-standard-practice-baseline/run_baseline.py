"""Minimal ordinary approval/audit-log baseline for the r27 executable design example.

This is the "standard practice" comparator requested by the JSS review: a
conventional SQLite approval table that stores approved values, expected
version, and a complete before/after audit log, but *not* the exact reviewed
candidate binding and *not* an explicit per-field source map.  It is
deliberately generous: it still validates candidate record/field context,
approved-value equality, changed-field domain, and version CAS, and it can
reconstruct per-field sources from the audit log.  The only capabilities it
lacks relative to the candidate-bound policy are exact reviewed-candidate
binding and the resulting unique proposal/authorized-value attribution.

Run:
    python run_baseline.py --out-dir <dir>

The runner writes one SQLite database per case plus summary.json/runs.json.
It never overwrites an existing database or evidence directory.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


class Rejected(Exception):
    pass


class ApprovalLogDemo:
    """Ordinary approval/audit-log policy with no reviewed-candidate binding."""

    def __init__(self, path, policy: str = "approval_log"):
        self.path = Path(path)
        if self.path.exists():
            raise FileExistsError("Use a fresh database; never overwrite a prior run")
        self.policy = policy
        self.con = sqlite3.connect(self.path, isolation_level=None)
        self.con.execute("PRAGMA foreign_keys=ON")
        self.con.execute("PRAGMA synchronous=FULL")
        self.con.executescript("""
            CREATE TABLE candidates (
                candidate_id TEXT PRIMARY KEY, record_id TEXT NOT NULL,
                field TEXT NOT NULL, proposed_json TEXT NOT NULL);
            CREATE TABLE records (
                record_id TEXT PRIMARY KEY, version INTEGER NOT NULL,
                values_json TEXT NOT NULL);
            CREATE TABLE approvals (
                approval_id TEXT PRIMARY KEY, record_id TEXT NOT NULL,
                expected_version INTEGER NOT NULL, principal TEXT NOT NULL,
                approved_values_json TEXT NOT NULL);
            CREATE TABLE versions (
                version INTEGER PRIMARY KEY, values_json TEXT NOT NULL);
            CREATE TABLE audits (
                version INTEGER PRIMARY KEY REFERENCES versions(version),
                approval_id TEXT NOT NULL REFERENCES approvals(approval_id),
                principal TEXT NOT NULL, before_json TEXT NOT NULL,
                after_json TEXT NOT NULL);
        """)
        for table in ("candidates", "approvals", "versions", "audits"):
            for action in ("UPDATE", "DELETE"):
                self.con.execute(
                    f"CREATE TRIGGER freeze_{table}_{action} BEFORE {action} ON {table} "
                    "BEGIN SELECT RAISE(ABORT, 'immutable history'); END")
        self.con.executemany("INSERT INTO candidates VALUES (?,?,?,?)", [
            ("q100a", "R1", "quantity", "100"),
            ("q100b", "R1", "quantity", "100"),
            ("q101", "R1", "quantity", "101"),
            ("other100", "R2", "quantity", "100"),
            ("batchB", "R1", "batch", '"B"'),
        ])
        initial = canonical({"quantity": 90, "batch": "A"})
        self.con.execute("INSERT INTO records VALUES ('R1',0,?)", (initial,))
        self.con.execute("INSERT INTO versions VALUES (0,?)", (initial,))

    def close(self):
        self.con.close()

    def _check_candidates(self, selected, fields):
        if set(selected) != set(fields):
            raise Rejected("field_domain")
        for field, candidate_id in selected.items():
            row = self.con.execute(
                "SELECT record_id,field FROM candidates WHERE candidate_id=?", (candidate_id,)
            ).fetchone()
            if row != ("R1", field):
                raise Rejected("candidate_context")

    def approve(self, approval_id, selected, values, principal="reviewer-1"):
        if principal != "reviewer-1":
            raise ValueError("unauthorized principal")
        if not values or not set(values) <= {"quantity", "batch"}:
            raise ValueError("invalid approval domain")
        self._check_candidates(selected, values)
        version = self.con.execute(
            "SELECT version FROM records WHERE record_id='R1'").fetchone()[0]
        self.con.execute(
            "INSERT INTO approvals VALUES (?,'R1',?,?,?)",
            (approval_id, version, principal, canonical(values)))

    def submit(self, approval_id, selected, values, *, fail_after_writes=False):
        self.con.execute("BEGIN IMMEDIATE")
        try:
            approval = self.con.execute(
                "SELECT expected_version,principal,approved_values_json "
                "FROM approvals WHERE approval_id=? AND record_id='R1'", (approval_id,)
            ).fetchone()
            if approval is None:
                raise Rejected("missing_approval")
            expected, principal, approved_json = approval
            if principal != "reviewer-1":
                raise Rejected("principal")
            if canonical(values) != approved_json:
                raise Rejected("approved_values")
            self._check_candidates(selected, values)
            before_json = self.con.execute(
                "SELECT values_json FROM records WHERE record_id='R1'").fetchone()[0]
            before = json.loads(before_json)
            after = {**before, **values}
            changed = {field for field in before
                       if canonical(before[field]) != canonical(after[field])}
            if changed != set(values):
                raise Rejected("changed_domain")
            successor = expected + 1
            after_json = canonical(after)
            updated = self.con.execute(
                "UPDATE records SET version=?,values_json=? WHERE record_id='R1' AND version=?",
                (successor, after_json, expected))
            if updated.rowcount != 1:
                raise Rejected("stale_version")
            self.con.execute("INSERT INTO versions VALUES (?,?)", (successor, after_json))
            self.con.execute("INSERT INTO audits VALUES (?,?,?,?,?)",
                             (successor, approval_id, principal, before_json, after_json))
            if fail_after_writes:
                raise Rejected("injected_failure")
            self.con.execute("COMMIT")
            return {"accepted": True, "reason": "committed"}
        except Rejected as exc:
            self.con.execute("ROLLBACK")
            return {"accepted": False, "reason": str(exc)}
        except Exception:
            self.con.execute("ROLLBACK")
            raise


def raw_state(db_path):
    with closing(sqlite3.connect(db_path)) as con:
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        state = {}
        for table in tables:
            columns = [r[1] for r in con.execute(f'PRAGMA table_info("{table}")')]
            rows = [list(r) for r in con.execute(f'SELECT * FROM "{table}" ORDER BY rowid')]
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
            if canonical(before[field]) != canonical(after[field]):
                sources[field] = f"v{row['version']}:{field}"
    return sources


def proposal_attribution(state):
    """Report what a conventional approval log can and cannot reconstruct."""
    approvals = rows_as_dicts(state, "approvals")
    if not approvals:
        return None
    approval = approvals[0]
    authorized = json.loads(approval["approved_values_json"])
    candidates = rows_as_dicts(state, "candidates")
    # The ordinary approval log stores no candidate identity.  A reviewer can
    # only join the proposal registry on record/field, which is ambiguous when
    # equal-valued candidates exist for the same field.
    field_candidates = {}
    for row in candidates:
        if row["record_id"] == approval["record_id"]:
            field_candidates.setdefault(row["field"], []).append(row["candidate_id"])
    return {
        "authorized_value": authorized,
        "reviewed_candidate_persisted": False,
        "candidate_ids_for_record": field_candidates,
        "unique_proposal_reconstruction": all(
            len(ids) == 1 for ids in field_candidates.values()),
    }


CASE_SPECS = {
    "legal-correction": "approve q100a; submit q100a (101)",
    "equal-value-substitution": "approve q100a; submit q100b (101)",
    "cross-record-candidate": "approve q100a; submit other100",
    "stale-version": "submit review-1 after intervening commit",
    "wrong-value": "approve 101; submit 102",
    "partial-batch": "approve quantity+batch; submit quantity",
    "injected-failure": "submit with failure after writes",
    "two-step-copy-forward": "commit quantity 101; then batch B",
    "paired-reviewed-candidate": "review q100a vs q101; both commit 101",
}

# Reference outcomes of the candidate-bound policy from
# evidence/checklist-runs-verified-2026-09-09/runs.json.
CANDIDATE_BOUND_REFERENCE = {
    "legal-correction": {"accepted": True, "reason": "committed"},
    "equal-value-substitution": {"accepted": False, "reason": "candidate_binding"},
    "cross-record-candidate": {"accepted": False, "reason": "candidate_context"},
    "stale-version": {"accepted": False, "reason": "stale_version"},
    "wrong-value": {"accepted": False, "reason": "approved_values"},
    "partial-batch": {"accepted": False, "reason": "approved_values"},
    "injected-failure": {"accepted": False, "reason": "injected_failure"},
    "two-step-copy-forward": {"accepted": True, "reason": "committed"},
    "paired-reviewed-candidate": {"states_equal": False},
}


def _fresh(out_dir, case_id, suffix=""):
    path = Path(out_dir) / "db" / f"{case_id}__approval_log{suffix}.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to replace prior evidence: {path}")
    return ApprovalLogDemo(path), path


def _record(case_id, requested, result, pre, post, path, out_dir, observations):
    return {
        "case_id": case_id,
        "policy": "approval_log",
        "requested_action": requested,
        "observed": {"accepted": bool(result["accepted"]),
                     "reason": result.get("reason")},
        "state_unchanged": pre["tables"] == post["tables"],
        "observations": observations,
        "database_file": path.name,
        "pre_state": pre,
        "post_state": post,
    }


def run_all(out_dir):
    out_dir = Path(out_dir)
    if out_dir.exists():
        raise FileExistsError(f"Refusing to replace prior evidence: {out_dir}")
    out_dir.mkdir(parents=True)
    runs = []

    # 1. legal correction
    demo, path = _fresh(out_dir, "legal-correction")
    try:
        demo.approve("review-1", {"quantity": "q100a"}, {"quantity": 101})
        pre = raw_state(path)
        result = demo.submit("review-1", {"quantity": "q100a"}, {"quantity": 101})
        post = raw_state(path)
        runs.append(_record(
            "legal-correction",
            [{"action": "approve", "candidate": {"quantity": "q100a"},
              "values": {"quantity": 101}},
             {"action": "submit", "candidate": {"quantity": "q100a"},
              "values": {"quantity": 101}}],
            result, pre, post, path, out_dir,
            {"successor_values": json.loads(rows_as_dicts(post, "records")[0]["values_json"]),
             "candidate_retained": any(d["candidate_id"] == "q100a"
                                       for d in rows_as_dicts(post, "candidates")),
             "audit_rows": len(rows_as_dicts(post, "audits")),
             "reconstructed_sources": reconstruct_sources(post),
             "proposal_attribution": proposal_attribution(post),
             "stored_sources": None}))
    finally:
        demo.close()

    # 2. equal-valued substitution
    demo, path = _fresh(out_dir, "equal-value-substitution")
    try:
        demo.approve("review-1", {"quantity": "q100a"}, {"quantity": 101})
        pre = raw_state(path)
        result = demo.submit("review-1", {"quantity": "q100b"}, {"quantity": 101})
        post = raw_state(path)
        runs.append(_record(
            "equal-value-substitution",
            [{"action": "approve", "candidate": {"quantity": "q100a"},
              "values": {"quantity": 101}},
             {"action": "submit", "candidate": {"quantity": "q100b"},
              "values": {"quantity": 101}}],
            result, pre, post, path, out_dir,
            {"reviewed_candidate": "q100a", "submitted_candidate": "q100b",
             "same_record_and_field": True,
             "reviewed_candidate_persisted": False,
             "accepted_substitute": bool(result["accepted"]),
             "proposal_attribution": proposal_attribution(post)}))
    finally:
        demo.close()

    # 3. cross-record candidate
    demo, path = _fresh(out_dir, "cross-record-candidate")
    try:
        demo.approve("review-1", {"quantity": "q100a"}, {"quantity": 101})
        pre = raw_state(path)
        result = demo.submit("review-1", {"quantity": "other100"}, {"quantity": 101})
        post = raw_state(path)
        runs.append(_record(
            "cross-record-candidate",
            [{"action": "approve", "candidate": {"quantity": "q100a"},
              "values": {"quantity": 101}},
             {"action": "submit", "candidate": {"quantity": "other100"},
              "values": {"quantity": 101}}],
            result, pre, post, path, out_dir,
            {"reviewed_candidate": "q100a", "submitted_candidate": "other100",
             "submitted_record": "R2"}))
    finally:
        demo.close()

    # 4. stale version
    demo, path = _fresh(out_dir, "stale-version")
    try:
        demo.approve("review-1", {"quantity": "q100a"}, {"quantity": 101})
        demo.approve("intervening", {"batch": "batchB"}, {"batch": "B"})
        first = demo.submit("intervening", {"batch": "batchB"}, {"batch": "B"})
        pre = raw_state(path)
        result = demo.submit("review-1", {"quantity": "q100a"}, {"quantity": 101})
        post = raw_state(path)
        runs.append(_record(
            "stale-version",
            [{"action": "approve", "candidate": {"quantity": "q100a"},
              "values": {"quantity": 101}},
             {"action": "intervening commit", "candidate": {"batch": "batchB"},
              "values": {"batch": "B"}},
             {"action": "submit", "candidate": {"quantity": "q100a"},
              "values": {"quantity": 101}, "note": "approved at version 0"}],
            result, pre, post, path, out_dir,
            {"intervening_commit_accepted": bool(first["accepted"]),
             "expected_version": 0,
             "version_after_intervening": rows_as_dicts(post, "records")[0]["version"]}))
    finally:
        demo.close()

    # 5. wrong value
    demo, path = _fresh(out_dir, "wrong-value")
    try:
        demo.approve("review-1", {"quantity": "q100a"}, {"quantity": 101})
        pre = raw_state(path)
        result = demo.submit("review-1", {"quantity": "q100a"}, {"quantity": 102})
        post = raw_state(path)
        runs.append(_record(
            "wrong-value",
            [{"action": "approve", "candidate": {"quantity": "q100a"},
              "values": {"quantity": 101}},
             {"action": "submit", "candidate": {"quantity": "q100a"},
              "values": {"quantity": 102}}],
            result, pre, post, path, out_dir,
            {"approved_value": 101, "submitted_value": 102}))
    finally:
        demo.close()

    # 6. partial batch
    demo, path = _fresh(out_dir, "partial-batch")
    try:
        demo.approve("review-1", {"quantity": "q100a", "batch": "batchB"},
                     {"quantity": 101, "batch": "B"})
        pre = raw_state(path)
        result = demo.submit("review-1", {"quantity": "q100a"}, {"quantity": 101})
        post = raw_state(path)
        runs.append(_record(
            "partial-batch",
            [{"action": "approve",
              "candidate": {"quantity": "q100a", "batch": "batchB"},
              "values": {"quantity": 101, "batch": "B"}},
             {"action": "submit", "candidate": {"quantity": "q100a"},
              "values": {"quantity": 101}}],
            result, pre, post, path, out_dir,
            {"approved_fields": ["quantity", "batch"],
             "submitted_fields": ["quantity"], "omitted_field": "batch"}))
    finally:
        demo.close()

    # 7. injected failure
    demo, path = _fresh(out_dir, "injected-failure")
    try:
        demo.approve("review-1", {"quantity": "q100a"}, {"quantity": 101})
        pre = raw_state(path)
        result = demo.submit("review-1", {"quantity": "q100a"}, {"quantity": 101},
                             fail_after_writes=True)
        post = raw_state(path)
        runs.append(_record(
            "injected-failure",
            [{"action": "approve", "candidate": {"quantity": "q100a"},
              "values": {"quantity": 101}},
             {"action": "submit", "candidate": {"quantity": "q100a"},
              "values": {"quantity": 101},
              "note": "injected failure after writes, before commit"}],
            result, pre, post, path, out_dir,
            {"injected_after": "CAS update, version insert, and audit insert",
             "tables_compared": sorted(pre["tables"])}))
    finally:
        demo.close()

    # 8. two-step copy-forward
    demo, path = _fresh(out_dir, "two-step-copy-forward")
    try:
        demo.approve("review-1", {"quantity": "q100a"}, {"quantity": 101})
        first = demo.submit("review-1", {"quantity": "q100a"}, {"quantity": 101})
        demo.approve("review-2", {"batch": "batchB"}, {"batch": "B"})
        pre = raw_state(path)
        second = demo.submit("review-2", {"batch": "batchB"}, {"batch": "B"})
        post = raw_state(path)
        reconstructed = reconstruct_sources(post)
        runs.append(_record(
            "two-step-copy-forward",
            [{"action": "commit", "candidate": {"quantity": "q100a"},
              "values": {"quantity": 101}},
             {"action": "commit", "candidate": {"batch": "batchB"},
              "values": {"batch": "B"},
              "note": "quantity is unchanged and must copy forward"}],
            second, pre, post, path, out_dir,
            {"first_step_accepted": bool(first["accepted"]),
             "second_step_accepted": bool(second["accepted"]),
             "reconstructed_sources": reconstructed,
             "stored_sources": None,
             "stored_matches_reconstruction": None,
             "proposal_attribution": proposal_attribution(post),
             "successor_versions": [v["version"] for v in rows_as_dicts(post, "versions")]}))
    finally:
        demo.close()

    # 9. paired reviewed-candidate histories
    runs_by_candidate = {}
    for candidate in ("q100a", "q101"):
        demo, path = _fresh(out_dir, "paired-reviewed-candidate", suffix=f"-{candidate}")
        try:
            demo.approve("review-1", {"quantity": candidate}, {"quantity": 101})
            result = demo.submit("review-1", {"quantity": candidate}, {"quantity": 101})
            runs_by_candidate[candidate] = {
                "observed": {"accepted": bool(result["accepted"]),
                             "reason": result.get("reason")},
                "state": raw_state(path),
                "database_file": path.name,
            }
        finally:
            demo.close()
    left = runs_by_candidate["q100a"]["state"]["tables"]
    right = runs_by_candidate["q101"]["state"]["tables"]
    differing = [table for table in sorted(left) if left[table] != right[table]]
    runs.append({
        "case_id": "paired-reviewed-candidate",
        "policy": "approval_log",
        "requested_action": [
            {"action": "approve+submit", "candidate": "q100a",
             "values": {"quantity": 101}},
            {"action": "approve+submit", "candidate": "q101",
             "values": {"quantity": 101}},
            {"note": "identical candidate pools, values, actor, and expected version"},
        ],
        "observed": {"states_equal": not differing, "differing_tables": differing},
        "state_unchanged": None,
        "observations": {
            "reviewed_candidates": ["q100a", "q101"],
            "candidate_proposed_values": {"q100a": 100, "q101": 101},
            "authorized_value": 101,
            "reviewed_candidate_persisted": False,
            "paired_histories_distinguishable": bool(differing),
        },
        "database_file": [runs_by_candidate[c]["database_file"]
                          for c in ("q100a", "q101")],
        "runs": runs_by_candidate,
    })

    # Comparison with the candidate-bound reference.
    by_case = {r["case_id"]: r for r in runs}
    divergent = []
    agreed = []
    for case_id, reference in CANDIDATE_BOUND_REFERENCE.items():
        record = by_case[case_id]
        if case_id == "paired-reviewed-candidate":
            baseline = {"states_equal": record["observed"]["states_equal"]}
        else:
            baseline = {"accepted": record["observed"]["accepted"],
                        "reason": record["observed"]["reason"]}
        if baseline == reference:
            agreed.append(case_id)
        else:
            divergent.append(case_id)

    capabilities = {
        "reviewed_candidate_persisted": False,
        "per_field_sources_stored": False,
        "per_field_sources_reconstructable_from_audit": True,
        "paired_histories_distinguishable": by_case["paired-reviewed-candidate"]["observed"]["states_equal"] is False,
        "unique_proposal_reconstruction": by_case["legal-correction"]["observations"]["proposal_attribution"]["unique_proposal_reconstruction"],
    }
    summary = {
        "schema": "auto-decte.r27-standard-practice-baseline.v1",
        "policy": "approval_log",
        "cases": len(CASE_SPECS),
        "runs": len(runs),
        "single_history_records": len([r for r in runs if r["case_id"] != "paired-reviewed-candidate"]),
        "paired_history_records": 1,
        "accepted_runs": sum(1 for r in runs if r["case_id"] != "paired-reviewed-candidate"
                             and r["observed"].get("accepted") is True),
        "rejected_runs": sum(1 for r in runs if r["case_id"] != "paired-reviewed-candidate"
                             and r["observed"].get("accepted") is False),
        "agreement_with_candidate_bound": agreed,
        "divergence_from_candidate_bound": divergent,
        "capabilities_relative_to_candidate_bound": capabilities,
        "interpretation": (
            "An ordinary approval/audit log agrees with the candidate-bound policy on "
            "the declared single-history cases except equal-valued candidate substitution. "
            "It can reconstruct per-field sources from the complete audit log, but it "
            "cannot distinguish which equal-valued candidate was reviewed, and the paired "
            "reviewed-candidate histories are identical in its persisted state. The "
            "demonstrated increment of candidate-bound admission is therefore exact "
            "reviewed-candidate binding and the resulting proposal/authorized-value "
            "attribution; this baseline is not a general event-sourcing/CQRS or temporal "
            "database comparison."
        ),
    }
    (out_dir / "runs.json").write_text(
        json.dumps(runs, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    summary = run_all(args.out_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
