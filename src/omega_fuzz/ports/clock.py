# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'horloge testable (OMEGA-FUZZ_ARBORESCENCE.md §15.3).
L'implementation de production delegue a `omega_lib.shared.clock.utc_now`
(D-005) ; `domain`/`application` ne l'appellent jamais elles-memes, `now`
est toujours recu en parametre explicite."""
from __future__ import annotations

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...
