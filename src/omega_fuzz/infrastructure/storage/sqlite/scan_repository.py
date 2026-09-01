# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/scan_repository.py::ScanRepository."""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence

from omega_fuzz.domain.scans.scan import Scan
from omega_fuzz.domain.scans.scan_state import ScanState
from omega_fuzz.infrastructure.storage.sqlite.mappers import (
    row_to_scan,
    row_to_scan_state,
    scan_state_to_row,
    scan_to_row,
)


class SqliteScanRepository:
    """Implemente ports/scan_repository.py::ScanRepository."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, scan: Scan) -> None:
        row = scan_to_row(scan)
        columns = ", ".join(row.keys())
        placeholders = ", ".join(f":{key}" for key in row)
        self._connection.execute(
            f"INSERT OR REPLACE INTO scans ({columns}) VALUES ({placeholders})", row
        )
        self._connection.commit()

    def get(self, scan_id: str) -> Scan | None:
        cursor = self._connection.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,))
        row = cursor.fetchone()
        return row_to_scan(row) if row is not None else None

    def list_history(self) -> Sequence[Scan]:
        cursor = self._connection.execute("SELECT * FROM scans ORDER BY created_at DESC")
        return [row_to_scan(row) for row in cursor.fetchall()]

    def clear(self) -> None:
        self._connection.execute("DELETE FROM scan_states")
        self._connection.execute("DELETE FROM findings")
        self._connection.execute("DELETE FROM scans")
        self._connection.commit()

    def save_state(self, state: ScanState) -> None:
        row = scan_state_to_row(state)
        columns = ", ".join(row.keys())
        placeholders = ", ".join(f":{key}" for key in row)
        self._connection.execute(
            f"INSERT OR REPLACE INTO scan_states ({columns}) VALUES ({placeholders})", row
        )
        self._connection.commit()

    def get_state(self, scan_id: str) -> ScanState | None:
        cursor = self._connection.execute(
            "SELECT * FROM scan_states WHERE scan_id = ?", (scan_id,)
        )
        row = cursor.fetchone()
        return row_to_scan_state(row) if row is not None else None
