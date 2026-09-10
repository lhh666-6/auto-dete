"""Test-only helpers for seeding pre-certificate history directly in the DB.

Fact writing in production goes exclusively through the authority
transaction (ReviewForms.confirm -> append_fact_transition). These helpers
write rows directly with a SQLAlchemy session so tests can build legacy
(pre-certificate) state without keeping a production bypass.
"""

from datetime import datetime

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.adapters.database.models import AuditEventRow, FormRow, RecordVersionRow


def add_legacy_record_version(
    engine: Engine,
    *,
    form_id: str,
    version: int,
    values: dict[str, object],
    confirmed_by: str,
    reason: str = "legacy",
    created_at: datetime,
    record_id: str | None = None,
) -> str:
    """Insert one pre-certificate record version and its CONFIRM audit row."""
    with Session(engine) as session, session.begin():
        form = session.get(FormRow, form_id)
        if form is None:
            raise KeyError(f"Unknown form: {form_id}")
        if version != form.current_record_version + 1:
            raise ValueError("Record versions must be appended sequentially")
        resolved_record_id = record_id or f"REC-LEGACY-{form_id}-{version}"
        session.add(
            RecordVersionRow(
                record_id=resolved_record_id,
                form_id=form_id,
                version=version,
                previous_version=(version - 1) or None,
                status="CONFIRMED",
                values=values,
                change_reason=reason,
                confirmed_by=confirmed_by,
                created_at=created_at,
            )
        )
        form.current_record_version = version
        form.review_status = "CONFIRMED"
        session.add(
            AuditEventRow(
                event_id=f"EVENT-LEGACY-{form_id}-{version}",
                form_id=form_id,
                event_type="CONFIRM",
                actor_id=confirmed_by,
                timestamp=created_at,
                before=None,
                after=values,
                reason=reason,
                evidence_ids=[],
            )
        )
    return resolved_record_id
