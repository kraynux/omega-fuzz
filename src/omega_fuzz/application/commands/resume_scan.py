# Copyright (c) 2026 kraynux - Licence MIT
"""Reprend un scan suspendu (OMEGA-FUZZ_SPECIFICATIONS.md §14.5,
OMEGA-FUZZ_ARBORESCENCE.md §16.3 : recharge l'etat persiste par
`pause_scan`, reprend exactement la ou le scan s'est arrete — aucun
test deja execute n'est rejoue —, `Scan.status` -> `running`)."""
from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from omega_fuzz.application.exceptions import InvalidScanTransitionError, ScanNotFoundError
from omega_fuzz.domain.scans.scan_policy import is_valid_transition
from omega_fuzz.domain.scans.scan_status import ScanStatus

if TYPE_CHECKING:
    from omega_fuzz.domain.scans.scan import Scan
    from omega_fuzz.domain.scans.scan_state import ScanState
    from omega_fuzz.ports.logger import Logger
    from omega_fuzz.ports.scan_repository import ScanRepository


def resume_scan(
    *, scan_repository: ScanRepository, logger: Logger, scan_id: str
) -> tuple[Scan, ScanState]:
    scan = scan_repository.get(scan_id)
    if scan is None:
        raise ScanNotFoundError(scan_id)
    if not is_valid_transition(scan.status, ScanStatus.RUNNING):
        raise InvalidScanTransitionError(scan.status, ScanStatus.RUNNING)

    state = scan_repository.get_state(scan_id)
    if state is None:
        raise ScanNotFoundError(f"{scan_id} (aucun etat de pause persiste)")

    updated = replace(scan, status=ScanStatus.RUNNING)
    scan_repository.save(updated)
    logger.info("scan_resumed", scan_id=scan_id)
    return updated, state
