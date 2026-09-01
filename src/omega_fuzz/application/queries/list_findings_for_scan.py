# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : lister les findings d'un scan passe (ecran Historique)."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from omega_fuzz.domain.findings.finding import Finding
    from omega_fuzz.ports.finding_repository import FindingRepository


def list_findings_for_scan(*, finding_repository: FindingRepository, scan_id: str) -> Sequence[Finding]:
    return finding_repository.list_for_scan(scan_id)
