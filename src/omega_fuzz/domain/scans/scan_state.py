# Copyright (c) 2026 kraynux - Licence MIT
"""Forme de l'etat resumable pause/resume (OMEGA-FUZZ_SPECIFICATIONS.md
§14.5) : ce que `pause` doit persister pour qu'un `resume` reprenne
exactement la ou le scan s'est arrete, sans rejouer un test deja
execute. Objet de valeur minimal a ce stade (Phase 2) — pas encore
cable a un repository ni a une vraie file de decouverte/fuzzing, ce
cablage arrive en Phase 3 (Limites) avec les commandes `pause_scan`/
`resume_scan`."""
from __future__ import annotations

from dataclasses import dataclass, field

from omega_fuzz.domain.scans.scan_status import ScanStatus


@dataclass(frozen=True, slots=True)
class ScanState:
    scan_id: str
    status: ScanStatus
    pending_discovery_urls: tuple[str, ...] = ()
    completed_test_ids: frozenset[str] = field(default_factory=frozenset)
