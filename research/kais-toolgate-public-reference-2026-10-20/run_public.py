"""Freeze inputs, run both configured boundaries, and execute native suffixes."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import shutil
import sqlite3
import sys
import traceback

sys.dont_write_bytecode = True
from public_io import ROOT, FEASIBILITY, PILOT, read, save, sha, dump_sql


def entry(path, expected=None):
    path = Path(path).resolve()
    actual = sha(path)
    if expected is not None and actual != expected:
        raise ValueError(f"Preserved input changed: {path}")
    return {"path": path.as_posix(), "sha256": actual}


def freeze():
    previous = read(FEASIBILITY / "FREEZE.json")
    files = [entry(item["path"], item["sha256"]) for item in previous["files"]]
    for name in ["PROTOCOL.md", "requirements.txt", "requirements-lock.txt",
                 "public_io.py", "prepare_public.py", "run_public.py",
                 "public_toolgate.py", "public_contract.py", "public_score.py"]:
        files.append(entry(ROOT / name))
    for path in sorted((ROOT / "inputs").rglob("*")):
        if path.is_file():
            files.append(entry(path))
    files += [entry(PILOT / "native_retail.py"), entry(PILOT / "source/manifest.json")]
    for item in read(PILOT / "source/manifest.json")["artifacts"]:
        files.append(entry(PILOT / item["path"], item["sha256"]))
    protected = [entry(item["path"], item["sha256"])
                 for item in previous["protected_files"]]
    frozen = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "type": "public-reference-control-freeze-after-reference-preflight",
        "tasks": 6, "scenarios": 4, "routes": 48,
        "methods": ["T-configured", "C"], "outside_mainline_scenarios": 0,
        "files": list({item["path"]: item for item in files}.values()),
        "protected_files": protected,
    }
    save(ROOT / "FREEZE.json", frozen)
    print(json.dumps({"frozen_files": len(frozen["files"]),
                      "protected_files": len(protected)}))


def verify_frozen():
    frozen = read(ROOT / "FREEZE.json")
    for item in frozen["files"] + frozen["protected_files"]:
        entry(item["path"], item["sha256"])
    return frozen


def actual_snapshot(tables, method):
    """Read durable rows independently of adapter-returned snapshots."""
    if method == "T-configured":
        row = max(tables["versions"], key=lambda r: r["version"])
        return {"version": row["version"], "values": json.loads(row["values_json"]),
                "sources": json.loads(row["sources_json"])}
    row = max(tables["record_versions"], key=lambda r: r["version"])
    return {"version": row["version"], "values": json.loads(row["values"]),
            "sources": json.loads(row["fact_sources"])}


def is_error(result):
    return (isinstance(result, str) and result.lower().startswith("error")) or (
        isinstance(result, dict) and bool(result.get("error")))


def run():
    frozen = verify_frozen()
    folder = ROOT / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder.mkdir(parents=True, exist_ok=False)
    save(folder / "freeze.json", frozen)
    shutil.copytree(ROOT / "inputs", folder / "inputs")
    cases = read(folder / "inputs/cases.json")
    save(folder / "cases.json", cases)
    network_attempts = []

    def no_network(event, args):
        if event in {"socket.connect", "socket.getaddrinfo", "socket.sendto"}:
            network_attempts.append(event)
            raise RuntimeError("Public reference comparison prohibits network/model calls")

    sys.addaudithook(no_network)
    sys.path.insert(0, str(PILOT))
    from native_retail import NativeRetail, TARGET_TOOL, verify_source
    import public_toolgate
    import public_contract
    native_source_check = verify_source()
    save(folder / "environment.json", {
        "python": sys.version, "platform": platform.platform(),
        "sqlite": sqlite3.sqlite_version,
        "packages": dict(sorted((d.metadata["Name"], d.version)
                                for d in importlib.metadata.distributions())),
        "network": "denied by audit hook", "hosted_model_calls": 0,
        "native_source_check": native_source_check,
    })
    receipts = []
    for case in cases:
        inputs = folder / "inputs" / str(case["task_id"])
        target = read(inputs / "target.json")
        task = read(inputs / "task.json")
        before_world = read(inputs / "before.json.gz")
        order_id = target["target"]["arguments"]["order_id"]
        actions = task["evaluation_criteria"]["actions"]
        for method, adapter in [("T-configured", public_toolgate), ("C", public_contract)]:
            arm = folder / case["id"] / method
            arm.mkdir(parents=True, exist_ok=False)
            drafts, suffix_records = [], []
            public = {
                "suffix_initial_path": "suffix-before.json.gz",
                "suffix_records_path": "suffix-records.json",
                "final_world_path": "public-final.json.gz",
                "draft_calls": drafts,
            }
            record = {"method": method, "case_id": case["id"], "kind": case["kind"],
                      "engineering_status": "ERROR"}
            final_world = deepcopy(before_world)
            suffix_started = False
            try:
                def native_draft(address):
                    staged = NativeRetail(snapshot=before_world)
                    arguments = {"order_id": order_id, **deepcopy(address)}
                    result = staged.execute(TARGET_TOOL, arguments)
                    world_path = f"draft-{len(drafts) + 1}.json.gz"
                    save(arm / world_path, staged.snapshot())
                    drafts.append({
                        "name": TARGET_TOOL, "tool_name": TARGET_TOOL,
                        "arguments": deepcopy(arguments), "address": deepcopy(address),
                        "result": deepcopy(result), "world_path": world_path,
                    })
                    if is_error(result):
                        raise RuntimeError(f"Native tool rejected draft: {result}")
                    return staged.order(order_id)

                record = adapter.run_case(deepcopy(case), arm, native_draft)
                database = Path(record["db_path"]).resolve()
                record["db_path"] = database.name
                sql_final = dump_sql(database)
                save(arm / "sql-final.json", sql_final)
                durable = actual_snapshot(sql_final, method)
                if durable != {key: record["final"][key] for key in durable}:
                    raise ValueError("Adapter final snapshot disagrees with actual SQLite")
                final_world["orders"][order_id] = deepcopy(durable["values"])
                save(arm / "suffix-before.json.gz", final_world)
                internal_errors = [
                    attempt for attempt in record["attempts"]
                    if attempt.get("engineering_errors")
                    or attempt.get("outcome") == "engineering_error"
                    or (isinstance(attempt.get("outcome"), dict)
                        and attempt["outcome"].get("status") in {"ERROR", "ENGINEERING_ERROR"})
                ]
                if internal_errors:
                    raise RuntimeError("Adapter retained engineering error; recovery is not evidence")
                # Continue only from a real durable boundary write.
                if durable["version"] > record["initial"]["version"]:
                    suffix_started = True
                    continuation = NativeRetail(snapshot=final_world)
                    for action in actions[target["target_index"] + 1:]:
                        result = continuation.execute(action["name"], action["arguments"])
                        suffix_records.append({
                            "action_id": action["action_id"], "name": action["name"],
                            "arguments": deepcopy(action["arguments"]), "result": deepcopy(result),
                        })
                        final_world = continuation.snapshot()
                        if is_error(result):
                            raise RuntimeError(f"Native suffix tool rejected: {action['name']}: {result}")
                record["engineering_status"] = "COMPLETE"
            except Exception as error:
                record["engineering_status"] = "ERROR"
                record["error_type"] = type(error).__name__
                record["error"] = str(error)
                record["traceback"] = traceback.format_exc()
            if not (arm / "suffix-before.json.gz").exists():
                save(arm / "suffix-before.json.gz", before_world)
            save(arm / "suffix-records.json", suffix_records)
            save(arm / "public-final.json.gz", final_world)
            public["suffix_started_from_durable_commit"] = suffix_started
            record["public"] = public
            record["task_id"] = case["task_id"]
            save(arm / "record.json", record)
            receipts.append({
                "case_id": case["id"], "method": method,
                "status": record["engineering_status"],
                "record": (arm / "record.json").relative_to(folder).as_posix(),
            })
            print(json.dumps({"case": case["id"], "method": method,
                              "status": record["engineering_status"]}), flush=True)
    verify_frozen()
    receipt = {
        "run_dir": folder.as_posix(), "records": receipts,
        "complete": sum(item["status"] == "COMPLETE" for item in receipts),
        "errors": sum(item["status"] != "COMPLETE" for item in receipts),
        "network_attempts": network_attempts,
        "sources_and_protected_files_unchanged": True,
        "result_hashes": [
            {"path": p.relative_to(folder).as_posix(), "sha256": sha(p)}
            for p in sorted(folder.rglob("*")) if p.is_file()
        ],
    }
    save(folder / "RUN.json", receipt)
    print(json.dumps({"run_dir": folder.as_posix(), "complete": receipt["complete"],
                      "errors": receipt["errors"], "network_attempts": len(network_attempts)}))
    if receipt["errors"] or network_attempts:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["freeze", "run"])
    args = parser.parse_args()
    freeze() if args.action == "freeze" else run()
