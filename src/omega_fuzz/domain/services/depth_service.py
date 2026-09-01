# Copyright (c) 2026 kraynux - Licence MIT
"""Bookkeeping de profondeur (OMEGA-FUZZ_ARBORESCENCE.md §14, PLAN_DEV
Phase 1). Une URL hors profondeur est conservee comme information mais
jamais developpee ni testee : `should_expand` distingue "accepter en
scope" (fait par `scope_service`) de "developper ses liens sortants"."""
from __future__ import annotations


def next_depth(current_depth: int) -> int:
    return current_depth + 1


def should_expand(*, depth: int, max_depth: int) -> bool:
    return depth <= max_depth
