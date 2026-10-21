"""Thin public-order adapters over the existing, byte-pinned implementations.

An entire public order is represented by FORM-1 in one isolated database.
Each top-level order key is a field; address is one JSON-valued field. The
public benchmark provides neither these certificates nor their provenance.
Only SQLite is authoritative. Native Retail executes on a projection/clone.
"""
from __future__ import annotations

from copy import deepcopy
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parent
CONTRACT = ROOT / "vendor" / "contract"
SUPPLEMENT = CONTRACT / "DKE-supplement"


def verify_sources():
    manifest = json.loads((ROOT / "contract-source-manifest.json").read_text(encoding="utf-8"))
    for artifact in manifest["artifacts"]:
        path = ROOT / artifact["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise ValueError(f"Pinned contract source changed: {artifact['path']}")
    return {"files": len(manifest["artifacts"]), "unchanged": True}


verify_sources()
sys.dont_write_bytecode = True
sys.path.insert(0, str(SUPPLEMENT))
from common import canonical, digest  # noqa: E402
from journal import Journal  # noqa: E402
from reference import Reference, packet  # noqa: E402


class Store:
    """Uniform interface; admission decisions remain in the original engines.

    Strong = author-built Journal(exact=True), not an external SOTA system.
    Full = original ReviewForms prepare + original repository admission.
    Native = HITL's approved actual arguments, with shared atomic snapshots
    but no additional candidate or approval-time predecessor checks.
    """

    def __init__(self, route, path, initial_order, *, timestamp=None):
        if route not in {"native", "strong", "full"}:
            raise ValueError(route)
        self.route = route
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            raise FileExistsError(f"Refuse to overwrite existing authority: {self.path}")
        self.fields = frozenset(initial_order)
        if "address" not in self.fields:
            raise ValueError("Public order requires address")
        self.timestamp = datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else timestamp
        self.timestamp = self.timestamp or datetime.now(timezone.utc)
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("Use an aware run timestamp")
        self.engine = None
        self.con = None
        self._packets = {}
        self._external_count = 0
        if route == "native":
            self.con = sqlite3.connect(self.path, isolation_level=None)
            self.con.executescript("""PRAGMA synchronous=FULL; PRAGMA busy_timeout=5000;
                CREATE TABLE head(id INTEGER PRIMARY KEY, version INTEGER NOT NULL);
                INSERT INTO head VALUES(1,1);
                CREATE TABLE versions(version INTEGER PRIMARY KEY, values_json TEXT NOT NULL);
                CREATE TABLE previews(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
            """)
            self.con.execute("INSERT INTO versions VALUES(1,?)", (canonical(initial_order),))
        else:
            self.engine = Journal(self.path, self.fields, exact=True) if route == "strong" else Reference(self.path, self.fields)
            ids = {}
            for field in sorted(self.fields):
                p = self._packet(field, initial_order[field], 0, f"seed:{initial_order.get('order_id', 'order')}:{field}", "public-order-seed")
                self._add(p)
                ids[field] = p["id"]
            self.engine.confirm(0, deepcopy(initial_order), ids)

    def _packet(self, field, proposed, version, nonce, evidence):
        return packet(field, deepcopy(proposed), version, nonce, evidence=evidence, now=self.timestamp)

    def _add(self, p):
        self._packets[p["id"]] = deepcopy(p)
        if self.engine is not None:
            self.engine.add(p)

    def snapshot(self):
        """Read fresh SQLite state, never a cached planner or Retail clone."""
        with closing(sqlite3.connect(self.path)) as con:
            con.row_factory = sqlite3.Row
            if self.route == "native":
                row = con.execute("SELECT version, values_json FROM versions ORDER BY version DESC LIMIT 1").fetchone()
                return {"version": row["version"], "values": json.loads(row["values_json"]), "sources": None}
            if self.route == "strong":
                row = con.execute("SELECT version, values_json, sources_json FROM versions ORDER BY version DESC LIMIT 1").fetchone()
                return {"version": row["version"], "values": json.loads(row["values_json"]), "sources": json.loads(row["sources_json"])}
            row = con.execute("SELECT version, \"values\", fact_sources FROM record_versions WHERE form_id='FORM-1' ORDER BY version DESC LIMIT 1").fetchone()
            return {"version": row["version"], "values": json.loads(row["values"]), "sources": json.loads(row["fact_sources"])}

    def prepare(self, proposed_address, authorized_address, nonce, evidence):
        before = self.snapshot()
        return self._prepare_fields(before, {"address": proposed_address}, {"address": authorized_address}, nonce, evidence)

    def _prepare_fields(self, before, proposed_values, authorized_values, nonce, evidence):
        ids = {}
        packets = {}
        for field in sorted(authorized_values):
            p = self._packet(field, proposed_values[field], before["version"], f"{nonce}:{field}", evidence)
            self._add(p)
            ids[field] = p["id"]
            packets[field] = p
        successor = deepcopy(before["values"])
        successor.update(deepcopy(authorized_values))
        preview = {"nonce": nonce, "record_id": "FORM-1", "public_order_id": before["values"].get("order_id"),
                   "expected_version": before["version"], "proposal": deepcopy(proposed_values),
                   "authorized": deepcopy(authorized_values), "candidate_ids": ids,
                   "candidate_packets": packets, "complete_successor": successor}
        if self.route == "native":
            approval = "N-" + digest(preview)
            self.con.execute("INSERT INTO previews VALUES(?,?)", (approval, canonical(preview)))
        else:
            approval = self.engine.prepare(before["version"], deepcopy(authorized_values), ids)
        return {"version": before["version"], "approval": approval, "ids": ids, "candidate_ids": deepcopy(ids),
                "packets": packets, "preview": preview}

    def commit(self, handle, actual_order, *, candidate_swap=False, failpoint=None):
        if set(actual_order) != self.fields:
            # The representation contract is identical for all routes. This is
            # a schema error, not a result of the authorization comparison.
            raise ValueError("Adapter requires one complete public-order record")
        before = self.snapshot()
        ids = deepcopy(handle["ids"])
        if candidate_swap:
            if self.route == "native":
                raise ValueError("Candidate substitution control is not applicable to native parameter binding")
            for field, original in handle["packets"].items():
                # Preserve the reviewed context exactly; only instance identity
                # changes. Reconstruct certificate ID from that frozen context.
                from reference import certificate
                p = deepcopy(original) | {"candidate_id": original["candidate_id"] + ":substitute"}
                p["id"] = certificate(p).certificate_id
                self._add(p)
                ids[field] = p["id"]
        try:
            if self.route == "native":
                self.con.execute("BEGIN IMMEDIATE")
                try:
                    current = self.con.execute("SELECT version FROM head WHERE id=1").fetchone()[0]
                    # This counter is serialization bookkeeping, not a check
                    # against the version that was observed during approval.
                    self.con.execute("UPDATE head SET version=? WHERE id=1", (current + 1,))
                    if failpoint == "after_cas":
                        raise RuntimeError("INJECTED:after_cas")
                    self.con.execute("INSERT INTO versions VALUES(?,?)", (current + 1, canonical(actual_order)))
                    if failpoint == "before_commit":
                        raise RuntimeError("INJECTED:before_commit")
                    self.con.commit()
                except Exception:
                    self.con.rollback()
                    raise
            elif self.route == "strong":
                self.engine.admit(handle["approval"], ids, values=deepcopy(actual_order), failpoint=failpoint)
            else:
                # The native adapter's prepared immutable authorization remains
                # intact. Supply actual Retail successor values to the native
                # repository so its own checks decide acceptance/rejection.
                approval = deepcopy(handle["approval"])
                approval["record"].values = deepcopy(actual_order)
                self.engine.admit(approval, ids, values=deepcopy(actual_order), failpoint=failpoint)
            status, reason, error_type = "COMMITTED", None, None
        except Exception as exc:
            status = "ROLLED_BACK" if str(exc).startswith("INJECTED:") else ("REJECTED" if isinstance(exc, ValueError) else "ERROR")
            reason, error_type = str(exc), type(exc).__name__
        after = self.snapshot()
        return {"status": status, "reason": reason, "error_type": error_type,
                "version_before": before["version"], "version_after": after["version"],
                "used_candidate_ids": ids, "reviewed_candidate_ids": deepcopy(handle["ids"])}

    def external_change(self, new_order):
        before = self.snapshot()
        changed = {f: deepcopy(v) for f, v in new_order.items() if canonical(v) != canonical(before["values"].get(f))}
        if not changed:
            raise ValueError("External change must change at least one field")
        self._external_count += 1
        handle = self._prepare_fields(before, changed, changed, f"external:{self._external_count}", "controlled-independent-transaction")
        outcome = self.commit(handle, new_order)
        if outcome["status"] != "COMMITTED":
            raise RuntimeError(f"External transaction failed: {outcome}")
        return outcome

    def dump(self):
        with closing(sqlite3.connect(self.path)) as con:
            con.row_factory = sqlite3.Row
            names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
            return {name: sorted([dict(r) for r in con.execute('SELECT * FROM "' + name.replace('"', '""') + '"')], key=canonical) for name in names}

    def trace(self):
        """Optional actual authority lineage query; native has no such schema."""
        return self.engine.query() if self.engine is not None else None

    def close(self):
        if self.engine is not None:
            self.engine.close()
        if self.con is not None:
            self.con.close()
        # The unmodified upstream query helper uses SQLite transaction context
        # managers; collect any unreachable read connections on Windows.
        import gc
        gc.collect()
