# Copyright (c) 2026 kraynux - Licence MIT
"""Niveaux de severite (OMEGA-FUZZ_SPECIFICATIONS.md §29)."""
from __future__ import annotations

from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
