"""E7/E8 admission, reverse-trace, and authority-storage characterization."""

from __future__ import annotations

import argparse
import json
import platform
import random
import shutil
import sqlite3
import statistics
import sys
import tempfile
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, event, func, insert, select, update
from sqlalchemy.engine import Engine

from app.adapters.database.authority_facades import AuthorityReadFacade, FactAdmissionFacade
from app.adapters.database.migrations import migrate_schema
from app.adapters.database.models import Base, FormFieldRow, FormRow, RecordVersionRow
from app.adapters.database.repositories import SqlAlchemyFormRepository, install_sqlite_pragmas
from app.adapters.storage.local import LocalEvidenceStorage
from app.application.import_forms import ImportForms
from app.application.query_forms import QueryForms
from app.application.review_forms import ReviewForms
from app.domain.models import FormField, RecordStatus, utc_now
from app.domain.principal import prototype_principal_policy

TABLES = tuple(Base.metadata.sorted_tables)


def _write_object(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _engine(path: Path) -> Engine:
    engine = create_engine(f"sqlite:///{path}")
    install_sqlite_pragmas(engine)
    return engine


def _review_service(repository: SqlAlchemyFormRepository) -> ReviewForms:
    return ReviewForms(
        repository,
        repository,
        authority_read=AuthorityReadFacade(repository),
        admission=FactAdmissionFacade(repository),
        known_producers=frozenset({("human-reviewer", "manual-entry-v1")}),
        known_selection_artifacts=frozenset({"recognition-threshold-v1"}),
    )


def _seed_form(root: Path, field_count: int, form_id: str = "FORM-1") -> tuple[Engine, str]:
    root.mkdir(parents=True, exist_ok=True)
    engine = _engine(root / "data.db")
    Base.metadata.create_all(engine)
    migrate_schema(engine)
    repository = SqlAlchemyFormRepository(
        engine, principal_policy=prototype_principal_policy(("reviewer",))
    )
    image = root / f"{form_id}.png"
    image.write_bytes(f"evidence:{form_id}".encode())
    evidence = ImportForms(
        repository, repository, repository, LocalEvidenceStorage(root / "evidence")
    ).import_image(image, form_id, "T1", "1", "benchmark")
    values = {f"f{index:03d}": 0 for index in range(field_count)}
    for index, field_name in enumerate(values):
        repository.add_form_field(FormField(f"{form_id}-FIELD-{index}", form_id, field_name, {}))
    _review_service(repository).confirm(
        form_id,
        0,
        values,
        "reviewer",
        "benchmark pre-state",
        certificate_ids_by_field={field: None for field in values},
        manual_evidence_ids_by_field={field: evidence.file_id for field in values},
    )
    return engine, evidence.file_id


def _checkpoint(engine: Engine) -> None:
    with engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA wal_checkpoint(TRUNCATE)")


def _row_count(engine: Engine) -> int:
    with engine.connect() as connection:
        return sum(
            connection.scalar(select(func.count()).select_from(table)) or 0 for table in TABLES
        )


def _measure(engine: Engine, action: Callable[[], None]) -> tuple[int, int]:
    statements = 0

    def count_statement(*args: Any) -> None:
        nonlocal statements
        statements += 1

    event.listen(engine, "before_cursor_execute", count_statement)
    started = time.perf_counter_ns()
    try:
        action()
    finally:
        elapsed = time.perf_counter_ns() - started
        event.remove(engine, "before_cursor_execute", count_statement)
    return elapsed, statements


def _full_admission(
    db_path: Path, field_count: int, changed_count: int, evidence_id: str
) -> dict[str, Any]:
    engine = _engine(db_path)
    repository = SqlAlchemyFormRepository(
        engine, principal_policy=prototype_principal_policy(("reviewer",))
    )
    values = {f"f{index:03d}": int(index < changed_count) for index in range(field_count)}
    before_rows = _row_count(engine)

    def action() -> None:
        _review_service(repository).confirm(
            "FORM-1",
            1,
            values,
            "reviewer",
            "measured correction",
            certificate_ids_by_field={field: None for field in values},
            manual_evidence_ids_by_field={field: evidence_id for field in values},
        )

    elapsed, statements = _measure(engine, action)
    assert QueryForms(repository).trace("FORM-1").status == "complete"
    after_rows = _row_count(engine)
    _checkpoint(engine)
    engine.dispose()
    return {
        "latency_ns": elapsed,
        "sql_statements": statements,
        "rows_written": after_rows - before_rows,
    }


def _lower_bound(db_path: Path, field_count: int, changed_count: int) -> dict[str, Any]:
    engine = _engine(db_path)
    values = {f"f{index:03d}": int(index < changed_count) for index in range(field_count)}
    before_rows = _row_count(engine)

    def action() -> None:
        with engine.begin() as connection:
            result = connection.execute(
                update(FormRow)
                .where(FormRow.form_id == "FORM-1")
                .where(FormRow.current_record_version == 1)
                .values(current_record_version=2)
            )
            assert result.rowcount == 1
            connection.execute(
                insert(RecordVersionRow).values(
                    record_id="LOWER-REC-2",
                    form_id="FORM-1",
                    version=2,
                    previous_version=1,
                    status=RecordStatus.CORRECTED.value,
                    values=values,
                    fact_sources={},
                    change_reason="minimal snapshot CAS",
                    confirmed_by="reviewer",
                    created_at=utc_now(),
                )
            )
            for field_name, value in values.items():
                connection.execute(
                    update(FormFieldRow)
                    .where(FormFieldRow.form_id == "FORM-1")
                    .where(FormFieldRow.field_name == field_name)
                    .values(current_value=value, current_record_version=2)
                )

    elapsed, statements = _measure(engine, action)
    after_rows = _row_count(engine)
    _checkpoint(engine)
    engine.dispose()
    return {
        "latency_ns": elapsed,
        "sql_statements": statements,
        "rows_written": after_rows - before_rows,
    }


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * fraction))]


