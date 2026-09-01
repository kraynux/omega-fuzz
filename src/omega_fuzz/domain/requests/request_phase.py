# Copyright (c) 2026 kraynux - Licence MIT
"""Distinction obligatoire decouverte/test (OMEGA-FUZZ_SPECIFICATIONS.md
§8, §11)."""
from __future__ import annotations

from enum import Enum


class RequestPhase(str, Enum):
    DISCOVERY = "discovery"
    TEST = "test"
