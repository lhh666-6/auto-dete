"""Non-self-referential SHA-256 manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(
    root: Path, destination: Path, *, ignored_prefixes: tuple[str, ...] = ()
) -> dict[str, object]:
    root = root.resolve()
    destination = destination.resolve()
    files: dict[str, dict[str, object]] = {}
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        if path.resolve() == destination:
            continue
        relative = path.relative_to(root).as_posix()
        if relative.startswith(ignored_prefixes):
            continue
        files[relative] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    payload: dict[str, object] = {
        "schema_version": 1,
        "algorithm": "sha256",
        "root": ".",
        "files": files,
        "ignored_prefixes": list(ignored_prefixes),
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def verify_manifest(root: Path, manifest_path: Path) -> list[str]:
    root = root.resolve()
    manifest_path = manifest_path.resolve()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = payload.get("files", {})
    ignored_prefixes = tuple(str(value) for value in payload.get("ignored_prefixes", []))
    if not isinstance(expected, dict):
        return ["invalid:files"]
    failures: list[str] = []
    for relative, metadata in sorted(expected.items()):
        path = (root / relative).resolve()
        if root not in path.parents:
            failures.append(f"unsafe:{relative}")
            continue
        if not path.is_file():
            failures.append(f"missing:{relative}")
            continue
        if not isinstance(metadata, dict) or sha256_file(path) != metadata.get("sha256"):
            failures.append(f"hash:{relative}")
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and path.resolve() != manifest_path
        and not path.relative_to(root).as_posix().startswith(ignored_prefixes)
    }
    failures.extend(f"extra:{relative}" for relative in sorted(actual - set(expected)))
    return failures
