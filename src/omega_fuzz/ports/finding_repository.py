# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de persistance des findings (OMEGA-FUZZ_ARBORESCENCE.md
§15.3, §12/§20). Revision Phase 8 : type `Finding` reel (existe depuis
`domain.findings.finding`) au lieu du placeholder `Any` de la Phase 0 —
meme moment que la revision de `ScanRepository` en Phase 3. Respecte le
plafond `max_evidence_storage_per_scan` (OMEGA-FUZZ_SPECIFICATIONS.md
§14.2) — l'implementation concrete, pas ce contrat, applique la
troncature."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from omega_fuzz.domain.findings.finding import Finding


class FindingRepository(Protocol):
    def save(self, finding: Finding) -> None: ...

    def list_for_scan(self, scan_id: str) -> Sequence[Finding]: ...

    def clear_for_scan(self, scan_id: str) -> None: ...
