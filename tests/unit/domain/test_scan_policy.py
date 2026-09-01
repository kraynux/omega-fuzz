# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import pytest

from omega_fuzz.domain.scans.scan_policy import is_valid_transition
from omega_fuzz.domain.scans.scan_status import TERMINAL_STATUSES, ScanStatus


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (ScanStatus.PLANNED, ScanStatus.RUNNING),
        (ScanStatus.PLANNED, ScanStatus.ABORTED),
        (ScanStatus.RUNNING, ScanStatus.PAUSED),
        (ScanStatus.PAUSED, ScanStatus.RUNNING),
        (ScanStatus.RUNNING, ScanStatus.COMPLETED),
        (ScanStatus.RUNNING, ScanStatus.COMPLETED_TRUNCATED),
        (ScanStatus.RUNNING, ScanStatus.STOPPED),
        (ScanStatus.RUNNING, ScanStatus.FAILED),
        (ScanStatus.PAUSED, ScanStatus.STOPPED),
        (ScanStatus.PAUSED, ScanStatus.COMPLETED_TRUNCATED),
    ],
)
def test_valid_transitions(current: ScanStatus, target: ScanStatus) -> None:
    assert is_valid_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (ScanStatus.PLANNED, ScanStatus.COMPLETED),
        (ScanStatus.PLANNED, ScanStatus.PAUSED),
        (ScanStatus.COMPLETED, ScanStatus.RUNNING),
        (ScanStatus.STOPPED, ScanStatus.RUNNING),
        (ScanStatus.FAILED, ScanStatus.COMPLETED),
    ],
)
def test_invalid_transitions(current: ScanStatus, target: ScanStatus) -> None:
    assert not is_valid_transition(current, target)


def test_terminal_statuses_have_no_outgoing_transition() -> None:
    for status in TERMINAL_STATUSES:
        for target in ScanStatus:
            assert not is_valid_transition(status, target)
