"""Describe the archived feedback pairs by permission state; no new runs."""
import argparse
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", type=Path, default=BASE / "tables/feedback-sensitivity/pairs.csv")
    parser.add_argument("--output", type=Path, default=BASE / "tables/feedback-sensitivity/strata.json")
    args = parser.parse_args()
    rows = list(csv.DictReader(args.pairs.open(encoding="utf-8-sig", newline="")))
    result = {"scope": "Descriptive grouping of 12 saved model pairs; four reused task definitions, not an interaction test", "states": {}}
    for state in ("valid", "revoked", "unavailable"):
        selected = [r for r in rows if r["controller"] == "model" and r["authorization_state"] == state]
        result["states"][state] = {
            "pairs": len(selected),
            "task_definitions": sorted({r["task_instance_id"] for r in selected}),
            "total_call_delta_labels_minus_facts": sum(int(r["delta_all_tool_calls"]) for r in selected),
            "state_query_delta": sum(int(r["delta_get_state_reads"]) for r in selected),
            "other_call_delta": sum(int(r["delta_other_tool_calls"]) for r in selected),
        }
    result["total_call_delta_labels_minus_facts"] = sum(r["total_call_delta_labels_minus_facts"] for r in result["states"].values())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))

if __name__ == "__main__":
    main()
