"""Non-self-referential artifact manifest build and strict verification."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
from typing import Any


def _hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _relative_exclusion(root: Path, manifest_path: Path) -> str | None:
    try:
        return manifest_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def build_manifest(root: Path, *, manifest_path: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise FileNotFoundError(root)
    excluded = _relative_exclusion(root, manifest_path)
    files = []
    for path in sorted((item for item in root.rglob("*") if item.is_file())):
        relative = path.relative_to(root).as_posix()
        if relative == excluded:
            continue
        files.append({"path": relative, "bytes": path.stat().st_size, "sha256": _hash(path)})
    return {
        "schema_version": "agent-authority-artifact-manifest.v2",
        "root": ".",
        "files": files,
    }


def verify_manifest(root: Path, manifest_path: Path) -> list[str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {str(item["path"]): item for item in manifest.get("files", [])}
    excluded = _relative_exclusion(root, manifest_path)
    actual = {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and path.relative_to(root).as_posix() != excluded
    }
    failures: list[str] = []
    for relative in sorted(set(expected) - set(actual)):
        failures.append(f"MISSING:{relative}")
    for relative in sorted(set(actual) - set(expected)):
        failures.append(f"EXTRA:{relative}")
    for relative in sorted(set(expected) & set(actual)):
        item = expected[relative]
        path = actual[relative]
        if path.stat().st_size != int(item["bytes"]) or _hash(path) != item["sha256"]:
            failures.append(f"HASH_OR_SIZE:{relative}")
    return failures
