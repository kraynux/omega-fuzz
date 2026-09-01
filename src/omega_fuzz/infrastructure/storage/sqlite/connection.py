# Copyright (c) 2026 kraynux - Licence MIT
"""Ouvre une connexion SQLite et applique le schema
(OMEGA-FUZZ_ARBORESCENCE.md §20). `sqlite3` confine a cette sous-couche
(contrat import-linter dedie)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from omega_fuzz.infrastructure.storage.sqlite.schema import SCHEMA_STATEMENTS


def open_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
    connection.commit()
    return connection
