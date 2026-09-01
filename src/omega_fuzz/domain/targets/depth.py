# Copyright (c) 2026 kraynux - Licence MIT
"""Profondeur de crawl : 0 (page de depart seule) a HARD_MAX_DEPTH
(OMEGA-FUZZ_ARBORESCENCE.md §8, OMEGA-FUZZ_SPECIFICATIONS.md §2,
decision A de la passe de coherence — 0..5 unifie partout)."""
from __future__ import annotations

HARD_MAX_DEPTH = 5


def validate_depth(depth: int) -> int:
    if not 0 <= depth <= HARD_MAX_DEPTH:
        raise ValueError(f"depth must be between 0 and {HARD_MAX_DEPTH}, got {depth}")
    return depth
