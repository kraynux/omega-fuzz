# Copyright (c) 2026 kraynux - Licence MIT
"""Cible d'un finding (OMEGA-FUZZ_SPECIFICATIONS.md §28.1)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FindingTarget:
    url: str
    endpoint: str
    method: str
    parameter: str | None = None
