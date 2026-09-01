# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de persistance de l'etat/statistiques du scan
(OMEGA-FUZZ_ARBORESCENCE.md §15.3, §20). Revision Phase 3 : types reels
(`Scan`/`ScanState` existent depuis les Phases 1-2, plus besoin des
placeholders `Any` de la Phase 0) + `save_state`/`get_state` pour le
contrat pause/resume (OMEGA-FUZZ_SPECIFICATIONS.md §14.5)."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from omega_fuzz.domain.scans.scan import Scan
from omega_fuzz.domain.scans.scan_state import ScanState


class ScanRepository(Protocol):
    def save(self, scan: Scan) -> None: ...

    def get(self, scan_id: str) -> Scan | None: ...

    def list_history(self) -> Sequence[Scan]: ...

    def clear(self) -> None: ...

    def save_state(self, state: ScanState) -> None: ...

    def get_state(self, scan_id: str) -> ScanState | None: ...
