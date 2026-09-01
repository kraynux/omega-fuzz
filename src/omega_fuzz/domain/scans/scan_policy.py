# Copyright (c) 2026 kraynux - Licence MIT
"""Transitions legales de `ScanStatus` (OMEGA-FUZZ_ARBORESCENCE.md §7,
OMEGA-FUZZ_SPECIFICATIONS.md §14.5). `planned -> aborted` couvre le cas
d'une erreur de configuration decouverte en preparation, avant meme le
premier `running` (mentionne explicitement en §7 malgre le schema
condense). Tout etat terminal (`TERMINAL_STATUSES`) n'a aucune
transition sortante."""
from __future__ import annotations

from omega_fuzz.domain.scans.scan_status import ScanStatus

_TERMINATIONS = frozenset(
    {
        ScanStatus.COMPLETED,
        ScanStatus.COMPLETED_TRUNCATED,
        ScanStatus.STOPPED,
        ScanStatus.ABORTED,
        ScanStatus.FAILED,
    }
)

_TRANSITIONS: dict[ScanStatus, frozenset[ScanStatus]] = {
    ScanStatus.PLANNED: frozenset({ScanStatus.RUNNING, ScanStatus.ABORTED}),
    ScanStatus.RUNNING: frozenset({ScanStatus.PAUSED}) | _TERMINATIONS,
    ScanStatus.PAUSED: frozenset({ScanStatus.RUNNING}) | _TERMINATIONS,
    ScanStatus.COMPLETED: frozenset(),
    ScanStatus.COMPLETED_TRUNCATED: frozenset(),
    ScanStatus.STOPPED: frozenset(),
    ScanStatus.ABORTED: frozenset(),
    ScanStatus.FAILED: frozenset(),
}


def is_valid_transition(current: ScanStatus, target: ScanStatus) -> bool:
    return target in _TRANSITIONS[current]
