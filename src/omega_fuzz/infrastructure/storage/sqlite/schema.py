# Copyright (c) 2026 kraynux - Licence MIT
"""Schema SQLite volontairement simplifie (OMEGA-FUZZ_ARBORESCENCE.md
§20) — meme discipline que D-011 (omega-fold) : pas de normalisation
poussee, les value objects imbriques de `Finding`
(target/evidence/scoring/metadata) sont serialises en colonnes JSON
plutot qu'eclates en sous-tables. Pas de `migrations.py` : un schema
unique sur un projet neuf n'a rien a versionner."""
from __future__ import annotations

SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS scans (
        scan_id TEXT PRIMARY KEY,
        target_id TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT,
        termination_trigger TEXT,
        termination_limit_name TEXT,
        termination_configured_value INTEGER,
        termination_observed_value INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS scan_states (
        scan_id TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        pending_discovery_urls TEXT NOT NULL,
        completed_test_ids TEXT NOT NULL,
        FOREIGN KEY (scan_id) REFERENCES scans (scan_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS findings (
        finding_id TEXT PRIMARY KEY,
        scan_id TEXT NOT NULL,
        title TEXT NOT NULL,
        type TEXT NOT NULL,
        status TEXT NOT NULL,
        severity_auto TEXT NOT NULL,
        severity_override TEXT,
        severity_override_reason TEXT,
        description TEXT,
        impact TEXT,
        recommendations TEXT NOT NULL,
        references_json TEXT NOT NULL,
        cwe TEXT,
        owasp_category TEXT,
        target_json TEXT NOT NULL,
        evidence_json TEXT NOT NULL,
        scoring_json TEXT NOT NULL,
        metadata_json TEXT NOT NULL,
        FOREIGN KEY (scan_id) REFERENCES scans (scan_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_findings_scan_id ON findings (scan_id)",
)
