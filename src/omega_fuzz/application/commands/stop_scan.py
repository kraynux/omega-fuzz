# Copyright (c) 2026 kraynux - Licence MIT
"""Arret manuel definitif d'un scan (OMEGA-FUZZ_SPECIFICATIONS.md §14.5,
OMEGA-FUZZ_ARBORESCENCE.md §16.3 : Ctrl+C en CLI, bouton « Annuler » en
TUI — finalise avec les resultats deja obtenus, `Scan.status` ->
`stopped`, distinct de `completed_truncated` (arret automatique par une
limite) et d'`aborted` (arret avant tout resultat exploitable))."""
from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from omega_fuzz.application.exceptions import InvalidScanTransitionError, ScanNotFoundError
from omega_fuzz.domain.reports.termination import TerminationReason, TerminationTrigger
from omega_fuzz.domain.scans.scan_policy import is_valid_transition
from omega_fuzz.domain.scans.scan_status import ScanStatus

if TYPE_CHECKING:
    from omega_fuzz.domain.scans.scan import Scan
    from omega_fuzz.ports.clock import Clock
    from omega_fuzz.ports.logger import Logger
    from omega_fuzz.ports.scan_repository import ScanRepository


def stop_scan(
    *, scan_repository: ScanRepository, clock: Clock, logger: Logger, scan_id: str
) -> Scan:
    scan = scan_repository.get(scan_id)
    if scan is None:
        raise ScanNotFoundError(scan_id)
    if not is_valid_transition(scan.status, ScanStatus.STOPPED):
        raise InvalidScanTransitionError(scan.status, ScanStatus.STOPPED)

    updated = replace(
        scan,
        status=ScanStatus.STOPPED,
        completed_at=clock.now(),
        termination_reason=TerminationReason(trigger=TerminationTrigger.MANUAL_STOP),
    )
    scan_repository.save(updated)
    logger.info("scan_stopped", scan_id=scan_id)
    return updated
