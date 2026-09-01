# Copyright (c) 2026 kraynux - Licence MIT
"""Hard caps absolus (OMEGA-FUZZ_PLAN_DEV.md Phase 3), appliques quel que
soit le profil. `HARD_MAX_DEPTH` est deja defini en Phase 1
(`domain.targets.depth`) — reexporte ici pour que tous les hard caps
soient consultables depuis un seul endroit, sans le redefinir."""
from __future__ import annotations

from omega_fuzz.domain.targets.depth import HARD_MAX_DEPTH

HARD_MAX_DURATION_SECONDS = 7200
HARD_MAX_TOTAL_REQUESTS = 1_000_000
HARD_MAX_CONCURRENT_REQUESTS = 64
HARD_MAX_PATHS_PER_TARGET = 10_000
HARD_MAX_PARAMS_PER_PATH = 30
HARD_MAX_RESPONSE_BODY_SIZE = 52_428_800
HARD_MAX_EVIDENCE_STORAGE_PER_SCAN = 1_073_741_824

__all__ = [
    "HARD_MAX_CONCURRENT_REQUESTS",
    "HARD_MAX_DEPTH",
    "HARD_MAX_DURATION_SECONDS",
    "HARD_MAX_EVIDENCE_STORAGE_PER_SCAN",
    "HARD_MAX_PARAMS_PER_PATH",
    "HARD_MAX_PATHS_PER_TARGET",
    "HARD_MAX_RESPONSE_BODY_SIZE",
    "HARD_MAX_TOTAL_REQUESTS",
]
