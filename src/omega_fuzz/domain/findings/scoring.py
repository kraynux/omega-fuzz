# Copyright (c) 2026 kraynux - Licence MIT
"""Score interne (OMEGA-FUZZ_SPECIFICATIONS.md §30) : 3 axes notes de 1
a 5 (impact, exploitabilite, portee), `raw_score = impact +
exploitability + scope` (3 a 15)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Scoring:
    impact: int
    exploitability: int
    scope: int
    raw_score: int