def _paired_interval(deltas: list[float], seed: int, draws: int = 2000) -> list[float]:
    rng = random.Random(seed)
    means = [statistics.fmean(rng.choice(deltas) for _ in deltas) for _ in range(draws)]
    return [_percentile(means, 0.025), _percentile(means, 0.975)]


def _admission_experiment(config: dict[str, Any], root: Path) -> dict[str, Any]:
    rng = random.Random(int(config["seed"]))
    observations: list[dict[str, Any]] = []
    cells = []
    for field_count in config["admission_fields"]:
        for changed in config["admission_changed"]:
            changed_count = field_count if changed == "all" else min(int(changed), field_count)
            cell = (int(field_count), changed_count)
            if cell not in cells:
                cells.append(cell)
    rng.shuffle(cells)
    for field_count, changed_count in cells:
        with tempfile.TemporaryDirectory(prefix="admission-cell-") as temporary:
            template_root = Path(temporary) / "template"
            engine, evidence_id = _seed_form(template_root, field_count)
            _checkpoint(engine)
            engine.dispose()
            template = template_root / "data.db"
            total = int(config["warmups"]) + int(config["trials"])
            for pair in range(total):
                arms = ["full", "lower"]
                rng.shuffle(arms)
                paired: dict[str, Any] = {}
                for arm in arms:
                    trial_path = Path(temporary) / f"{arm}-{pair}.db"
                    shutil.copy2(template, trial_path)
                    before_bytes = trial_path.stat().st_size
                    result = (
                        _full_admission(trial_path, field_count, changed_count, evidence_id)
                        if arm == "full"
                        else _lower_bound(trial_path, field_count, changed_count)
                    )
                    result["main_db_byte_delta"] = trial_path.stat().st_size - before_bytes
                    paired[arm] = result
                if pair >= int(config["warmups"]):
                    observations.append(
                        {
                            "fields": field_count,
                            "changed": changed_count,
                            "pair": pair - int(config["warmups"]),
                            "order": arms,
                            **paired,
                        }
                    )
    return {"schema_version": 1, "observations": observations}


def _trace_experiment(config: dict[str, Any]) -> dict[str, Any]:
    observations: list[dict[str, Any]] = []
    for fields in config["trace_fields"]:
        for versions in config["trace_versions"]:
            for records in config["trace_records"]:
                with tempfile.TemporaryDirectory(prefix="trace-cell-") as temporary:
                    root = Path(temporary)
                    engine, evidence_id = _seed_form(root, int(fields))
                    repository = SqlAlchemyFormRepository(
                        engine, principal_policy=prototype_principal_policy(("reviewer",))
                    )
                    review = _review_service(repository)
                    values = {f"f{index:03d}": 0 for index in range(int(fields))}
                    for version in range(2, int(versions) + 1):
                        values["f000"] = version
                        review.confirm(
                            "FORM-1",
                            version - 1,
                            values,
                            "reviewer",
                            "trace history",
                            certificate_ids_by_field={field: None for field in values},
                            manual_evidence_ids_by_field={field: evidence_id for field in values},
                        )
                    for record_index in range(1, int(records)):
                        form_id = f"OTHER-{record_index}"
                        image = root / f"{form_id}.png"
                        image.write_bytes(f"distractor:{form_id}".encode())
                        evidence = ImportForms(
                            repository,
                            repository,
                            repository,
                            LocalEvidenceStorage(root / "evidence"),
                        ).import_image(image, form_id, "T1", "1", "benchmark")
                        repository.add_form_field(
                            FormField(f"{form_id}-FIELD-0", form_id, "f000", {})
                        )
                        review.confirm(
                            form_id,
                            0,
                            {"f000": record_index},
                            "reviewer",
                            "trace distractor",
                            certificate_ids_by_field={"f000": None},
                            manual_evidence_ids_by_field={"f000": evidence.file_id},
                        )
                    query = QueryForms(repository)
                    assert query.trace("FORM-1").status == "complete"
                    total = int(config["warmups"]) + int(config["trials"])
                    for trial in range(total):
                        elapsed, statements = _measure(
                            engine, lambda query=query: _assert_complete(query.trace("FORM-1"))
                        )
                        if trial >= int(config["warmups"]):
                            observations.append(
                                {
                                    "fields": fields,
                                    "versions": versions,
                                    "records": records,
                                    "trial": trial - int(config["warmups"]),
                                    "latency_ns": elapsed,
                                    "sql_statements": statements,
                                }
                            )
                    engine.dispose()
    return {"schema_version": 1, "observations": observations}


