# Copyright (c) 2026 kraynux - Licence MIT
"""Suspend l'execution d'un scan (OMEGA-FUZZ_SPECIFICATIONS.md §14.5,
OMEGA-FUZZ_ARBORESCENCE.md §16.3 : suspend la planification, persiste
l'etat de la file de decouverte/fuzzing restante, `Scan.status` ->
`paused`)."""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import replace
from typing import TYPE_CHECKING

from omega_fuzz.application.exceptions import InvalidScanTransitionError, ScanNotFoundError
from omega_fuzz.domain.scans.scan_policy import is_valid_transition
from omega_fuzz.domain.scans.scan_state import ScanState
from omega_fuzz.domain.scans.scan_status import ScanStatus

if TYPE_CHECKING:
    from omega_fuzz.domain.scans.scan import Scan
    from omega_fuzz.ports.logger import Logger
    from omega_fuzz.ports.scan_repository import ScanRepository


def pause_scan(
    *,
    scan_repository: ScanRepository,
    logger: Logger,
    scan_id: str,
    pending_discovery_urls: Sequence[str] = (),
    completed_test_ids: Iterable[str] = (),
) -> Scan:
    scan = scan_repository.get(scan_id)
    if scan is None:
        raise ScanNotFoundError(scan_id)
    if not is_valid_transition(scan.status, ScanStatus.PAUSED):
        raise InvalidScanTransitionError(scan.status, ScanStatus.PAUSED)

    scan_repository.save_state(
        ScanState(
            scan_id=scan_id,
            status=ScanStatus.PAUSED,
            pending_discovery_urls=tuple(pending_discovery_urls),
            completed_test_ids=frozenset(completed_test_ids),
        )
    )
    updated = replace(scan, status=ScanStatus.PAUSED)
    scan_repository.save(updated)
    logger.info("scan_paused", scan_id=scan_id)
    return updated
