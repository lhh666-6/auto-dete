import sqlite3

from auto_decte_agent_benchmark.digests import digest_state
from auto_decte_agent_benchmark.state_probe import snapshot_sqlite


def test_snapshot_is_logical_sorted_and_separates_candidate_from_authority(tmp_path) -> None:
    database = tmp_path / "state.db"
    with sqlite3.connect(database) as connection:
        connection.executescript(
            """
            PRAGMA user_version = 7;
            CREATE TABLE forms (form_id TEXT PRIMARY KEY, current_record_version INTEGER);
            CREATE TABLE candidate_certificates (certificate_id TEXT PRIMARY KEY, value TEXT);
            INSERT INTO forms VALUES ('F2', 0), ('F1', 0);
            INSERT INTO candidate_certificates VALUES ('C1', '8');
            """
        )

    before = digest_state(snapshot_sqlite(database))
    with sqlite3.connect(database) as connection:
        connection.execute("INSERT INTO candidate_certificates VALUES ('C2', '9')")
    candidate_changed = digest_state(snapshot_sqlite(database))
    with sqlite3.connect(database) as connection:
        connection.execute("UPDATE forms SET current_record_version = 1 WHERE form_id = 'F1'")
    authority_changed = digest_state(snapshot_sqlite(database))

    assert candidate_changed.candidate != before.candidate
    assert candidate_changed.authority == before.authority
    assert authority_changed.authority != candidate_changed.authority


def test_snapshot_rejects_missing_database(tmp_path) -> None:
    try:
        snapshot_sqlite(tmp_path / "missing.db")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("missing database must not be created implicitly")