def _assert_complete(trace: Any) -> None:
    assert trace.status == "complete"


def _populate_storage(path: Path, transitions: int, full: bool) -> dict[str, Any]:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    now = datetime.now(UTC).isoformat()
    connection.execute(
        "INSERT INTO forms VALUES (?,?,?,?,?,?,?,?)",
        ("FORM-1", "T1", "1", "1", "CONFIRMED", "NOT_EXPORTED", transitions, now),
    )
    connection.execute(
        "INSERT INTO form_fields VALUES (?,?,?,?,?,?,?)",
        (
            "FIELD-1",
            "FORM-1",
            "f000",
            "{}",
            transitions,
            f"T-{transitions}" if full else None,
            transitions,
        ),
    )
    if full:
        connection.execute(
            "INSERT INTO evidence_files VALUES (?,?,?,?,?,?,?,?)",
            (
                "EVID-1",
                "FORM-1",
                "FIELD-1",
                "ORIGINAL_IMAGE",
                "evidence://stable",
                "ab" * 32,
                1,
                now,
            ),
        )
    chunk = 2000
    for start in range(1, transitions + 1, chunk):
        stop = min(transitions + 1, start + chunk)
        versions = [
            (
                f"REC-{i}",
                "FORM-1",
                i,
                i - 1 if i > 1 else None,
                "CONFIRMED" if i == 1 else "CORRECTED",
                json.dumps({"f000": i}),
                json.dumps({"f000": f"T-{i}"}) if full else "{}",
                "storage",
                "reviewer",
                now,
            )
            for i in range(start, stop)
        ]
        connection.executemany("INSERT INTO record_versions VALUES (?,?,?,?,?,?,?,?,?,?)", versions)
        audits = [
            (
                f"A-{i}",
                "FORM-1",
                "CONFIRM",
                "reviewer",
                now,
                None,
                json.dumps({"f000": i}),
                "storage",
                "[]",
            )
            for i in range(start, stop)
        ]
        connection.executemany("INSERT INTO audit_events VALUES (?,?,?,?,?,?,?,?,?)", audits)
        if full:
            certificates = [
                (
                    f"C-{i}",
                    f"CAN-{i}",
                    "f000",
                    "FORM-1",
                    None,
                    "EVID-1",
                    None,
                    json.dumps(i),
                    "ab" * 32,
                    "evidence:v1:FORM-1:-:evidence://stable:" + "ab" * 32,
                    "T1",
                    "1",
                    "manual_entry",
                    "human-reviewer",
                    "manual-entry-v1",
                    None,
                    1.0,
                    "accepted",
                    "[]",
                    "FORM-1",
                    i - 1,
                    now,
                )
                for i in range(start, stop)
            ]
            connection.executemany(
                "INSERT INTO candidate_certificates VALUES "
                "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                certificates,
            )
            decisions = [
                (f"D-{i}", "FORM-1", f"CAN-{i}", "f000", "reviewer", "storage", 0, now)
                for i in range(start, stop)
            ]
            connection.executemany(
                "INSERT INTO human_decisions VALUES (?,?,?,?,?,?,?,?)", decisions
            )
            bindings = [
                (f"B-{i}", f"D-{i}", f"C-{i}", json.dumps(i), now) for i in range(start, stop)
            ]
            connection.executemany(
                "INSERT INTO authorization_bindings VALUES (?,?,?,?,?)", bindings
            )
            facts = [
                (
                    f"T-{i}",
                    "FORM-1",
                    i,
                    "f000",
                    "FORM-1",
                    f"REC-{i}",
                    f"D-{i}",
                    f"C-{i}",
                    "ab" * 32,
                    "evidence:v1:FORM-1:-:evidence://stable:" + "ab" * 32,
                    "human-reviewer",
                    "manual-entry-v1",
                    "T1",
                    "1",
                    "manual_entry",
                    json.dumps(i),
                    now,
                )
                for i in range(start, stop)
            ]
            connection.executemany(
                "INSERT INTO fact_transitions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", facts
            )
        connection.commit()
    foreign_key_failures = list(connection.execute("PRAGMA foreign_key_check"))
    connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    connection.execute("VACUUM")
    connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    page_size = connection.execute("PRAGMA page_size").fetchone()[0]
    page_count = connection.execute("PRAGMA page_count").fetchone()[0]
    freelist = connection.execute("PRAGMA freelist_count").fetchone()[0]
    connection.close()
    wal_bytes = Path(f"{path}-wal").stat().st_size if Path(f"{path}-wal").exists() else 0
    shm_bytes = Path(f"{path}-shm").stat().st_size if Path(f"{path}-shm").exists() else 0
    assert wal_bytes == 0 and shm_bytes == 0
    return {
        "bytes": path.stat().st_size,
        "page_size": page_size,
        "page_count": page_count,
        "freelist_count": freelist,
        "wal_bytes": wal_bytes,
        "shm_bytes": shm_bytes,
        "foreign_key_failures": foreign_key_failures,
    }


