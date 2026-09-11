#!/usr/bin/env python3
"""Build and verify the deterministic manifest for the integrated latest package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


REVISION = "latest-review-refinement-2026-09-11"
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


def pdf_page_count(path: Path) -> int | None:
    """Return the page count recorded by the PDF page tree, using no third-party reader.

    pdfTeX writes the page-tree root with an explicit ``/Count``; this is read
    directly so that the manifest's page fields can be derived from the shipped
    PDFs instead of being maintained by hand.  Returns ``None`` when the file is
    absent or has no recognisable page tree.
    """
    try:
        data = path.read_bytes()
    except OSError:
        return None
    counts = [
        int(match.group(1))
        for match in re.finditer(rb"/Type\s*/Pages[^>]*?/Count\s+(\d+)", data, re.S)
    ]
    counts += [
        int(match.group(1))
        for match in re.finditer(rb"/Count\s+(\d+)[^>]*?/Type\s*/Pages", data, re.S)
    ]
    return max(counts) if counts else None


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
    parser.add_argument(
        "--main-pages",
        type=int,
        default=None,
        help="Main-manuscript page count. Defaults to the count recorded "
             "in --root/paper/main.pdf.",
    )
    parser.add_argument(
        "--supplement-pages",
        type=int,
        default=None,
        help="Supplement page count. Defaults to the count recorded in "
             "--root/paper/supplement.pdf.",
    )
    parser.add_argument("--citations", type=int, default=54)
    parser.add_argument("--verify-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    manifest_path = args.manifest.resolve()
    if not args.verify_only:
        main_pages = args.main_pages
        if main_pages is None:
            main_pages = pdf_page_count(root / "paper" / "main.pdf")
        supplement_pages = args.supplement_pages
        if supplement_pages is None:
            supplement_pages = pdf_page_count(root / "paper" / "supplement.pdf")
        if main_pages is None or supplement_pages is None:
            print(
                "cannot determine PDF page counts; pass --main-pages and "
                "--supplement-pages explicitly",
                file=sys.stderr,
            )
            return 2
        manifest = build_manifest(
            root,
            pages={"main": main_pages, "supplement": supplement_pages},
            citations=args.citations,
        )
        write_manifest(manifest_path, manifest)
    errors = verify_manifest(root, manifest_path)
    # The file set is compared above; independently confirm that the recorded
    # page counts still describe the PDFs that are actually shipped.
    recorded = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key, relative in (("main", "paper/main.pdf"),
                          ("supplement", "paper/supplement.pdf")):
        actual = pdf_page_count(root / relative)
        if actual is not None and recorded.get("pages", {}).get(key) != actual:
            errors.append(
                f"page-count mismatch: {relative} recorded="
                f"{recorded.get('pages', {}).get(key)} actual={actual}"
            )
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"manifest verified: {len(recorded['files'])} files, "
          f"pages={recorded.get('pages')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
