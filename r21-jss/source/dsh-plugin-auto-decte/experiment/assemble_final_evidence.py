"""Assemble a non-overwriting ten-scenario R19 DSH evidence package."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("core_run", type=Path)
    parser.add_argument("clean_report", type=Path)
    parser.add_argument("tamper_report", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    core = args.core_run.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite final evidence: {output}")
    core_receipt = load(core / "receipt.json")
    clean = load(args.clean_report)
    tamper = load(args.tamper_report)
    d10_passed = (
        clean.get("verified") is True
        and tamper.get("verified") is False
        and tamper.get("changed") == ["receipt.json"]
        and tamper.get("missing") == []
        and tamper.get("extra") == []
    )
    results = dict(core_receipt["results"])
    results["D10"] = {
        "passed": d10_passed,
        "clean_manifest_verified": clean.get("verified"),
        "one_byte_mutation_verified": tamper.get("verified"),
        "exact_changed_path": tamper.get("changed"),
        "missing": tamper.get("missing"),
        "extra": tamper.get("extra"),
    }
    receipt = {
        "schema_version": "auto-decte.dsh-experiment-receipt.v2",
        "passed": all(item.get("passed") is True for item in results.values()),
        "denominator": 10,
        "passed_count": sum(item.get("passed") is True for item in results.values()),
        "dsh": core_receipt["dsh"],
        "runtime": core_receipt["runtime"],
        "claims": [
            "Two tools were composed and executed through the pinned DSH ToolRuntime.",
            "AI output remained a candidate until a separate host confirmation.",
            "Negative cases failed closed without changing the normalized authority state.",
            "An offline manifest verifier detected an exact one-byte mutation path.",
        ],
        "non_claims": [
            "No live model accuracy, usability, security isolation, or production effectiveness claim.",
            "Host authentication and actor identity are preconditions outside this experiment.",
        ],
        "results": results,
    }
    output.mkdir(parents=True)
    shutil.copytree(core, output / "core-run")
    (output / "receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    shutil.copy2(core / "run_metadata.json", output / "run_metadata.json")
    (output / "D10_source_clean_verification.json").write_text(
        json.dumps(clean, indent=2) + "\n", encoding="utf-8"
    )
    (output / "D10_source_tamper_verification.json").write_text(
        json.dumps(tamper, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"output": str(output), "passed": receipt["passed"]}))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
