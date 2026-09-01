# Copyright (c) 2026 kraynux - Licence MIT
"""Schemas autorises (OMEGA-FUZZ_ARBORESCENCE.md §8, PLAN_DEV Phase 1)."""
from __future__ import annotations

from enum import Enum


class AllowedScheme(str, Enum):
    HTTP = "http"
    HTTPS = "https"


DEFAULT_PORTS: dict[str, int] = {
    AllowedScheme.HTTP.value: 80,
    AllowedScheme.HTTPS.value: 443,
}
