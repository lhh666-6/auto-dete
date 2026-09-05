import argparse
import tempfile
from pathlib import Path

from benchmarks.io import write_json
from benchmarks.trust_faults import run_fault_matrix


def main() -> int:
    parser = argparse.ArgumentParser(description="Run trust-boundary fault injection")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="auto-decte-trust-") as temporary:
        outcomes = run_fault_matrix(Path(temporary))
    write_json(args.output, outcomes)
    valid = all(item.fact_unchanged and item.audit_complete for item in outcomes)
    valid = valid and all(
        item.expected_exception is not None
        for item in outcomes
        if item.fault in {"stale_human_replay", "duplicate_evidence"}
    )
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
