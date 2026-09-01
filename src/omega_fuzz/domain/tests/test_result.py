# Copyright (c) 2026 kraynux - Licence MIT
"""Resultats initiaux d'un `Test` (OMEGA-FUZZ_ARBORESCENCE.md §9,
OMEGA-FUZZ_SPECIFICATIONS.md §10)."""
from __future__ import annotations

from enum import Enum


class TestResult(str, Enum):
    NO_FINDING = "no_finding"
    FINDING_SUSPECTED = "finding_suspected"
    FINDING_CONFIRMED = "finding_confirmed"
    INCONCLUSIVE = "inconclusive"
