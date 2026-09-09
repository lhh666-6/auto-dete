"""Create or verify a non-self-referential SHA-256 manifest for an R19 DSH run."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA_VERSION = "auto-decte.dsh-evidence-manifest.v1"
MANIFEST_NAME = "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory(root: Path) -> list[dict[str, object]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != MANIFEST_NAME
    ]


def create(root: Path) -> dict[str, object]:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "hash_algorithm": "sha256",
        "self_excluded": MANIFEST_NAME,
        "files": inventory(root),
    }
    path = root / MANIFEST_NAME
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing manifest: {path}")
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def verify(root: Path) -> dict[str, object]:
    manifest_path = root / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported manifest schema")
    expected = {entry["path"]: entry for entry in manifest["files"]}
    actual = {entry["path"]: entry for entry in inventory(root)}
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed = sorted(
        path
        for path in set(expected) & set(actual)
        if expected[path]["sha256"] != actual[path]["sha256"]
        or expected[path]["bytes"] != actual[path]["bytes"]
    )
    return {
        "schema_version": "auto-decte.dsh-evidence-verification.v1",
        "verified": not missing and not extra and not changed,
        "checked_files": len(expected),
        "missing": missing,
        "extra": extra,
        "changed": changed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("create", "verify"))
    parser.add_argument("root", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    result = create(root) if args.mode == "create" else verify(root)
    if args.report is not None:
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if args.mode == "create" or result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