def _storage_experiment(config: dict[str, Any], root: Path) -> dict[str, Any]:
    observations = []
    for transitions in config["storage_transitions"]:
        cell = root / f"storage-{transitions}"
        cell.mkdir(parents=True)
        full_path = cell / "full.db"
        lower_path = cell / "lower.db"
        for path in (full_path, lower_path):
            engine = _engine(path)
            Base.metadata.create_all(engine)
            migrate_schema(engine)
            engine.dispose()
        full = _populate_storage(full_path, int(transitions), True)
        lower = _populate_storage(lower_path, int(transitions), False)
        observations.append(
            {
                "transitions": transitions,
                "full": full,
                "lower": lower,
                "incremental_bytes": full["bytes"] - lower["bytes"],
            }
        )
    return {"schema_version": 1, "observations": observations}


def _summarize(
    admission: dict[str, Any], trace: dict[str, Any], storage: dict[str, Any], seed: int
) -> dict[str, Any]:
    admission_cells = []
    keys = sorted({(row["fields"], row["changed"]) for row in admission["observations"]})
    for fields, changed in keys:
        rows = [
            row
            for row in admission["observations"]
            if (row["fields"], row["changed"]) == (fields, changed)
        ]
        full = [row["full"]["latency_ns"] / 1e6 for row in rows]
        lower = [row["lower"]["latency_ns"] / 1e6 for row in rows]
        deltas = [a - b for a, b in zip(full, lower, strict=True)]
        admission_cells.append(
            {
                "fields": fields,
                "changed": changed,
                "trials": len(rows),
                "full_p50_ms": statistics.median(full),
                "full_p95_ms": _percentile(full, 0.95),
                "lower_p50_ms": statistics.median(lower),
                "paired_mean_delta_ms": statistics.fmean(deltas),
                "paired_mean_delta_95ci_ms": _paired_interval(deltas, seed + fields + changed),
            }
        )
    trace_cells = []
    trace_keys = sorted({(r["fields"], r["versions"], r["records"]) for r in trace["observations"]})
    for fields, versions, records in trace_keys:
        values = [
            row["latency_ns"] / 1e6
            for row in trace["observations"]
            if (row["fields"], row["versions"], row["records"]) == (fields, versions, records)
        ]
        trace_cells.append(
            {
                "fields": fields,
                "versions": versions,
                "records": records,
                "trials": len(values),
                "p50_ms": statistics.median(values),
                "p95_ms": _percentile(values, 0.95),
            }
        )
    return {"admission": admission_cells, "trace": trace_cells, "storage": storage["observations"]}


def run_cost_benchmark(config_path: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    (output / "raw").mkdir()
    (output / "paper_inputs").mkdir()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise ValueError("unsupported cost config")
    admission = _admission_experiment(config, output)
    _write_object(output / "raw" / "admission.json", admission)
    trace = _trace_experiment(config)
    _write_object(output / "raw" / "trace.json", trace)
    storage = _storage_experiment(config, output)
    _write_object(output / "raw" / "storage.json", storage)
    summary = _summarize(admission, trace, storage, int(config["seed"]))
    _write_object(output / "paper_inputs" / "cost_summary.json", summary)
    receipt = {
        "schema_version": 1,
        "status": "complete",
        "config": config,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "sqlite": sqlite3.sqlite_version,
        },
    }
    _write_object(output / "receipt.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_cost_benchmark(args.config, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
