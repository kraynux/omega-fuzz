# Copyright (c) 2026 kraynux - Licence MIT
"""Statuts de scan (OMEGA-FUZZ_ARBORESCENCE.md §7,
OMEGA-FUZZ_SPECIFICATIONS.md §14.5)."""
from __future__ import annotations

from enum import Enum


class ScanStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    COMPLETED_TRUNCATED = "completed_truncated"
    STOPPED = "stopped"
    ABORTED = "aborted"
    FAILED = "failed"


TERMINAL_STATUSES = frozenset(
    {
        ScanStatus.COMPLETED,
        ScanStatus.COMPLETED_TRUNCATED,
        ScanStatus.STOPPED,
        ScanStatus.ABORTED,
        ScanStatus.FAILED,
    }
)
