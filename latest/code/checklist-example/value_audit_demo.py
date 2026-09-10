"""Two declared SQLite policies for an executable design example.

Both policies provide value-bound approval, complete before/after audits,
immutable candidates, exact field-domain checking and transactional version CAS.
Only candidate_bound persists the reviewed candidate binding and field sources.
This is not the full Auto-Decte implementation or a production security boundary.
"""
import json
from pathlib import Path
import sqlite3


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


class Rejected(Exception):
    pass


class Demo:
    def __init__(self, path, policy):
        if policy not in {"value_audit", "candidate_bound"}:
            raise ValueError("unknown policy")
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
                values_json TEXT NOT NULL, reviewed_candidates_json TEXT);
            CREATE TABLE versions (
                version INTEGER PRIMARY KEY, values_json TEXT NOT NULL,
                sources_json TEXT);
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
        sources = canonical({"quantity": "v0:quantity", "batch": "v0:batch"})
        self.con.execute("INSERT INTO versions VALUES (0,?,?)",
                         (initial, sources if policy == "candidate_bound" else None))

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
        version = self.con.execute("SELECT version FROM records WHERE record_id='R1'").fetchone()[0]
        binding = canonical(selected) if self.policy == "candidate_bound" else None
        self.con.execute("INSERT INTO approvals VALUES (?,'R1',?,?,?,?)",
                         (approval_id, version, principal, canonical(values), binding))

    def submit(self, approval_id, selected, values, *, fail_after_writes=False):
        self.con.execute("BEGIN IMMEDIATE")
        try:
            approval = self.con.execute(
                "SELECT expected_version,principal,values_json,reviewed_candidates_json "
                "FROM approvals WHERE approval_id=? AND record_id='R1'", (approval_id,)
            ).fetchone()
            if approval is None:
                raise Rejected("missing_approval")
            expected, principal, approved_json, binding = approval
            if principal != "reviewer-1":
                raise Rejected("principal")
            if canonical(values) != approved_json:
                raise Rejected("approved_values")
            self._check_candidates(selected, values)
            if self.policy == "candidate_bound" and canonical(selected) != binding:
                raise Rejected("candidate_binding")
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
            sources_json = None
            if self.policy == "candidate_bound":
                prior = self.con.execute(
                    "SELECT sources_json FROM versions WHERE version=?", (expected,)).fetchone()
                sources = json.loads(prior[0])
                if set(sources) != set(before):
                    raise Rejected("incomplete_source_domain")
                for field in changed:
                    sources[field] = f"v{successor}:{field}"
                sources_json = canonical(sources)
            self.con.execute("INSERT INTO versions VALUES (?,?,?)",
                             (successor, after_json, sources_json))
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
