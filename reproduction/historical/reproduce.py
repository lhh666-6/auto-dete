"""Reproduce the archived correction-chain audit without changing its source.

Python 3.11+, standard library only. All copied inputs and reports go to a fresh
--output directory. This performs offline persistence auditing, not model calls.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys

PACKAGE = "research/authorization-granularity-phase1-2026-10-06"
REFERENCE_COMMIT = "c66bab68f"
MAPPING = {
    "revisions/2026-08-27-jss-r21-live-agent-performance/": "r21-jss/",
    "revisions/2026-09-12-r30-submission-candidate/": "latest/",
}
PINS = {
    "correction-input-hashes.json": "9c9cd32341ce422ae6cc39a697f8c30bc5bac8bed5d188438f835e483ba0a85c",
    "audit_corrections.py": "4099738e61f710f7bca1747f50b5266618f1e6f6998a37d4da371238505fd852",
    "correction-summary.json": "246388eef14ce1db292437ab3b78fb0bdb1ec64129a7dc3a0beb3c473b440564",
    "correction-chains.jsonl": "13f0a990f75b81ecca66aaa46188f9ccc447110e1c4eef8c41fd215ed56f164a",
}


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_relative(value: str) -> Path:
    """Reject absolute, traversal, drive and alternate-separator paths."""
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError(f"Invalid relative input path: {value!r}")
    parts = value.split("/")
    if PurePosixPath(value).is_absolute() or any(part in ("", ".", "..") for part in parts):
        raise ValueError(f"Invalid relative input path: {value!r}")
    return Path(*parts)


def contained_path(root: Path, relative: str, *, must_exist: bool) -> Path:
    path = (root / safe_relative(relative)).resolve(strict=must_exist)
    if not path.is_relative_to(root):
        raise ValueError(f"Input path escapes its root: {relative}")
    if must_exist and not path.is_file():
        raise ValueError(f"Input is not a regular file: {relative}")
    return path


def validate_output(source: Path, requested: Path) -> Path:
    if requested.exists() or requested.is_symlink():
        raise FileExistsError("Output already exists; choose a new --output directory.")
    output = requested.resolve()
    for tree in ("r21-jss", "latest", "revisions", "research", "DKE-supplement"):
        if output.is_relative_to((source / tree).resolve()):
            raise ValueError("Output cannot be inside a source evidence tree.")
    if source.is_relative_to(output):
        raise ValueError("Output cannot contain the source repository.")
    return output


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_chains(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def reproduce(source: Path, requested_output: Path) -> dict:
    source = source.resolve(strict=True)
    if not source.is_dir():
        raise ValueError("--source must be a repository directory.")
    output = validate_output(source, requested_output)
    metadata = {}
    for name, expected in PINS.items():
        path = contained_path(source, f"{PACKAGE}/{name}", must_exist=True)
        if sha256(path) != expected:
            raise ValueError(f"Archived file hash mismatch: {PACKAGE}/{name}")
        metadata[name] = path
    ledger = read_json(metadata["correction-input-hashes.json"])
    if not isinstance(ledger, dict) or len(ledger) != 1854:
        raise ValueError("Expected exactly 1,854 declared historical input files.")

    workspace = output / "workspace"
    rows = []
    for original, expected in ledger.items():
        safe_relative(original)
        prefixes = [prefix for prefix in MAPPING if original.startswith(prefix)]
        if len(prefixes) != 1:
            raise ValueError(f"No unique historical mapping for: {original}")
        prefix = prefixes[0]
        mapped = MAPPING[prefix] + original[len(prefix):]
        input_path = contained_path(source, mapped, must_exist=True)
        contained_path(workspace, original, must_exist=False)
        if sha256(input_path) != expected:
            raise ValueError(f"Historical input hash mismatch: {mapped}")
        rows.append({"original": original, "mapped": mapped,
                     "bytes": input_path.stat().st_size, "sha256": expected})

    output.mkdir(parents=True, exist_ok=False)
    workspace.mkdir()
    for row in rows:
        input_path = contained_path(source, row["mapped"], must_exist=True)
        destination = contained_path(workspace, row["original"], must_exist=False)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(input_path, destination)
        if sha256(destination) != row["sha256"]:
            raise ValueError(f"Copied input hash mismatch: {row['original']}")

    script = f"{PACKAGE}/audit_corrections.py"
    copied_script = contained_path(workspace, script, must_exist=False)
    copied_script.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(metadata["audit_corrections.py"], copied_script)
    if sha256(copied_script) != PINS["audit_corrections.py"]:
        raise ValueError("Copied audit script hash mismatch.")
    run = subprocess.run([sys.executable, "-B", script], cwd=workspace,
                         capture_output=True, text=True)
    (output / "audit-stdout.txt").write_text(run.stdout, encoding="utf-8")
    (output / "audit-stderr.txt").write_text(run.stderr, encoding="utf-8")
    if run.returncode:
        raise RuntimeError(f"Historical audit exited {run.returncode}; inspect audit-stderr.txt.")

    generated = workspace / PACKAGE
    summary = read_json(generated / "correction-summary.json")
    checks = {
        "summary_semantic_match": summary == read_json(metadata["correction-summary.json"]),
        "chains_semantic_match": read_chains(generated / "correction-chains.jsonl") == read_chains(metadata["correction-chains.jsonl"]),
        "ledger_semantic_match": read_json(generated / "correction-input-hashes.json") == ledger,
        "source_inputs_unchanged": all(sha256(contained_path(source, row["mapped"], must_exist=True)) == row["sha256"] for row in rows),
        "copied_inputs_unchanged": all(sha256(contained_path(workspace, row["original"], must_exist=True)) == row["sha256"] for row in rows),
        "source_metadata_unchanged": all(sha256(path) == PINS[name] for name, path in metadata.items()),
        "audit_script_unchanged": sha256(copied_script) == PINS["audit_corrections.py"],
    }
    receipt = {
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "reference_commit": REFERENCE_COMMIT,
        "python": platform.python_version(),
        "os": platform.platform(),
        "reviewer_tool": "reproduction/historical/reproduce.py",
        "reviewer_tool_sha256": sha256(Path(__file__).resolve()),
        "workspace": "workspace",
        "input_file_count": len(rows),
        "input_bytes": sum(row["bytes"] for row in rows),
        "mapping": MAPPING,
        "archived_file_sha256": PINS,
        "audit_exit_code": run.returncode,
        "checks": checks,
        "counts": summary["counts"],
        "all_pass": all(checks.values()),
        "scope": "All declared historical inputs mapped and hashed; unchanged audit script executed against copied databases; derived summary, every chain and input ledger compared semantically. No provider calls, fresh historical task execution or annotation review. Zero unchanged-field checks in this archive.",
    }
    (output / "input-map.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    (output / "verification.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if not receipt["all_pass"]:
        raise ValueError("Historical verification failed; inspect verification.json.")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[2],
                        help="Repository root (default: repository containing this tool).")
    parser.add_argument("--output", type=Path, required=True,
                        help="Fresh directory for copied inputs and verification reports.")
    args = parser.parse_args()
    try:
        receipt = reproduce(args.source, args.output)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
