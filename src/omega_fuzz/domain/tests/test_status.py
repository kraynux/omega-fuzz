# Copyright (c) 2026 kraynux - Licence MIT
"""Etats d'un `Test` (OMEGA-FUZZ_ARBORESCENCE.md §9,
OMEGA-FUZZ_SPECIFICATIONS.md §10)."""
from __future__ import annotations

from enum import Enum


class TestStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    ABORTED = "aborted"
    INCONCLUSIVE = "inconclusive"
