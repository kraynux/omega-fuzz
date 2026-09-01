# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/finding_repository.py::FindingRepository. Le
plafond `max_evidence_storage_per_scan` (ARBORESCENCE §20) n'est pas
applique ici — le port `save` ne recoit pas les limites effectives du
scan, coupe de perimetre documentee (voir le plan Phase 9b)."""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence

from omega_fuzz.domain.findings.finding import Finding
from omega_fuzz.infrastructure.storage.sqlite.mappers import finding_to_row, row_to_finding


class SqliteFindingRepository:
    """Implemente ports/finding_repository.py::FindingRepository."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, finding: Finding) -> None:
        row = finding_to_row(finding)
        columns = ", ".join(row.keys())
        placeholders = ", ".join(f":{key}" for key in row)
        self._connection.execute(
            f"INSERT OR REPLACE INTO findings ({columns}) VALUES ({placeholders})", row
        )
        self._connection.commit()

    def list_for_scan(self, scan_id: str) -> Sequence[Finding]:
        cursor = self._connection.execute("SELECT * FROM findings WHERE scan_id = ?", (scan_id,))
        return [row_to_finding(row) for row in cursor.fetchall()]

    def clear_for_scan(self, scan_id: str) -> None:
        self._connection.execute("DELETE FROM findings WHERE scan_id = ?", (scan_id,))
        self._connection.commit()
