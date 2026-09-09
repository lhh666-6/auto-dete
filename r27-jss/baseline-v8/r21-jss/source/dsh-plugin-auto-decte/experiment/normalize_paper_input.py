"""Normalize the final R19 DSH receipt into the paper's bounded claim input."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("clean_verification", type=Path)
    parser.add_argument("tamper_verification", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    clean = json.loads(args.clean_verification.read_text(encoding="utf-8"))
    tamper = json.loads(args.tamper_verification.read_text(encoding="utf-8"))
    cases = [
        {
            "case_id": case_id,
            "passed": item["passed"],
            **{
                key: value
                for key, value in item.items()
                if key
                in {
                    "exact_tool_count",
                    "tool_names",
                    "current_fact_version",
                    "proposed_value",
                    "authorized_value",
                    "rejected",
                    "schemas_after_unload",
                    "exact_changed_path",
                }
            },
        }
        for case_id, item in receipt["results"].items()
    ]
    output = {
        "schema_version": "auto-decte.paper-input.dsh-plugin-integration.v1",
        "source_receipt": "evidence/reproduced/r19-dsh-2026-08-27-final/receipt.json",
        "dsh_tag": receipt["dsh"]["tag"],
        "dsh_commit": receipt["dsh"]["commit"],
        "execution_mode": "deterministic keyless calls through pinned Cordis/DSH ToolRuntime",
        "denominator": receipt["denominator"],
        "passed_count": receipt["passed_count"],
        "all_passed": receipt["passed"],
        "registered_model_tools": ["auto_decte_propose", "auto_decte_verify"],
        "model_callable_fact_write_tools": 0,
        "clean_manifest_verified": clean["verified"],
        "tamper_manifest_verified": tamper["verified"],
        "tamper_exact_changed_path": tamper["changed"],
        "cases": cases,
        "claim_limits": receipt["non_claims"],
    }
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite paper input: {args.output}")
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    return 0 if output["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
