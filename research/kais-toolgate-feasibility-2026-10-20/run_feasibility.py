"""Freeze and run eight developmental controls; every execution gets a new folder."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sqlite3
import sys
import traceback
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
SPRINT = ROOT.parent / "kais-external-baseline-sprint-2026-10-15"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as output:
        json.dump(value, output, ensure_ascii=False, indent=2)
        output.write("\n")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump_sql(path):
    with closing(sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)) as con:
        con.row_factory = sqlite3.Row
        names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {
            name: sorted(
                [dict(r) for r in con.execute('SELECT * FROM "' + name.replace('"', '""') + '"')],
                key=lambda row: json.dumps(row, sort_keys=True),
            )
            for name in names
        }


def path_entry(path, expected=None):
    path = Path(path).resolve()
    actual = sha(path)
    if expected is not None and actual != expected:
        raise ValueError(f"Preserved source mismatch: {path}")
    return {"path": path.as_posix(), "sha256": actual}


def freeze():
    local = ["PROTOCOL.md", "cases.json", "requirements.txt", "run_feasibility.py",
             "toolgate_adapter.py", "contract_adapter.py", "score_feasibility.py"]
    entries = [path_entry(ROOT / name) for name in local]
    for item in read(ROOT / "UPSTREAM-SOURCE.json")["files"]:
        entries.append(path_entry(ROOT / item["path"], item["sha256"]))
    entries.append(path_entry(SPRINT / "stores.py"))
    for item in read(SPRINT / "contract-source-manifest.json")["artifacts"]:
        entries.append(path_entry(SPRINT / item["path"], item["sha256"]))
    protected = []
    for item in read(ROOT.parent / "kais-rejection-comparison-2026-10-20/OUTPUT-VERIFICATION.json")["protected_files"]:
        path = Path(item["path"])
        protected.append(path_entry(path if path.is_absolute() else PROJECT / path, item["sha256"]))
    result = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "type": "developmental-control-freeze-not-heldout-or-preregistration",
        "cases": 8, "conditions": ["T-configured", "C"],
        "outside_mainline_scenarios": 0,
        "files": entries, "protected_files": protected,
    }
    write_new(ROOT / "FREEZE.json", result)
    print(json.dumps({"frozen_sources": len(entries), "protected_files": len(protected)}))


def verify_frozen():
    frozen = read(ROOT / "FREEZE.json")
    for item in frozen["files"] + frozen["protected_files"]:
        path_entry(item["path"], item["sha256"])
    return frozen


def run():
    frozen = verify_frozen()
    folder = ROOT / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder.mkdir(parents=True, exist_ok=False)
    write_new(folder / "freeze.json", frozen)
    cases = read(ROOT / "cases.json")
    write_new(folder / "cases.json", cases)
    network_attempts = []

    def deny_network(event, args):
        if event in {"socket.connect", "socket.getaddrinfo", "socket.sendto"}:
            network_attempts.append(event)
            raise RuntimeError("This development run prohibits network/model calls")

    sys.addaudithook(deny_network)
    import toolgate_adapter
    import contract_adapter

    environment = {
        "python": sys.version, "platform": platform.platform(),
        "sqlite": sqlite3.sqlite_version,
        "packages": {p: importlib.metadata.version(p) for p in
                     ["numpy", "SQLAlchemy", "greenlet", "typing_extensions"]},
        "network_access_during_run": "denied by Python audit hook",
        "hosted_model_calls": 0,
    }
    write_new(folder / "environment.json", environment)
    records = []
    for case in cases:
        # Expected labels are confined to the scorer, never passed to either gate.
        fixture = {k: v for k, v in case.items() if k != "expected_write"}
        for method, adapter in [("T-configured", toolgate_adapter), ("C", contract_adapter)]:
            arm = folder / case["id"] / method
            arm.mkdir(parents=True, exist_ok=False)
            try:
                record = adapter.run_case(json.loads(json.dumps(fixture)), arm)
                db = Path(record["db_path"]).resolve()
                record["db_path"] = db.name
                record["engineering_status"] = "COMPLETE"
                record["sql_after_path"] = "sql_after.json"
                write_new(arm / "sql_after.json", dump_sql(db))
                if "sql_before" in record:
                    write_new(arm / "sql_before.json", record.pop("sql_before"))
                    record["sql_before_path"] = "sql_before.json"
                record.pop("sql_after", None)
            except Exception as error:
                record = {
                    "method": method, "case_id": case["id"],
                    "engineering_status": "ERROR", "error_type": type(error).__name__,
                    "error": str(error), "traceback": traceback.format_exc(),
                }
            write_new(arm / "record.json", record)
            records.append({
                "case_id": case["id"], "method": method,
                "status": record["engineering_status"],
                "record": (arm / "record.json").relative_to(folder).as_posix(),
            })
    verify_frozen()
    receipt = {
        "run_dir": folder.as_posix(), "records": records,
        "complete": sum(r["status"] == "COMPLETE" for r in records),
        "errors": sum(r["status"] != "COMPLETE" for r in records),
        "network_attempts": network_attempts,
        "sources_and_protected_files_unchanged": True,
    }
    write_new(folder / "RUN.json", receipt)
    print(json.dumps({"run_dir": folder.as_posix(), "complete": receipt["complete"],
                      "errors": receipt["errors"], "network_attempts": len(network_attempts)}))
    if receipt["errors"] or network_attempts:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["freeze", "run"])
    args = parser.parse_args()
    freeze() if args.action == "freeze" else run()
