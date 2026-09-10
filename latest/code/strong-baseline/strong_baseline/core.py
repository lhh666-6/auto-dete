"""Shared primitives: canonical JSON, database inspection, digests, clocks.

Database inspection is delegated to the *frozen B0 harness* so that B1 is
measured with exactly the same instrument as B0 (prompt v3.2, section 53/55).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from . import b0_bridge

_B0 = b0_bridge.load_b0()

#: Identical to B0's ``canonical`` (and to the E0 demonstrator's).
canonical: Callable[[Any], str] = _B0.canonical

#: Identical to B0's rejection carrier; reason strings stay comparable.
Rejected = _B0.Rejected

#: Identical to B0's external state reader (fresh connection, no ORM cache).
raw_state: Callable[[Any], dict] = _B0.raw_state
rows_as_dicts: Callable[[dict, str], list] = _B0.rows_as_dicts
reconstruct_sources_from_audit: Callable[[dict], dict] = _B0.reconstruct_sources


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Any) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return sha256_text(canonical(value))


class DeterministicClock:
    """Reproducible microsecond-free timestamps.

    The harness is a controlled experiment, so surrogate timestamps are
    injected rather than read from the wall clock.  This lets a paired
    SAFE/UNSAFE history be compared *exactly*; prompt v3.2 section 23 warns that
    wall-clock surrogates would otherwise create physical differences that say
    nothing about the semantics under test.
    """

    def __init__(self, date: str = "2026-09-10") -> None:
        self.date = date
        self.n = 0

    def __call__(self) -> str:
        self.n += 1
        return f"{self.date}T00:00:{self.n:02d}.000000+00:00"


class WallClock:
    """Non-deterministic clock, used only for the section 23 robustness run."""

    def __call__(self) -> str:
        return datetime.now(timezone.utc).isoformat()


class Counter:
    """Deterministic surrogate-id source (transaction ids, attempt sequences)."""

    def __init__(self, prefix: str, width: int = 4) -> None:
        self.prefix = prefix
        self.width = width
        self.n = 0

    def __call__(self) -> str:
        self.n += 1
        return f"{self.prefix}-{self.n:0{self.width}d}"


def table_digests(state: dict) -> dict[str, str]:
    """Per-table content digest of an externally read state."""
    return {table: digest(spec) for table, spec in sorted(state["tables"].items())}


def diff_tables(left: dict, right: dict) -> dict[str, dict]:
    """Structural difference between two externally read states, per table."""
    out: dict[str, dict] = {}
    for table in sorted(set(left["tables"]) | set(right["tables"])):
        lspec = left["tables"].get(table)
        rspec = right["tables"].get(table)
        if lspec == rspec:
            continue
        if lspec is None or rspec is None:
            out[table] = {"present_only_in": "left" if lspec else "right"}
            continue
        lcols, rcols = lspec["columns"], rspec["columns"]
        lrows = [dict(zip(lcols, r)) for r in lspec["rows"]]
        rrows = [dict(zip(rcols, r)) for r in rspec["rows"]]
        lkeys = {canonical(r) for r in lrows}
        rkeys = {canonical(r) for r in rrows}
        out[table] = {
            "columns_left": lcols,
            "columns_right": rcols,
            "only_left": sorted(lkeys - rkeys),
            "only_right": sorted(rkeys - lkeys),
            "row_counts": [len(lrows), len(rrows)],
        }
    if left.get("triggers") != right.get("triggers"):
        out["__triggers__"] = {"only_left": sorted(set(left.get("triggers", [])) - set(right.get("triggers", []))),
                               "only_right": sorted(set(right.get("triggers", [])) - set(left.get("triggers", [])))}
    return out


def foreign_keys_into(db_path: Any, target_table: str, target_column: str) -> list[dict]:
    """Every column in the schema that references ``target_table.target_column``.

    Used for the section 46 self-check: does any authority relation already name
    the exact candidate?
    """
    hits: list[dict] = []
    with closing(sqlite3.connect(db_path)) as con:
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        for table in tables:
            for row in con.execute(f'PRAGMA foreign_key_list("{table}")'):
                # (id, seq, table, from, to, on_update, on_delete, match)
                if row[2] == target_table and (row[4] or "").lower() == target_column.lower():
                    hits.append({"from_table": table, "from_column": row[3],
                                 "to_table": row[2], "to_column": row[4]})
    return hits


def columns_of(db_path: Any, table: str) -> list[str]:
    with closing(sqlite3.connect(db_path)) as con:
        return [r[1] for r in con.execute(f'PRAGMA table_info("{table}")')]


def all_columns(db_path: Any) -> dict[str, list[str]]:
    with closing(sqlite3.connect(db_path)) as con:
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        return {t: [r[1] for r in con.execute(f'PRAGMA table_info("{t}")')] for t in tables}


def loads(text: str) -> Any:
    return json.loads(text)
