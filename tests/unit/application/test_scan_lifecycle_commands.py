# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from omega_fuzz.application.commands.pause_scan import pause_scan
from omega_fuzz.application.commands.resume_scan import resume_scan
from omega_fuzz.application.commands.stop_scan import stop_scan
from omega_fuzz.application.exceptions import InvalidScanTransitionError, ScanNotFoundError
from omega_fuzz.domain.reports.termination import TerminationTrigger
from omega_fuzz.domain.scans.scan import Scan
from omega_fuzz.domain.scans.scan_id import ScanId
from omega_fuzz.domain.scans.scan_status import ScanStatus

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _running_scan(scan_id: str = "11111111111111111111111111111111") -> Scan:
    return Scan(
        scan_id=ScanId(scan_id),
        target_id="example_root",
        status=ScanStatus.RUNNING,
        created_at=NOW,
        started_at=NOW,
    )


def test_pause_then_resume_round_trip(scan_repository, logger) -> None:
    scan = _running_scan()
    scan_repository.save(scan)

    paused = pause_scan(
        scan_repository=scan_repository,
        logger=logger,
        scan_id=scan.scan_id.value,
        pending_discovery_urls=["https://example.com/a", "https://example.com/b"],
        completed_test_ids=["test_fuzzhttp_example_root_000001"],
    )
    assert paused.status is ScanStatus.PAUSED

    resumed, state = resume_scan(
        scan_repository=scan_repository, logger=logger, scan_id=scan.scan_id.value
    )
    assert resumed.status is ScanStatus.RUNNING
    assert state.pending_discovery_urls == ("https://example.com/a", "https://example.com/b")
    assert state.completed_test_ids == frozenset({"test_fuzzhttp_example_root_000001"})


def test_pause_unknown_scan_raises(scan_repository, logger) -> None:
    with pytest.raises(ScanNotFoundError):
        pause_scan(scan_repository=scan_repository, logger=logger, scan_id="unknown")


def test_pause_from_terminal_status_is_invalid(scan_repository, logger) -> None:
    scan = replace(_running_scan(), status=ScanStatus.COMPLETED)
    scan_repository.save(scan)

    with pytest.raises(InvalidScanTransitionError):
        pause_scan(scan_repository=scan_repository, logger=logger, scan_id=scan.scan_id.value)


def test_resume_without_prior_pause_raises(scan_repository, logger) -> None:
    scan = replace(_running_scan(), status=ScanStatus.PAUSED)
    scan_repository.save(scan)

    with pytest.raises(ScanNotFoundError):
        resume_scan(scan_repository=scan_repository, logger=logger, scan_id=scan.scan_id.value)


def test_stop_sets_manual_stop_termination_reason(scan_repository, clock, logger) -> None:
    scan = _running_scan()
    scan_repository.save(scan)

    stopped = stop_scan(
        scan_repository=scan_repository, clock=clock, logger=logger, scan_id=scan.scan_id.value
    )

    assert stopped.status is ScanStatus.STOPPED
    assert stopped.termination_reason is not None
    assert stopped.termination_reason.trigger is TerminationTrigger.MANUAL_STOP
    assert stopped.completed_at == clock.now()
