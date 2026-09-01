# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : detecter le terminal et resoudre son profil de rendu.
Porte depuis omega-check (D-007/D-008)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_lib.terminal.service import resolve_render_profile

if TYPE_CHECKING:
    from omega_lib.terminal.models import TerminalProfile

    from omega_fuzz.ports.terminal_detector import TerminalDetector


def detect_terminal(*, terminal_detector: TerminalDetector) -> TerminalProfile:
    signals = terminal_detector.detect()
    return resolve_render_profile(signals)
