-- REFERENCE ONLY: the canonical executable migration chain is
-- app/adapters/database/migrations.py::migrate_schema.
--
-- This file supersedes schema_migration_v4.sql, which is retained as
-- historical G3b evidence and must not be run for the v5 certificate era.
-- The Python migration is idempotent, checks existing columns, creates these
-- named constraints, records the canonical-locator era marker, and stamps
-- PRAGMA user_version only after every operation succeeds.

CREATE UNIQUE INDEX IF NOT EXISTS uq_fact_transitions_decision_id
ON fact_transitions (decision_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_fact_transitions_certificate_id
ON fact_transitions (certificate_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_authorization_bindings_decision_id
ON authorization_bindings (decision_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_authorization_bindings_certificate_id
ON authorization_bindings (certificate_id);

INSERT OR IGNORE INTO authority_meta (key, value)
VALUES ('canonical_evidence_locator_v1_started_at', '<UTC timestamp from migrator>');

PRAGMA user_version = 5;
