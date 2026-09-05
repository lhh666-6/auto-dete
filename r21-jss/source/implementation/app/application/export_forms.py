"""XLSX export orchestration and batch persistence."""

import hashlib
from dataclasses import asdict, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from app.adapters.export.xlsx import XlsxExporter
from app.application.query_forms import FormFilters, QueryForms
from app.domain.models import AuditEvent, ExportBatch, ExportStatus, ReviewStatus


class ExportRepository(Protocol):
    def add_export_batch(self, batch: ExportBatch) -> None: ...
    def set_export_status(self, form_id: str, status: ExportStatus) -> None: ...
    def add_audit_event(self, event: AuditEvent) -> None: ...


class ExportForms:
    def __init__(
        self,
        repository: ExportRepository,
        exporter: XlsxExporter,
        queries: QueryForms,
    ) -> None:
        self._repository = repository
        self._exporter = exporter
        self._queries = queries

    def export(
        self,
        export_type: str,
        filters: FormFilters,
        output_directory: Path,
        actor_id: str,
    ) -> ExportBatch:
        confirmed_filters = replace(filters, review_status=ReviewStatus.CONFIRMED)
        results = self._queries.search(confirmed_filters)
        batch_id = f"EXPORT-{uuid4().hex}"
        timestamp = datetime.now(UTC)
        destination = output_directory / f"{export_type}-{timestamp:%Y%m%dT%H%M%S}-{batch_id}.xlsx"
        serialized_filters = {
            key: value.value if hasattr(value, "value") else value
            for key, value in asdict(confirmed_filters).items()
            if value is not None
        }
        self._exporter.write(destination, batch_id, export_type, results, serialized_filters)
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        batch = ExportBatch(
            export_batch_id=batch_id,
            export_type=export_type,
            filters=serialized_filters,
            included_records=tuple(
                (result.form.form_id, result.current_record.version) for result in results
            ),
            file_path=str(destination),
            file_sha256=digest,
            exported_by=actor_id,
            exported_at=timestamp,
        )
        self._repository.add_export_batch(batch)
        for result in results:
            self._repository.set_export_status(result.form.form_id, ExportStatus.EXPORTED)
            self._repository.add_audit_event(
                AuditEvent(
                    event_id=f"EVENT-{uuid4().hex}",
                    form_id=result.form.form_id,
                    event_type="EXPORT",
                    actor_id=actor_id,
                    after={
                        "export_batch_id": batch_id,
                        "record_version": result.current_record.version,
                    },
                )
            )
        return batch
