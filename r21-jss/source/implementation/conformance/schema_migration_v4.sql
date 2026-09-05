-- HISTORICAL G3b REFERENCE ONLY. Superseded by schema_migration_v5.sql and
-- app/adapters/database/migrations.py. Do not run this file for current data.

-- 1. Immutable authorization bindings
CREATE TABLE IF NOT EXISTS authorization_bindings (
    binding_id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL REFERENCES human_decisions(decision_id),
    certificate_id TEXT NOT NULL REFERENCES candidate_certificates(certificate_id),
    authorized_value_payload TEXT NOT NULL,
    bound_at DATETIME NOT NULL
);

-- 2. Per-field immutable source anchor map on record versions
ALTER TABLE record_versions ADD COLUMN fact_sources JSON;

-- 3. Frozen transition value on fact transitions
ALTER TABLE fact_transitions ADD COLUMN value_payload TEXT;
