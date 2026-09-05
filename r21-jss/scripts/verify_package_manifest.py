"""Verify the non-self-referential R21 deposit manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(root: Path) -> list[str]:
    manifest_path = root / "PACKAGE_MANIFEST.json"
    if not manifest_path.is_file():
        return ["missing:PACKAGE_MANIFEST.json"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    entries = manifest.get("files", [])
    total_bytes = 0

    if manifest.get("algorithm") != "sha256":
        failures.append("algorithm")
    if manifest.get("file_count") != len(entries):
        failures.append("file_count")

    for entry in entries:
        relative = entry["path"]
        path = root / relative
        if not path.is_file():
            failures.append(f"missing:{relative}")
            continue
        size = path.stat().st_size
        total_bytes += size
        if size != entry["bytes"]:
            failures.append(f"bytes:{relative}")
        if sha256(path) != entry["sha256"]:
            failures.append(f"sha256:{relative}")

    if total_bytes != manifest.get("total_bytes"):
        failures.append("total_bytes")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    failures = verify(args.root.resolve())
    print(json.dumps({"verified": not failures, "failures": failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
