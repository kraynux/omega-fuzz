# Copyright (c) 2026 kraynux - Licence MIT
"""Resolution du port effectif : port explicite ou port par defaut du
schema (OMEGA-FUZZ_ARBORESCENCE.md §8, PLAN_DEV Phase 1)."""
from __future__ import annotations

from omega_fuzz.domain.targets.scheme import DEFAULT_PORTS


def normalize_port(*, scheme: str, explicit_port: int | None) -> int:
    if explicit_port is not None:
        return explicit_port
    return DEFAULT_PORTS[scheme]
