# Copyright (c) 2026 kraynux - Licence MIT
"""Session de scan (OMEGA-FUZZ_ARBORESCENCE.md §7)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from omega_fuzz.domain.reports.termination import TerminationReason
from omega_fuzz.domain.scans.scan_id import ScanId
from omega_fuzz.domain.scans.scan_status import ScanStatus


@dataclass(frozen=True, slots=True)
class Scan:
    scan_id: ScanId
    target_id: str
    status: ScanStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    termination_reason: TerminationReason | None = None
