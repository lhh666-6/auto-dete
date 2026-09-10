"""The two policies compared by E0-parity and E1.

``TransactionalValueAuditBaseline`` (B1)
    A conventional transactional value-audit baseline.  It is a strict
    capability superset of B0 (see ``reports/Phase1-*.md``) yet its human
    authorization is still a function of
    ``(principal, record, expected_version, authorized values, scope)`` only.
    It records **no** relation between an authorization and the exact candidate
    that was reviewed, and **no** relation between an authorization and the
    candidate that admission actually used (prompt v3.2 sections 7 and 20).

    ``variant``:
      * ``"B1"``  -- main strengthened baseline.
      * ``"B2"``  -- B2 enriched review context: the authorization additionally
        snapshots the reviewed candidate's *content* (proposal value, producer,
        producer version, evidence hash) and re-checks it at admission.  Still
        no exact candidate identity.
      * ``"B2plus"`` -- B2 plus ``admission_used_candidate`` recording.  By
        construction this makes paired histories distinguishable, so the
        "indistinguishable" claim is dropped for this variant (section 21).

``CandidateBoundPolicy`` (Full)
    The candidate-bound policy in the paper's own vocabulary: human decision
    (principal, action, reason, candidate reference) plus an immutable
    authorization-binding row (decision, exact certificate identity, authorized
    value), with content-addressed certificate identity.  Used as the
    in-process comparator so that E1's two histories differ in exactly one
    semantic element.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from .core import Rejected, canonical, sha256_text

POLICY_B1 = "transactional_value_audit"
POLICY_FULL = "candidate_bound"

POLICY_VERSION = "auto-decte.strong-baseline.b1.v1"

#: The 17-field production certificate content is mirrored here; ``created_at``
#: and the evidence locator participate, exactly as in
#: ``app/domain/authority.py:251-273``, so that "identical content, different
#: identity" is *not* constructible (R1 of the Phase 1 report).
CANDIDATE_CONTENT_FIELDS: tuple[str, ...] = (
    "record_id",
    "field",
    "proposed_json",
    "producer_id",
    "producer_version",
    "selection_artifact_id",
    "expected_fact_version",
    "evidence_hash",
    "evidence_locator",
    "created_at",
)

#: Fields a B2 review-context snapshot compares (content, not identity).
REVIEW_CONTEXT_FIELDS: tuple[str, ...] = (
    "proposed_json",
    "producer_id",
    "producer_version",
    "evidence_hash",
)

FIELDS = ("quantity", "batch")

CANDIDATE_COLUMNS = ("candidate_id", *CANDIDATE_CONTENT_FIELDS, "content_hash")


def candidate_content_hash(record: Mapping[str, Any]) -> str:
    return sha256_text(canonical({key: record[key] for key in CANDIDATE_CONTENT_FIELDS}))


def content_addressed_candidate_id(content_hash: str, prefix: str = "CERT-") -> str:
    return f"{prefix}{content_hash[:16].upper()}"


def make_candidate(clock: Callable[[], str], registry: Sequence[Mapping[str, Any]],
                   candidate_id_prefix: str = "CERT-") -> list[dict]:
    """Materialize registry rows, deriving ``created_at``, ``content_hash`` and a
    content-addressed ``candidate_id`` the way production does."""
    rows: list[dict] = []
    for spec in registry:
        record = dict(spec)
        record.setdefault("created_at", clock())
        content_hash = candidate_content_hash(record)
        record["content_hash"] = content_hash
        if record.get("candidate_id") is None:
            record["candidate_id"] = content_addressed_candidate_id(content_hash, candidate_id_prefix)
        rows.append(record)
    return rows


# --------------------------------------------------------------------------
# shared authority machinery
# --------------------------------------------------------------------------

class _AuthorityCore:
    """Transactional machinery common to every policy in this experiment.

    Deliberately *stronger* than B0 (prompt v3.2 section 5): explicit schema
    versioning, a principal registry, an enriched immutable candidate registry
    with persisted evidence hash/locator, an explicit per-field source map, a
    tamper-evident audit chain, transaction grouping, an admission decision log,
    approval-consumption (replay) protection, foreign keys, and a post-commit
    consistency check.  None of these additions name a candidate in any
    authority relation.
    """

    policy: str = "unknown"
    records_candidate_identity_in_authorization = False  # asserted by the section 46 check
    records_used_candidate = False

    def __init__(self, path: str | Path, *, candidates: Sequence[Mapping[str, Any]],
                 principals: Mapping[str, Sequence[str]] | None = None,
                 initial_values: Mapping[str, Any] | None = None,
                 clock: Callable[[], str], tx_ids: Callable[[], str],
                 record_id: str = "R1") -> None:
        self.path = Path(path)
        if self.path.exists():
            raise FileExistsError(f"Use a fresh database; never overwrite a prior run: {self.path}")
        self.record_id = record_id
        self.clock = clock
        self.tx_ids = tx_ids
        self.con = sqlite3.connect(self.path, isolation_level=None)
        self.con.execute("PRAGMA foreign_keys=ON")
        self.con.execute("PRAGMA synchronous=FULL")
        self.con.execute("PRAGMA busy_timeout=5000")
        self._create_schema()
        self._seed(principals or {"reviewer-1": ("reviewer", list(FIELDS))},
                   candidates, initial_values or {"quantity": 90, "batch": "A"})

    # -- schema ------------------------------------------------------------
    def _create_schema(self) -> None:
        self.con.executescript("""
            CREATE TABLE schema_meta (
                policy TEXT PRIMARY KEY,
                schema_name TEXT NOT NULL,
                schema_version INTEGER NOT NULL,
                created_at TEXT NOT NULL);
            CREATE TABLE principals (
                principal_id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                authorized_fields_json TEXT NOT NULL,
                active INTEGER NOT NULL CHECK (active IN (0,1)));
            CREATE TABLE candidates (
                candidate_id TEXT PRIMARY KEY,
                record_id TEXT NOT NULL,
                field TEXT NOT NULL,
                proposed_json TEXT NOT NULL,
                producer_id TEXT NOT NULL,
                producer_version TEXT NOT NULL,
                selection_artifact_id TEXT NOT NULL,
                expected_fact_version INTEGER NOT NULL CHECK (expected_fact_version >= 0),
                evidence_hash TEXT NOT NULL,
                evidence_locator TEXT NOT NULL,
                created_at TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                UNIQUE (content_hash));
            CREATE TABLE records (
                record_id TEXT PRIMARY KEY,
                version INTEGER NOT NULL,
                values_json TEXT NOT NULL);
            CREATE TABLE versions (
                version INTEGER PRIMARY KEY,
                values_json TEXT NOT NULL,
                sources_json TEXT NOT NULL);
            CREATE TABLE audits (
                audit_seq INTEGER PRIMARY KEY,
                tx_id TEXT NOT NULL,
                version INTEGER NOT NULL REFERENCES versions(version),
                approval_id TEXT NOT NULL,
                principal TEXT NOT NULL,
                before_json TEXT NOT NULL,
                after_json TEXT NOT NULL,
                changed_fields_json TEXT NOT NULL,
                before_digest TEXT NOT NULL,
                after_digest TEXT NOT NULL,
                prev_row_digest TEXT NOT NULL,
                row_digest TEXT NOT NULL);
            CREATE TABLE fact_sources (
                record_id TEXT NOT NULL,
                field TEXT NOT NULL,
                source_version INTEGER NOT NULL,
                source_kind TEXT NOT NULL,
                approval_id TEXT,
                PRIMARY KEY (record_id, field));
            CREATE TABLE admission_attempts (
                attempt_seq INTEGER PRIMARY KEY,
                tx_id TEXT NOT NULL,
                approval_id TEXT NOT NULL,
                outcome TEXT NOT NULL CHECK (outcome IN ('accepted','rejected')),
                reason TEXT NOT NULL,
                observed_version INTEGER,
                attempted_values_json TEXT NOT NULL,
                recorded_at TEXT NOT NULL);
            CREATE TABLE approval_consumption (
                approval_id TEXT PRIMARY KEY,
                consumed_version INTEGER NOT NULL,
                consumed_at TEXT NOT NULL,
                tx_id TEXT NOT NULL);
            CREATE TABLE tx_log (
                tx_id TEXT PRIMARY KEY,
                opened_at TEXT NOT NULL,
                settled_at TEXT,
                status TEXT NOT NULL);
        """)
        self._create_policy_tables()
        if self.records_used_candidate:
            # B2+ robustness variant only (section 21): the audit records which
            # candidate admission used, but still not which one was reviewed.
            self.con.execute("ALTER TABLE admission_attempts "
                             "ADD COLUMN used_candidate_json TEXT")
        immutable = ("schema_meta", "principals", "candidates", "versions", "audits",
                     "approval_consumption") + tuple(self._policy_immutable_tables())
        for table in immutable:
            for action in ("UPDATE", "DELETE"):
                self.con.execute(
                    f"CREATE TRIGGER freeze_{table}_{action} BEFORE {action} ON {table} "
                    "BEGIN SELECT RAISE(ABORT, 'immutable history'); END")

    def _create_policy_tables(self) -> None:  # pragma: no cover - overridden
        raise NotImplementedError

    def _policy_immutable_tables(self) -> Iterable[str]:  # pragma: no cover - overridden
        return ()

    # -- seeding -----------------------------------------------------------
    def _seed(self, principals: Mapping[str, Sequence[str]], candidates: Sequence[Mapping[str, Any]],
              initial_values: Mapping[str, Any]) -> None:
        self.con.execute("INSERT INTO schema_meta VALUES (?,?,?,?)",
                         (self.policy, f"auto-decte.strong-baseline.{self.policy}", 1, self.clock()))
        for principal_id, (role, fields) in sorted(principals.items()):
            self.con.execute("INSERT INTO principals VALUES (?,?,?,1)",
                             (principal_id, role, canonical(list(fields))))
        columns = ", ".join(CANDIDATE_COLUMNS)
        placeholders = ", ".join("?" for _ in CANDIDATE_COLUMNS)
        self.con.executemany(
            f"INSERT INTO candidates ({columns}) VALUES ({placeholders})",
            [tuple(row[key] for key in CANDIDATE_COLUMNS) for row in candidates])
        initial = canonical(initial_values)
        self.con.execute("INSERT INTO records VALUES (?,0,?)", (self.record_id, initial))
        sources = canonical({field: f"v0:{field}" for field in initial_values})
        self.con.execute("INSERT INTO versions VALUES (0,?,?)", (initial, sources))
        self.con.executemany("INSERT INTO fact_sources VALUES (?,?,0,'initial',NULL)",
                             [(self.record_id, field) for field in sorted(initial_values)])

    # -- helpers -----------------------------------------------------------
    def close(self) -> None:
        self.con.close()

    def candidate(self, candidate_id: str) -> dict | None:
        row = self.con.execute(
            f"SELECT {', '.join(CANDIDATE_COLUMNS)} FROM candidates WHERE candidate_id=?",
            (candidate_id,)).fetchone()
        return dict(zip(CANDIDATE_COLUMNS, row)) if row else None

    def _principal(self, principal: str) -> tuple[str, list[str]]:
        row = self.con.execute(
            "SELECT role, authorized_fields_json, active FROM principals WHERE principal_id=?",
            (principal,)).fetchone()
        if row is None or row[2] != 1:
            raise Rejected("principal")
        return row[0], list(__import__("json").loads(row[1]))

    def context_of(self, candidate: Mapping[str, Any]) -> str:
        """The review context B2 snapshots: content, never identity."""
        return canonical({key: candidate[key] for key in REVIEW_CONTEXT_FIELDS})

    def _check_candidate_context(self, selected: Mapping[str, str], fields: Iterable[str]) -> None:
        if set(selected) != set(fields):
            raise Rejected("field_domain")
        for field, candidate_id in selected.items():
            row = self.con.execute(
                "SELECT record_id, field FROM candidates WHERE candidate_id=?",
                (candidate_id,)).fetchone()
            if row != (self.record_id, field):
                raise Rejected("candidate_context")

    def _authorized_domain(self, values: Mapping[str, Any], principal: str) -> None:
        if not values:
            raise ValueError("empty approval domain")
        _, fields = self._principal(principal)
        if not set(values) <= set(fields):
            raise Rejected("field_domain")

    # -- write path --------------------------------------------------------
    def _next_audit_seq(self) -> int:
        return (self.con.execute("SELECT COALESCE(MAX(audit_seq),0) FROM audits").fetchone()[0] or 0) + 1

    def _commit_successor(self, *, tx_id: str, handle: str, principal: str,
                          expected: int, selected: Mapping[str, str],
                          values: Mapping[str, Any]) -> dict:
        before_json = self.con.execute(
            "SELECT values_json FROM records WHERE record_id=?", (self.record_id,)).fetchone()[0]
        before = __import__("json").loads(before_json)
        after = {**before, **values}
        changed = {field for field in before
                   if canonical(before[field]) != canonical(after[field])}
        if changed != set(values):
            raise Rejected("changed_domain")
        successor = expected + 1
        after_json = canonical(after)
        updated = self.con.execute(
            "UPDATE records SET version=?, values_json=? WHERE record_id=? AND version=?",
            (successor, after_json, self.record_id, expected))
        if updated.rowcount != 1:
            raise Rejected("stale_version")

        prior = self.con.execute(
            "SELECT sources_json FROM versions WHERE version=?", (expected,)).fetchone()
        sources = __import__("json").loads(prior[0])
        if set(sources) != set(before):  # total source map required
            raise Rejected("incomplete_source_domain")
        for field in changed:
            sources[field] = f"v{successor}:{field}"
        sources_json = canonical(sources)

        self.con.execute("INSERT INTO versions VALUES (?,?,?)", (successor, after_json, sources_json))
        for field in sorted(sources):
            self.con.execute(
                "INSERT INTO fact_sources VALUES (?,?,?,?,?) "
                "ON CONFLICT(record_id, field) DO UPDATE SET "
                "source_version=excluded.source_version, source_kind=excluded.source_kind, "
                "approval_id=excluded.approval_id",
                (self.record_id, field, successor, "human_authorized", handle))

        seq = self._next_audit_seq()
        prev = self.con.execute(
            "SELECT COALESCE(MAX(audit_seq),0) FROM audits").fetchone()[0] or 0
        prev_digest = "GENESIS"
        if prev:
            prev_digest = self.con.execute(
                "SELECT row_digest FROM audits WHERE audit_seq=?", (prev,)).fetchone()[0]
        payload = canonical({"tx_id": tx_id, "version": successor, "approval_id": handle,
                             "principal": principal, "before": before_json, "after": after_json,
                             "changed": sorted(changed), "before_digest": sha256_text(before_json),
                             "after_digest": sha256_text(after_json), "prev": prev_digest})
        self.con.execute(
            "INSERT INTO audits (audit_seq, tx_id, version, approval_id, principal, before_json, "
            "after_json, changed_fields_json, before_digest, after_digest, prev_row_digest, "
            "row_digest) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                         (seq, tx_id, successor, handle, principal, before_json, after_json,
                          canonical(sorted(changed)), sha256_text(before_json),
                          sha256_text(after_json), prev_digest, sha256_text(payload)))
        return {"successor": successor, "before_json": before_json, "after_json": after_json,
                "changed": sorted(changed), "sources": sources}

    # -- transaction scaffold ---------------------------------------------
    def _record_attempt(self, *, tx_id: str, handle: str, outcome: str, reason: str,
                        observed_version: int | None, values: Mapping[str, Any],
                        used_candidate: Mapping[str, str] | None = None) -> None:
        """Append one admission-decision row.

        The row records the decision and its reason code.  In the B1/B2 variants
        it deliberately records **no** candidate identity; only the optional
        ``B2plus`` robustness variant adds ``used_candidate_json`` (section 21).
        """
        seq = (self.con.execute("SELECT COALESCE(MAX(attempt_seq),0) FROM admission_attempts")
               .fetchone()[0] or 0) + 1
        body = {
            "attempt_seq": seq,
            "tx_id": tx_id,
            "approval_id": handle,
            "outcome": outcome,
            "reason": reason,
            "observed_version": observed_version,
            "attempted_values_json": canonical(values),
            "recorded_at": self.clock(),
        }
        if self.records_used_candidate:
            body["used_candidate_json"] = canonical(used_candidate)
        columns = list(body)
        self.con.execute(
            f"INSERT INTO admission_attempts ({', '.join(columns)}) "
            f"VALUES ({', '.join('?' for _ in columns)})",
            tuple(body[column] for column in columns))

    def _settle(self, tx_id: str, status: str) -> None:
        self.con.execute("UPDATE tx_log SET settled_at=?, status=? WHERE tx_id=?",
                         (self.clock(), status, tx_id))

    def submit(self, handle: str, selected: Mapping[str, str], values: Mapping[str, Any], *,
               fail_after_writes: bool = False) -> dict:
        """Admission of ``values`` under the authorization identified by ``handle``.

        ``selected`` is the admission-time candidate handle per field.  The
        policy decides whether that handle is *named* by the authorization (Full)
        or merely context-checked (B1/B2).
        """
        tx_id = self.tx_ids()
        self.con.execute("BEGIN IMMEDIATE")
        self.con.execute("INSERT INTO tx_log VALUES (?,?,NULL,'open')", (tx_id, self.clock()))
        try:
            outcome = self._submit_inner(tx_id, handle, selected, values,
                                         fail_after_writes=fail_after_writes)
            self._settle(tx_id, "committed")
            self.con.execute("COMMIT")
            return outcome
        except Rejected as exc:
            self.con.execute("ROLLBACK")
            return {"accepted": False, "reason": str(exc)}
        except Exception:
            self.con.execute("ROLLBACK")
            raise

    def _submit_inner(self, tx_id, handle, selected, values, *, fail_after_writes):  # pragma: no cover
        raise NotImplementedError


# --------------------------------------------------------------------------
# B1 / B2 / B2+
# --------------------------------------------------------------------------

class TransactionalValueAuditBaseline(_AuthorityCore):
    """Conventional transactional value-audit baseline (value-bound approval)."""

    def __init__(self, path, *, variant: str = "B1", **kwargs) -> None:
        if variant not in {"B1", "B2", "B2plus"}:
            raise ValueError("variant must be B1, B2 or B2plus")
        self.variant = variant
        self.policy = variant if variant != "B1" else POLICY_B1
        self.records_used_candidate = variant == "B2plus"
        self.records_candidate_identity_in_authorization = False
        super().__init__(path, **kwargs)

    def _create_policy_tables(self) -> None:
        self.con.executescript("""
            CREATE TABLE approvals (
                approval_id TEXT PRIMARY KEY,
                record_id TEXT NOT NULL,
                expected_version INTEGER NOT NULL,
                principal TEXT NOT NULL REFERENCES principals(principal_id),
                approved_values_json TEXT NOT NULL,
                scope_json TEXT NOT NULL,
                policy_version TEXT NOT NULL,
                requested_at TEXT NOT NULL,
                reviewed_context_json TEXT,
                reviewed_per_field_json TEXT);
        """)

    def _policy_immutable_tables(self) -> Iterable[str]:
        return ("approvals", "admission_attempts")

    # -- approval ----------------------------------------------------------
    def approve(self, approval_id: str, selected: Mapping[str, str],
                values: Mapping[str, Any], principal: str = "reviewer-1") -> None:
        self._authorized_domain(values, principal)
        self._check_candidate_context(selected, values)
        version = self.con.execute("SELECT version FROM records WHERE record_id=?",
                                   (self.record_id,)).fetchone()[0]
        reviewed_context = None
        reviewed_per_field = None
        if self.variant in {"B2", "B2plus"}:
            per_field = {}
            for field in sorted(selected):
                candidate = self.candidate(selected[field])
                per_field[field] = {key: candidate[key] for key in REVIEW_CONTEXT_FIELDS}
            reviewed_per_field = canonical(per_field)
            reviewed_context = canonical(
                {key: per_field[sorted(per_field)[0]][key] for key in REVIEW_CONTEXT_FIELDS}
                if len(per_field) == 1 else per_field)
        self.con.execute(
            "INSERT INTO approvals VALUES (?,?,?,?,?,?,?,?,?,?)",
            (approval_id, self.record_id, version, principal, canonical(values),
             canonical(sorted(values)), POLICY_VERSION, self.clock(),
             reviewed_context, reviewed_per_field))

    # -- admission ---------------------------------------------------------
    def _submit_inner(self, tx_id, handle, selected, values, *, fail_after_writes):
        row = self.con.execute(
            "SELECT expected_version, principal, approved_values_json, reviewed_per_field_json "
            "FROM approvals WHERE approval_id=? AND record_id=?", (handle, self.record_id)).fetchone()
        if row is None:
            raise Rejected("missing_approval")
        expected, principal, approved_json, reviewed_per_field = row
        observed = self.con.execute("SELECT version FROM records WHERE record_id=?",
                                    (self.record_id,)).fetchone()[0]
        self._principal(principal)
        if canonical(values) != approved_json:
            raise Rejected("approved_values")
        self._check_candidate_context(selected, values)
        if self.variant in {"B2", "B2plus"} and reviewed_per_field is not None:
            snapshot = __import__("json").loads(reviewed_per_field)
            for field, candidate_id in sorted(selected.items()):
                candidate = self.candidate(candidate_id)
                if {key: candidate[key] for key in REVIEW_CONTEXT_FIELDS} != snapshot[field]:
                    raise Rejected("reviewed_context")
        consumed = self.con.execute("SELECT consumed_version FROM approval_consumption WHERE approval_id=?",
                                    (handle,)).fetchone()
        if consumed is not None:
            raise Rejected("approval_already_consumed")
        result = self._commit_successor(tx_id=tx_id, handle=handle, principal=principal,
                                        expected=expected, selected=selected, values=values)
        self.con.execute("INSERT INTO approval_consumption VALUES (?,?,?,?)",
                         (handle, result["successor"], self.clock(), tx_id))
        self._record_attempt(tx_id=tx_id, handle=handle, outcome="accepted", reason="committed",
                             observed_version=observed, values=values,
                             used_candidate=None if not self.records_used_candidate
                             else dict(selected))
        if fail_after_writes:
            raise Rejected("injected_failure")
        return {"accepted": True, "reason": "committed", "successor": result["successor"]}


# --------------------------------------------------------------------------
# Full / candidate-bound
# --------------------------------------------------------------------------

class CandidateBoundPolicy(_AuthorityCore):
    """Candidate-bound admission using the paper's real implementation vocabulary."""

    policy = POLICY_FULL
    records_candidate_identity_in_authorization = True

    def __init__(self, path, **kwargs) -> None:
        super().__init__(path, **kwargs)

    def _create_policy_tables(self) -> None:
        self.con.executescript("""
            CREATE TABLE decisions (
                decision_id TEXT PRIMARY KEY,
                principal TEXT NOT NULL REFERENCES principals(principal_id),
                action TEXT NOT NULL CHECK (action IN ('authorize')),
                reason TEXT NOT NULL,
                expected_version INTEGER NOT NULL,
                candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id),
                created_at TEXT NOT NULL);
            CREATE TABLE authorization_bindings (
                binding_seq INTEGER PRIMARY KEY,
                decision_id TEXT NOT NULL REFERENCES decisions(decision_id),
                field TEXT NOT NULL,
                certificate_id TEXT NOT NULL REFERENCES candidates(candidate_id),
                authorized_value_json TEXT NOT NULL,
                principal TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE (decision_id, field));
        """)

    def _policy_immutable_tables(self) -> Iterable[str]:
        return ("decisions", "authorization_bindings", "admission_attempts")

    def authorize(self, decision_id: str, selected: Mapping[str, str], values: Mapping[str, Any],
                  principal: str = "reviewer-1", reason: str = "reviewed candidate") -> None:
        self._authorized_domain(values, principal)
        self._check_candidate_context(selected, values)
        version = self.con.execute("SELECT version FROM records WHERE record_id=?",
                                   (self.record_id,)).fetchone()[0]
        primary = sorted(selected)[0]
        self.con.execute("INSERT INTO decisions VALUES (?,?,?,?,?,?,?)",
                         (decision_id, principal, "authorize", reason, version,
                          selected[primary], self.clock()))
        seq = (self.con.execute("SELECT COALESCE(MAX(binding_seq),0) FROM authorization_bindings")
               .fetchone()[0] or 0) + 1
        for field in sorted(selected):
            self.con.execute("INSERT INTO authorization_bindings VALUES (?,?,?,?,?,?,?)",
                             (seq, decision_id, field, selected[field],
                              canonical({field: values[field]}), principal, self.clock()))
            seq += 1

    def _bound(self, handle: str) -> dict[str, str]:
        rows = self.con.execute(
            "SELECT field, certificate_id FROM authorization_bindings WHERE decision_id=?",
            (handle,)).fetchall()
        return {field: certificate_id for field, certificate_id in rows}

    def _submit_inner(self, tx_id, handle, selected, values, *, fail_after_writes):
        row = self.con.execute(
            "SELECT principal, expected_version FROM decisions WHERE decision_id=?",
            (handle,)).fetchone()
        if row is None:
            raise Rejected("missing_approval")
        principal, expected = row
        observed = self.con.execute("SELECT version FROM records WHERE record_id=?",
                                    (self.record_id,)).fetchone()[0]
        self._principal(principal)
        bound = self._bound(handle)
        authorized = {}
        for field, certificate_id in bound.items():
            authorized[field] = __import__("json").loads(self.con.execute(
                "SELECT authorized_value_json FROM authorization_bindings "
                "WHERE decision_id=? AND field=?", (handle, field)).fetchone()[0])[field]
        if canonical(values) != canonical(authorized):
            raise Rejected("approved_values")
        self._check_candidate_context(selected, values)
        if dict(selected) != bound:
            raise Rejected("candidate_binding")
        consumed = self.con.execute("SELECT consumed_version FROM approval_consumption WHERE approval_id=?",
                                    (handle,)).fetchone()
        if consumed is not None:
            raise Rejected("approval_already_consumed")
        result = self._commit_successor(tx_id=tx_id, handle=handle, principal=principal,
                                        expected=expected, selected=selected, values=values)
        self.con.execute("INSERT INTO approval_consumption VALUES (?,?,?,?)",
                         (handle, result["successor"], self.clock(), tx_id))
        self._record_attempt(tx_id=tx_id, handle=handle, outcome="accepted", reason="committed",
                             observed_version=observed, values=values,
                             used_candidate=None if not self.records_used_candidate
                             else dict(selected))
        if fail_after_writes:
            raise Rejected("injected_failure")
        return {"accepted": True, "reason": "committed", "successor": result["successor"]}


POLICY_CLASSES = {
    POLICY_B1: TransactionalValueAuditBaseline,
    POLICY_FULL: CandidateBoundPolicy,
}


def open_policy(policy: str, path, **kwargs) -> _AuthorityCore:
    if policy == POLICY_FULL:
        return CandidateBoundPolicy(path, **kwargs)
    if policy in {POLICY_B1, "B2", "B2plus"}:
        variant = "B1" if policy == POLICY_B1 else policy
        return TransactionalValueAuditBaseline(path, variant=variant, **kwargs)
    raise ValueError(f"unknown policy {policy!r}")


def publish(policy_object: _AuthorityCore, handle: str, selected, values, principal="reviewer-1"):
    """Uniform authorization entry point so one case runner can drive both policies."""
    if isinstance(policy_object, CandidateBoundPolicy):
        return policy_object.authorize(handle, selected, values, principal)
    return policy_object.approve(handle, selected, values, principal)
