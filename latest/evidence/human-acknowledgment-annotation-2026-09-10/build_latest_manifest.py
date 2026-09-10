#!/usr/bin/env python3
"""Build and verify the deterministic manifest for the integrated latest package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REVISION = "latest-post-r28-human-annotation-2026-09-10"
STATUS = "INTEGRATED_CANDIDATE_PENDING_AUTHOR_CONFIRMATIONS"
EXCLUDED_DIRECTORY_NAMES = {
    "out",
    "tmp",
    "__pycache__",
    ".pytest_cache",
    ".hypothesis",
    "build",
    "dist",
}
EXCLUDED_FILE_NAMES = {"MANIFEST-r27.json"}
EXCLUDED_SUFFIXES = (".pyc", ".synctex.gz")


def _excluded(relative_path: Path) -> bool:
    if relative_path.name in EXCLUDED_FILE_NAMES:
        return True
    directory_parts = relative_path.parts[:-1]
    if any(part in EXCLUDED_DIRECTORY_NAMES for part in directory_parts):
        return True
    if any(part.endswith(".egg-info") for part in directory_parts):
        return True
    return relative_path.name.endswith(EXCLUDED_SUFFIXES)


def _file_entry(path: Path) -> dict[str, int | str]:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"sha256": digest.hexdigest(), "bytes": path.stat().st_size}


def collect_files(root: Path) -> dict[str, dict[str, int | str]]:
    root = root.resolve()
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if not _excluded(relative):
            paths.append(relative)
    return {
        relative.as_posix(): _file_entry(root / relative)
        for relative in sorted(paths, key=lambda item: item.as_posix())
    }


def build_manifest(
    root: Path,
    *,
    pages: dict[str, int],
    citations: int,
) -> dict[str, Any]:
    return {
        "schema": "auto-decte.latest-human-annotation.v1",
        "revision": REVISION,
        "status": STATUS,
        "pages": pages,
        "citations": citations,
        "files": collect_files(root),
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def verify_manifest(root: Path, manifest_path: Path) -> list[str]:
    recorded = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_files = collect_files(root)
    actual_files = recorded.get("files", {})
    errors: list[str] = []
    for missing in sorted(set(expected_files) - set(actual_files)):
        errors.append(f"missing from manifest: {missing}")
    for extra in sorted(set(actual_files) - set(expected_files)):
        errors.append(f"extra in manifest: {extra}")
    for name in sorted(set(expected_files) & set(actual_files)):
        if expected_files[name] != actual_files[name]:
            errors.append(f"digest or size mismatch: {name}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--main-pages", type=int, default=59)
    parser.add_argument("--supplement-pages", type=int, default=16)
    parser.add_argument("--citations", type=int, default=54)
    parser.add_argument("--verify-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    manifest_path = args.manifest.resolve()
    if not args.verify_only:
        manifest = build_manifest(
            root,
            pages={"main": args.main_pages, "supplement": args.supplement_pages},
            citations=args.citations,
        )
        write_manifest(manifest_path, manifest)
    errors = verify_manifest(root, manifest_path)
    if errors:
        for error in errors:
            print(error)
        return 1
    count = len(json.loads(manifest_path.read_text(encoding="utf-8"))["files"])
    print(f"manifest verified: {count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
