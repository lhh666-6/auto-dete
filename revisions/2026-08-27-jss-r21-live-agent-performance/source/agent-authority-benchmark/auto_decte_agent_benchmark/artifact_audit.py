"""Run an isolated one-byte tamper probe against a verified Final artifact."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from .manifest import verify_manifest


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_json_exclusive(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _outside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return True
    return False


def audit_final_artifact(*, final_root: Path, output: Path) -> Path:
    """Verify a clean Final, probe a copied byte, and retain a compact receipt.

    The Final directory and its manifest are never modified. ``output`` is create-only and must
    be outside the Final root; the temporary mutated copy is removed after verification.
    """
    final_root = final_root.resolve()
    output = output.resolve()
    manifest_path = final_root / "manifest.json"
    if not final_root.is_dir():
        raise FileNotFoundError(final_root)
    if not _outside(final_root, output):
        raise ValueError("audit output must be outside the Final root")
    if output.exists():
        raise FileExistsError(output)
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)

    clean_before = verify_manifest(final_root, manifest_path)
    if clean_before:
        raise ValueError(f"clean Final manifest verification failed: {clean_before}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("files", [])
    target_entry = next((entry for entry in entries if int(entry.get("bytes", 0)) > 0), None)
    if not isinstance(target_entry, dict):
        raise ValueError("Final artifact has no non-empty manifest file for tamper probe")
    mutated_relative = str(target_entry["path"])
    original = final_root / Path(mutated_relative)
    if not original.is_file():
        raise ValueError(f"tamper target is not a file: {mutated_relative}")

    parent = output.parent
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent, prefix=f".{output.name}-tampered-") as temp_dir:
        tampered_root = Path(temp_dir) / "artifact"
        shutil.copytree(final_root, tampered_root)
        tampered = tampered_root / Path(mutated_relative)
        payload = bytearray(tampered.read_bytes())
        payload[0] ^= 1
        tampered.write_bytes(payload)
        tampered_failures = verify_manifest(tampered_root, tampered_root / "manifest.json")
        expected_failure = f"HASH_OR_SIZE:{mutated_relative}"
        if tampered_failures != [expected_failure]:
            raise ValueError(
                "isolated tamper probe did not produce the exact expected failure: "
                f"{tampered_failures!r}"
            )
        mutated_sha256 = _digest(tampered)

    clean_after = verify_manifest(final_root, manifest_path)
    if clean_after:
        raise ValueError(f"Final changed during tamper probe: {clean_after}")
    receipt = {
        "schema_version": "agent-authority-tamper-probe.v2",
        "status": "PASS",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "mutated_path": mutated_relative,
        "original_bytes": original.stat().st_size,
        "mutated_bytes": int(target_entry["bytes"]),
        "original_sha256": str(target_entry["sha256"]),
        "mutated_sha256": mutated_sha256,
        "manifest_sha256": _digest(manifest_path),
        "clean_verification_before": clean_before,
        "tampered_verification": [expected_failure],
        "clean_verification_after": clean_after,
    }
    receipt_path = output / "TAMPER_PROBE.json"
    _write_json_exclusive(receipt_path, receipt)
    return receipt_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    receipt = audit_final_artifact(final_root=args.final_root, output=args.output)
    print(receipt.read_text(encoding="utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
