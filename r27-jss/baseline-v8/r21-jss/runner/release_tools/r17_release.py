from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _portable(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _normalize_prefixes(prefixes: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for prefix in prefixes:
        value = prefix.replace("\\", "/").strip("/")
        if not value or value == ".." or value.startswith("../") or "/../" in value:
            raise ValueError(f"invalid excluded prefix: {prefix}")
        normalized.append(value)
    return tuple(sorted(set(normalized)))


def _is_excluded(relative: str, prefixes: tuple[str, ...]) -> bool:
    return any(relative == prefix or relative.startswith(prefix + "/") for prefix in prefixes)


def write_manifest(
    root: Path, output: Path, *, exclude_prefixes: tuple[str, ...] = ()
) -> dict[str, Any]:
    root = root.resolve()
    output = output.resolve()
    excluded = _normalize_prefixes(exclude_prefixes)
    if output.parent != root:
        raise ValueError("manifest must be written at the covered root")

    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path == output:
            continue
        relative = _portable(path, root)
        if _is_excluded(relative, excluded):
            continue
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed: {relative}")
        if not path.is_file():
            continue
        files.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )

    payload: dict[str, Any] = {
        "schema_version": 1,
        "algorithm": "sha256",
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "excluded_prefixes": list(excluded),
        "files": files,
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


def verify_manifest(root: Path, manifest: Path) -> list[str]:
    root = root.resolve()
    payload = json.loads(manifest.read_text(encoding="utf-8-sig"))
    excluded = _normalize_prefixes(tuple(payload.get("excluded_prefixes", [])))
    expected = {item["path"]: item for item in payload["files"]}
    failures: list[str] = []

    actual: set[str] = set()
    for path in root.rglob("*"):
        if path.resolve() == manifest.resolve():
            continue
        relative = _portable(path, root)
        if _is_excluded(relative, excluded):
            continue
        if path.is_symlink():
            failures.append(f"symlink:{relative}")
            continue
        if path.is_file():
            actual.add(relative)

    for relative in sorted(set(expected) - actual):
        failures.append(f"missing:{relative}")
    for relative in sorted(actual - set(expected)):
        failures.append(f"extra:{relative}")
    for relative in sorted(set(expected) & actual):
        path = root / relative
        item = expected[relative]
        if _sha256(path) != item["sha256"]:
            failures.append(f"hash:{relative}")

    if payload.get("file_count") != len(expected):
        failures.append("metadata:file_count")
    if payload.get("total_bytes") != sum(item["bytes"] for item in expected.values()):
        failures.append("metadata:total_bytes")
    return failures


def verify_declared_manifest(root: Path, manifest: Path) -> list[str]:
    """Verify every declared legacy file while permitting R17 additions."""
    root = root.resolve()
    payload = json.loads(manifest.read_text(encoding="utf-8-sig"))
    failures: list[str] = []
    for relative, item in sorted(payload["files"].items()):
        path = root / relative
        if not path.is_file():
            failures.append(f"missing:{relative}")
        elif _sha256(path) != item["sha256"]:
            failures.append(f"hash:{relative}")
    return failures


def compare_exact_inputs(expected: Path, actual: Path) -> dict[str, Any]:
    expected_files = {path.name: path for path in expected.glob("*.json")}
    actual_files = {path.name: path for path in actual.glob("*.json")}
    missing = sorted(set(expected_files) - set(actual_files))
    extra = sorted(set(actual_files) - set(expected_files))
    mismatches = sorted(
        name
        for name in set(expected_files) & set(actual_files)
        if _sha256(expected_files[name]) != _sha256(actual_files[name])
    )
    status = "PASS" if not (missing or extra or mismatches) else "FAIL"
    return {
        "status": status,
        "expected_count": len(expected_files),
        "actual_count": len(actual_files),
        "missing": missing,
        "extra": extra,
        "hash_mismatches": mismatches,
    }


def _alloy_projection(value: Any) -> Any:
    keys = ("profile", "command", "class", "expected", "actual", "status", "model")
    return sorted(
        ({key: row.get(key) for key in keys} for row in value),
        key=lambda row: (row["profile"], row["command"]),
    )


def _refinement_projection(value: dict[str, Any]) -> Any:
    return {
        "case_count": value.get("case_count"),
        "sat_count": value.get("sat_count"),
        "unsat_count": value.get("unsat_count"),
        "cases": sorted(
            (
                {
                    "case": row.get("case"),
                    "alloy_outcome": row.get("alloy_outcome"),
                    "projection_outcome": row.get("projection_outcome"),
                }
                for row in value.get("cases", [])
            ),
            key=lambda row: row["case"],
        ),
    }


def _conformance_projection(value: dict[str, Any]) -> Any:
    return {
        key: value.get(key)
        for key in (
            "catalogue_version",
            "declared_denominator",
            "executed_denominator",
            "passed",
            "failed",
        )
    } | {
        "results": sorted(
            (
                {"case_id": row.get("case_id"), "return_code": row.get("return_code")}
                for row in value.get("results", [])
            ),
            key=lambda row: row["case_id"],
        )
    }


def _run_projection(value: dict[str, Any]) -> Any:
    commands = [
        {
            "command_id": row.get("command_id"),
            "exit_code": row.get("exit_code"),
            "timed_out": row.get("timed_out"),
        }
        for row in value.get("commands", [])
        if row.get("group") == "correctness"
    ]
    return sorted(commands, key=lambda row: row["command_id"])


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def _lifecycle_projection(value: dict[str, Any]) -> dict[str, Any]:
    correction = value.get("correction", {})
    locator_value = value.get("input_evidence_locator")
    try:
        locator = json.loads(locator_value) if isinstance(locator_value, str) else {}
    except json.JSONDecodeError:
        locator = {}
    uri = locator.get("uri")
    return {
        key: value.get(key)
        for key in (
            "schema_version",
            "status",
            "trace_status",
            "copy_forward_fields",
            "export_values_equal_final",
            "final_values",
            "initial_values",
            "input_sha256",
            "versions",
        )
    } | {
        "correction": {
            key: correction.get(key)
            for key in ("authorized_value", "machine_candidate", "transition_id")
        }
        | {"certificate_id_is_sha256": _is_sha256(correction.get("certificate_id"))},
        "export_sha256_is_sha256": _is_sha256(value.get("export_sha256")),
        "input_evidence_locator": {
            "form_id": locator.get("form_id"),
            "related_field_id": locator.get("related_field_id"),
            "v": locator.get("v"),
            "uri_is_evidence_png": (
                isinstance(uri, str) and uri.startswith("images/") and uri.endswith(".png")
            ),
        },
    }


def compare_correctness_semantics(expected: Path, actual: Path) -> dict[str, Any]:
    projections = {
        "alloy_results.json": _alloy_projection,
        "formal_refinement_summary.json": _refinement_projection,
        "conformance_summary.json": _conformance_projection,
        "run_summary.json": _run_projection,
        "quality_summary.json": lambda value: value,
        "lifecycle_summary.json": _lifecycle_projection,
    }
    mismatches: list[str] = []
    missing: list[str] = []
    for name, project in projections.items():
        expected_path = expected / name
        actual_path = actual / name
        if not expected_path.is_file():
            continue
        if not actual_path.is_file():
            missing.append(name)
            continue
        if project(_load(expected_path)) != project(_load(actual_path)):
            mismatches.append(name)
    return {
        "status": "PASS" if not (missing or mismatches) else "FAIL",
        "checked": sorted(projections),
        "missing": sorted(missing),
        "mismatches": sorted(mismatches),
    }


def _finite_positive(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def compare_performance_descriptively(
    expected_path: Path, actual_path: Path
) -> dict[str, Any]:
    expected = _load(expected_path)
    actual = _load(actual_path)
    failures: list[str] = []

    key_fields = {
        "admission": ("fields", "changed", "trials"),
        "trace": ("fields", "versions", "records", "trials"),
        "storage": ("transitions",),
    }
    positive_fields = {
        "admission": ("full_p50_ms", "full_p95_ms", "lower_p50_ms"),
        "trace": ("p50_ms", "p95_ms"),
        "storage": ("incremental_bytes",),
    }
    grid: dict[str, int] = {}
    ratios: dict[str, dict[str, float]] = {}
    for family, keys in key_fields.items():
        expected_rows = expected.get(family, [])
        actual_rows = actual.get(family, [])
        grid[family] = len(actual_rows)
        expected_grid = sorted(tuple(row[key] for key in keys) for row in expected_rows)
        actual_grid = sorted(tuple(row.get(key) for key in keys) for row in actual_rows)
        if expected_grid != actual_grid:
            failures.append(f"grid:{family}")
            continue

        expected_by_key = {tuple(row[key] for key in keys): row for row in expected_rows}
        family_ratios: list[float] = []
        for row in actual_rows:
            row_key = tuple(row[key] for key in keys)
            for field in positive_fields[family]:
                if not _finite_positive(row.get(field)):
                    failures.append(f"nonpositive:{family}:{field}")
                    continue
                expected_value = expected_by_key[row_key].get(field)
                if _finite_positive(expected_value):
                    family_ratios.append(float(row[field]) / float(expected_value))
        if family_ratios:
            ratios[family] = {
                "min": min(family_ratios),
                "max": max(family_ratios),
            }

    return {
        "status": "PASS" if not failures else "FAIL",
        "grid": grid,
        "failures": sorted(set(failures)),
        "observed_ratio_ranges": ratios,
        "interpretation": "structural and finite-value gate; timing ratios are descriptive",
    }


def _write_report(path: Path | None, result: dict[str, Any]) -> None:
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if path is None:
        print(rendered, end="")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUTO-DECTE R17 release verifier")
    subparsers = parser.add_subparsers(dest="command", required=True)

    manifest_parser = subparsers.add_parser("manifest")
    manifest_parser.add_argument("--root", type=Path, required=True)
    manifest_parser.add_argument("--manifest", type=Path, required=True)
    manifest_parser.add_argument(
        "--exclude-prefix", action="append", default=["evidence/reproduced"]
    )

    verify_parser = subparsers.add_parser("verify-manifest")
    verify_parser.add_argument("--root", type=Path, required=True)
    verify_parser.add_argument("--manifest", type=Path, required=True)
    verify_parser.add_argument("--report", type=Path)

    declared_parser = subparsers.add_parser("verify-declared")
    declared_parser.add_argument("--root", type=Path, required=True)
    declared_parser.add_argument("--manifest", type=Path, required=True)
    declared_parser.add_argument("--report", type=Path)

    exact_parser = subparsers.add_parser("compare-exact")
    exact_parser.add_argument("--expected", type=Path, required=True)
    exact_parser.add_argument("--actual", type=Path, required=True)
    exact_parser.add_argument("--report", type=Path)

    semantic_parser = subparsers.add_parser("compare-correctness")
    semantic_parser.add_argument("--expected", type=Path, required=True)
    semantic_parser.add_argument("--actual", type=Path, required=True)
    semantic_parser.add_argument("--report", type=Path)

    performance_parser = subparsers.add_parser("compare-performance")
    performance_parser.add_argument("--expected", type=Path, required=True)
    performance_parser.add_argument("--actual", type=Path, required=True)
    performance_parser.add_argument("--report", type=Path)

    args = parser.parse_args(argv)
    if args.command == "manifest":
        write_manifest(
            args.root, args.manifest, exclude_prefixes=tuple(args.exclude_prefix)
        )
        return 0
    if args.command == "verify-manifest":
        failures = verify_manifest(args.root, args.manifest)
        result = {"status": "PASS" if not failures else "FAIL", "failures": failures}
    elif args.command == "verify-declared":
        failures = verify_declared_manifest(args.root, args.manifest)
        result = {"status": "PASS" if not failures else "FAIL", "failures": failures}
    elif args.command == "compare-exact":
        result = compare_exact_inputs(args.expected, args.actual)
    elif args.command == "compare-correctness":
        result = compare_correctness_semantics(args.expected, args.actual)
    else:
        result = compare_performance_descriptively(args.expected, args.actual)
    _write_report(args.report, result)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
