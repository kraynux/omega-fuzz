# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/id_generator.py::IdGenerator. Delegue a
omega_lib.shared.ids.new_id (UUID, D-006). Les IDs scan-scopes
(target_id/test_id/request_id) ne passent plus par ce port depuis la
Phase 2 (voir ports/id_generator.py) — construits par des fonctions
pures du domaine a la place."""
from __future__ import annotations

from omega_lib.shared.ids import new_id


class SystemIdGenerator:
    def new_scan_id(self) -> str:
        return new_id()
