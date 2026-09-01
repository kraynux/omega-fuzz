# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/clock.py::Clock, delegue a omega_lib.shared.clock
(D-005)."""
from __future__ import annotations

from datetime import datetime

from omega_lib.shared.clock import utc_now


class SystemClock:
    def now(self) -> datetime:
        return utc_now()
