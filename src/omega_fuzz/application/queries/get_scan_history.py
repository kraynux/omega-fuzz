# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : lister les scans passes (ecran Historique). Porte depuis
omega-check (D-007/D-008). `ScanRepository.list_history()` (Phase 9b)
trie deja par `created_at DESC` cote SQLite."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from omega_fuzz.domain.scans.scan import Scan
    from omega_fuzz.ports.scan_repository import ScanRepository


def get_scan_history(*, scan_repository: ScanRepository) -> Sequence[Scan]:
    return scan_repository.list_history()
