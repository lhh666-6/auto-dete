"""Select by structure before results, then replay fixed native reference paths."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import traceback

sys.dont_write_bytecode = True
from public_io import ROOT, PILOT, canon, save, sha

SELECTED = ["59", "71", "78", "96", "101", "102"]
KINDS = ["corrected", "reauthorized", "instance_mismatch", "wrong_value"]


def main():
    output = ROOT / "inputs"
    output.mkdir(exist_ok=False)
    network_attempts = []

    def no_network(event, args):
        if event in {"socket.connect", "socket.getaddrinfo", "socket.sendto"}:
            network_attempts.append(event)
            raise RuntimeError("Offline reference preflight prohibits network calls")

    sys.addaudithook(no_network)
    sys.path.insert(0, str(PILOT))
    from native_retail import NativeRetail, TARGET_TOOL, load_tasks, replay_reference, verify_source

    tasks = sorted(load_tasks(), key=lambda task: int(task["id"]))
    groups = {}
    for task in tasks:
        actions = task["evaluation_criteria"]["actions"]
        if str(task["id"]) in {"17", "22", "34"} or task.get("initial_state") is not None:
            continue
        if sum(action["name"] == TARGET_TOOL for action in actions) != 1:
            continue
        signature = canon([{k: v for k, v in action.items() if k != "action_id"} for action in actions])
        groups.setdefault(signature, []).append(str(task["id"]))
    representatives = [group[0] for group in groups.values()]
    if representatives[:6] != SELECTED:
        raise ValueError(f"Frozen structural selection differs: {representatives[:6]}")
    selection = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "rule": "first six distinct reference action paths by minimum task id, excluding prior17/22/34",
        "groups": list(groups.values()), "selected": SELECTED,
        "native_sources": verify_source(), "task_file_sha256": sha(PILOT / "source/tau2-bench/data/tau2/domains/retail/tasks.json"),
    }
    save(output / "selection.json", selection)
    cases, receipts = [], []
    for task_id in SELECTED:
        task = next(task for task in tasks if str(task["id"]) == task_id)
        folder = output / task_id
        folder.mkdir(exist_ok=False)
        save(folder / "task.json", task)
        try:
            actions = task["evaluation_criteria"]["actions"]
            index = next(i for i, action in enumerate(actions) if action["name"] == TARGET_TOOL)
            target = actions[index]
            reference, reference_records = replay_reference(task)
            base = NativeRetail(task)
            prefix_records = base.replay(actions[:index])
            before = base.snapshot()
            final = reference.snapshot()
            for item in reference_records:
                if isinstance(item["result"], str) and item["result"].lower().startswith("error"):
                    raise ValueError(f"Native tool returned an error: {item['name']}: {item['result']}")
            save(folder / "before.json.gz", before)
            save(folder / "reference-final.json.gz", final)
            save(folder / "target.json", {"target_index": index, "target": target,
                                        "prefix_records": prefix_records, "reference_records": reference_records,
                                        "native_reference_hash": reference.toolkit.get_db_hash()})
            authorized = {k: deepcopy(v) for k, v in target["arguments"].items() if k != "order_id"}
            proposal = deepcopy(authorized)
            proposal["address2"] = str(proposal.get("address2", "")) + " [unreviewed-draft]"
            for kind in KINDS:
                cases.append({"id": f"P{task_id}-{kind}", "task_id": task_id, "kind": kind,
                              "initial": before["orders"][target["arguments"]["order_id"]],
                              "proposal": proposal, "authorized": authorized})
            receipts.append({"task_id": task_id, "status": "COMPLETE", "reference_calls": len(reference_records),
                             "prefix_calls": len(prefix_records), "suffix_calls": len(actions) - index - 1})
        except Exception as error:
            receipts.append({"task_id": task_id, "status": "ERROR", "error": str(error),
                             "traceback": traceback.format_exc()})
    save(output / "PREFLIGHT.json", {"tasks": receipts, "network_attempts": network_attempts,
                                    "hosted_model_calls": 0, "official_reward": None})
    if any(r["status"] != "COMPLETE" for r in receipts) or network_attempts:
        raise RuntimeError("Preserved failed reference preflight; no task replacements permitted")
    save(output / "cases.json", cases)
    files = {p.relative_to(output).as_posix(): sha(p) for p in sorted(output.rglob("*")) if p.is_file()}
    save(output / "MANIFEST.json", {"files": files})
    print(json.dumps({"reference_tasks": len(receipts), "cases": len(cases),
                      "reference_calls": sum(r["reference_calls"] for r in receipts),
                      "network_attempts": len(network_attempts)}))


if __name__ == "__main__":
    main()
