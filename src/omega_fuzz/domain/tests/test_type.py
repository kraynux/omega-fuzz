# Copyright (c) 2026 kraynux - Licence MIT
"""Types de test (OMEGA-FUZZ_ARBORESCENCE.md §9)."""
from __future__ import annotations

from enum import Enum


class TestType(str, Enum):
    FUZZ = "fuzz"
    SIGNATURE = "signature"
    LOGIC = "logic"
    OTHER = "other"
