"""R21 feature-equivalent relational materialization baseline.

The baseline preserves the exact relational post-state produced by full
admission while ablating application-level certificate validation and plan
construction from the timed region. It therefore isolates persistence cost;
it is not an alternative authority implementation.
"""

from __future__ import annotations

import hashlib
import json
import platform
import random
import shutil
import sqlite3
import statistics
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import and_, create_engine, insert, select, update
from sqlalchemy.engine import Engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import install_sqlite_pragmas
from benchmarks.authority_cost import (
    _checkpoint,
    _full_admission,
    _measure,
    _percentile,
    _row_count,
    _seed_form,
)


def _engine(path: Path) -> Engine:
    engine = create_engine(f"sqlite:///{path}")
    install_sqlite_pragmas(engine)
    return engine


def _normalize(value: object) -> object:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bytes):
        return {"__bytes__": value.hex()}
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    return value


def _snapshot(engine: Engine) -> dict[str, list[dict[str, Any]]]:
    with engine.connect() as connection:
        return {
            table.name: [dict(row) for row in connection.execute(select(table)).mappings()]
            for table in Base.metadata.sorted_tables
        }


def _fingerprint(snapshot: dict[str, list[dict[str, Any]]]) -> str:
    normalized = {
        table: sorted(
            (_normalize(row) for row in rows),
            key=lambda row: json.dumps(row, sort_keys=True, separators=(",", ":")),
        )
        for table, rows in snapshot.items()
    }
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _primary_key(table: Any, row: dict[str, Any]) -> tuple[object, ...]:
    return tuple(row[column.name] for column in table.primary_key.columns)


def build_database_delta(before_path: Path, after_path: Path) -> dict[str, Any]:
    before_engine = _engine(before_path)
    after_engine = _engine(after_path)
    try:
        before = _snapshot(before_engine)
        after = _snapshot(after_engine)
    finally:
        before_engine.dispose()
        after_engine.dispose()

    tables: dict[str, dict[str, Any]] = {}
    deleted_rows = 0
    for table in Base.metadata.sorted_tables:
        before_rows = {_primary_key(table, row): row for row in before[table.name]}
        after_rows = {_primary_key(table, row): row for row in after[table.name]}
        deleted = sorted(set(before_rows) - set(after_rows), key=repr)
        deleted_rows += len(deleted)
        inserted = [after_rows[key] for key in sorted(set(after_rows) - set(before_rows), key=repr)]
        updated = [
            {"before": before_rows[key], "after": after_rows[key]}
            for key in sorted(set(after_rows) & set(before_rows), key=repr)
            if after_rows[key] != before_rows[key]
        ]
        tables[table.name] = {
            "primary_key": [column.name for column in table.primary_key.columns],
            "inserted": inserted,
            "updated": updated,
            "deleted_primary_keys": deleted,
        }
    return {
        "schema_version": 1,
        "equivalent_target": "full_admission_relational_state",
        "ablated_features": [
            "certificate_validation",
            "lineage_validation",
            "admission_plan_derivation",
            "authority_object_construction",
        ],
        "preserved_features": [
            "complete_record_snapshot",
            "total_fact_source_map",
            "candidate_certificate_rows",
            "human_decision_rows",
            "authorization_binding_rows",
            "fact_transition_rows",
            "audit_rows",
            "single_transaction",
            "form_version_compare_and_swap",
        ],
        "before_fingerprint": _fingerprint(before),
        "after_fingerprint": _fingerprint(after),
        "deleted_rows": deleted_rows,
        "tables": tables,
    }


def apply_database_delta(path: Path, delta: dict[str, Any]) -> dict[str, Any]:
    if delta.get("deleted_rows") != 0:
        raise ValueError("feature baseline does not support deleted rows")
    engine = _engine(path)
    before = _snapshot(engine)
    if _fingerprint(before) != delta.get("before_fingerprint"):
        engine.dispose()
        raise RuntimeError("target database does not match the locked pre-state")
    before_rows = _row_count(engine)

    def action() -> None:
        with engine.begin() as connection:
            for table in Base.metadata.sorted_tables:
                changes = delta["tables"][table.name]
                primary_names = set(changes["primary_key"])
                for item in changes["updated"]:
                    prior = item["before"]
                    final = item["after"]
                    predicates = [
                        table.c[name] == prior[name] for name in changes["primary_key"]
                    ]
                    if table.name == "forms":
                        predicates.append(
                            table.c.current_record_version == prior["current_record_version"]
                        )
                    values = {
                        key: value for key, value in final.items() if key not in primary_names
                    }
                    result = connection.execute(
                        update(table).where(and_(*predicates)).values(**values)
                    )
                    if result.rowcount != 1:
                        raise RuntimeError(f"compare-and-swap/update failed for {table.name}")
            for table in Base.metadata.sorted_tables:
                rows = delta["tables"][table.name]["inserted"]
                if rows:
                    connection.execute(insert(table), rows)

    elapsed, statements = _measure(engine, action)
    after = _snapshot(engine)
    if _fingerprint(after) != delta.get("after_fingerprint"):
        engine.dispose()
        raise RuntimeError("materialized database does not match the full-admission post-state")
    after_rows = _row_count(engine)
    _checkpoint(engine)
    engine.dispose()
    return {
        "latency_ns": elapsed,
        "sql_statements": statements,
        "rows_written": after_rows - before_rows,
        "post_state_fingerprint": delta["after_fingerprint"],
    }


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _cells(config: dict[str, Any]) -> list[tuple[int, int]]:
    cells: list[tuple[int, int]] = []
    for raw_fields in config["admission_fields"]:
        fields = int(raw_fields)
        for raw_changed in config["admission_changed"]:
            changed = fields if raw_changed == "all" else min(int(raw_changed), fields)
            if (fields, changed) not in cells:
                cells.append((fields, changed))
    return cells


