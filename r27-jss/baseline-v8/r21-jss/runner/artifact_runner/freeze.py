"""Allow-listed, path-independent source-freeze builder."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from artifact_runner.integrity import build_manifest, verify_manifest


def _safe_relative(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe allow-list path: {value}")
    return path


def _copy_entry(
    source_root: Path, destination_root: Path, entry: dict[str, Any], excluded: set[str]
) -> None:
    relative = _safe_relative(str(entry["path"]))
    source = source_root / relative
    destination = destination_root / relative
    if not source.exists():
        raise FileNotFoundError(source)
    if entry["kind"] == "file":
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return
    if entry["kind"] != "tree":
        raise ValueError(f"unsupported entry kind: {entry['kind']}")
    for path in sorted(source.rglob("*")):
        subpath = path.relative_to(source)
        if any(part in excluded for part in subpath.parts):
            continue
        target = destination / subpath
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def build_source_freeze(
    parent_root: Path,
    implementation_root: Path,
    config_path: Path,
    output: Path,
) -> dict[str, object]:
    if output.exists():
        raise FileExistsError(output)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise ValueError("unsupported freeze config schema")
    output.mkdir(parents=True)
    excluded = set(config.get("excluded_names", []))
    sections = (
        ("paper_repo", parent_root, output / "source" / "paper-repo"),
        ("implementation", implementation_root, output / "source" / "implementation"),
        ("runner", parent_root, output / "runner"),
    )
    try:
        for section, source_root, destination_root in sections:
            for entry in config.get(section, []):
                _copy_entry(source_root.resolve(), destination_root, entry, excluded)
        (output / "evidence" / "frozen").mkdir(parents=True)
        (output / "evidence" / "reproduced").mkdir(parents=True)
        config_copy = output / "freeze_config.json"
        shutil.copy2(config_path, config_copy)
        payload = build_manifest(
            output,
            output / "source_manifest.json",
            ignored_prefixes=("evidence/",),
        )
        failures = verify_manifest(output, output / "source_manifest.json")
        if failures:
            raise RuntimeError(f"freeze verification failed: {failures}")
        return payload
    except BaseException:
        # Preserve a failed staging attempt and its files for diagnosis.
        (output / "FREEZE_FAILED.txt").write_text("source freeze failed\n", encoding="utf-8")
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-root", type=Path, required=True)
    parser.add_argument("--implementation-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build_source_freeze(args.parent_root, args.implementation_root, args.config, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
