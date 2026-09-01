# Copyright (c) 2026 kraynux - Licence MIT
"""Statuts d'un finding (OMEGA-FUZZ_PLAN_DEV.md Phase 8)."""
from __future__ import annotations

from enum import Enum


class FindingStatus(str, Enum):
    SUSPECTED = "suspected"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    ACCEPTED_RISK = "accepted_risk"