def _summary(
    observations: list[dict[str, Any]], equivalence: dict[tuple[int, int], bool]
) -> dict[str, Any]:
    cells = []
    for fields, changed in sorted(equivalence):
        rows = [
            row
            for row in observations
            if (int(row["fields"]), int(row["changed"])) == (fields, changed)
        ]
        full = [float(row["full"]["latency_ns"]) / 1e6 for row in rows]
        materialization = [
            float(row["materialization"]["latency_ns"]) / 1e6 for row in rows
        ]
        deltas = [
            full_value - materialized_value
            for full_value, materialized_value in zip(full, materialization, strict=True)
        ]
        cells.append(
            {
                "fields": fields,
                "changed": changed,
                "trials": len(rows),
                "equivalence_verified": equivalence[(fields, changed)],
                "full_p50_ms": statistics.median(full),
                "full_p95_ms": _percentile(full, 0.95),
                "materialization_p50_ms": statistics.median(materialization),
                "materialization_p95_ms": _percentile(materialization, 0.95),
                "paired_mean_validation_and_planning_delta_ms": statistics.fmean(deltas),
            }
        )
    return {
        "schema_version": 1,
        "comparison": "full_admission_vs_prevalidated_equivalent_materialization",
        "cells": cells,
    }


def run_feature_baseline(config_path: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError(output)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise ValueError("unsupported feature baseline config")
    output.mkdir(parents=True)
    rng = random.Random(int(config["seed"]))
    observations: list[dict[str, Any]] = []
    equivalence: dict[tuple[int, int], bool] = {}
    cells = _cells(config)
    rng.shuffle(cells)
    for fields, changed in cells:
        with tempfile.TemporaryDirectory(prefix="r21-feature-baseline-") as temporary:
            root = Path(temporary)
            template_root = root / "template"
            engine, evidence_id = _seed_form(template_root, fields)
            _checkpoint(engine)
            engine.dispose()
            template = template_root / "data.db"
            reference = root / "reference.db"
            verification = root / "verification.db"
            shutil.copy2(template, reference)
            shutil.copy2(template, verification)
            _full_admission(reference, fields, changed, evidence_id)
            delta = build_database_delta(template, reference)
            verified = apply_database_delta(verification, delta)
            equivalence[(fields, changed)] = (
                verified["post_state_fingerprint"] == delta["after_fingerprint"]
            )
            total = int(config["warmups"]) + int(config["trials"])
            for pair in range(total):
                arms = ["full", "materialization"]
                rng.shuffle(arms)
                paired: dict[str, Any] = {}
                for arm in arms:
                    trial_path = root / f"{arm}-{pair}.db"
                    shutil.copy2(template, trial_path)
                    paired[arm] = (
                        _full_admission(trial_path, fields, changed, evidence_id)
                        if arm == "full"
                        else apply_database_delta(trial_path, delta)
                    )
                if pair >= int(config["warmups"]):
                    observations.append(
                        {
                            "fields": fields,
                            "changed": changed,
                            "pair": pair - int(config["warmups"]),
                            "order": arms,
                            **paired,
                        }
                    )
    raw = {"schema_version": 1, "observations": observations}
    summary = _summary(observations, equivalence)
    _write_json(output / "raw.json", raw)
    _write_json(output / "feature_baseline_summary.json", summary)
    receipt = {
        "schema_version": 1,
        "status": "complete",
        "config": config,
        "cells": len(equivalence),
        "observations": len(observations),
        "equivalence_verified_cells": sum(equivalence.values()),
        "command_failures": 0,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "sqlite": sqlite3.sqlite_version,
        },
    }
    _write_json(output / "receipt.json", receipt)
    return receipt


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_feature_baseline(args.config, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

