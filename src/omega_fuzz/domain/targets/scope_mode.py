# Copyright (c) 2026 kraynux - Licence MIT
"""Modes de scope (OMEGA-FUZZ_ARBORESCENCE.md §8, PLAN_DEV Phase 1)."""
from __future__ import annotations

from enum import Enum


class ScopeMode(str, Enum):
    EXACT = "exact"
    SUBDOMAINS = "subdomains"
