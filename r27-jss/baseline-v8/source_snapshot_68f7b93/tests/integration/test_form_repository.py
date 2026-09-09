from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import create_engine

from app.adapters.database.models import Base
from app.adapters.database.repositories import SqlAlchemyFormRepository
from app.domain.models import Form
from tests.helpers.legacy_fixtures import add_legacy_record_version

NOW = datetime(2026, 1, 1, 9, 0, tzinfo=UTC)


def test_repository_retains_history_and_points_to_latest_version(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'demo.db'}")
    Base.metadata.create_all(engine)
    repository = SqlAlchemyFormRepository(engine)
    repository.add_form(Form("FORM-0001", "T1", "1"))
    add_legacy_record_version(
        engine,
        form_id="FORM-0001",
        version=1,
        values={"total_quantity": 10},
        confirmed_by="reviewer-old",
        created_at=NOW,
        record_id="RECORD-1",
    )
    add_legacy_record_version(
        engine,
        form_id="FORM-0001",
        version=2,
        values={"total_quantity": 12},
        confirmed_by="reviewer-old",
        created_at=NOW,
        record_id="RECORD-2",
    )

    restored = repository.get_form("FORM-0001")
    versions = repository.list_record_versions("FORM-0001")

    assert restored is not None
    assert restored.current_record_version == 2
    assert [version.version for version in versions] == [1, 2]
    assert versions[0].values == {"total_quantity": 10}
    assert versions[1].values == {"total_quantity": 12}
