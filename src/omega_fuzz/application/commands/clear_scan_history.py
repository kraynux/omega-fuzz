# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : vider l'historique des scans (ecran Reglages). Porte depuis
omega-check (D-007/D-008) — `ScanRepository.clear()` (Phase 9b) vide deja
scans/etats/findings en un seul geste, rien a granulariser cote
omega-fuzz."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omega_fuzz.ports.scan_repository import ScanRepository


def clear_scan_history(*, scan_repository: ScanRepository) -> None:
    scan_repository.clear()
