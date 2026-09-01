# Copyright (c) 2026 kraynux - Licence MIT
"""Cible initiale d'un scan (OMEGA-FUZZ_ARBORESCENCE.md §8, PLAN_DEV
Phase 1) : URL d'entree normalisee associee a son perimetre."""
from __future__ import annotations

from dataclasses import dataclass

from omega_fuzz.domain.targets.scope import Scope
from omega_fuzz.domain.targets.target_id import TargetId
from omega_fuzz.domain.targets.url import NormalizedUrl


@dataclass(frozen=True, slots=True)
class Target:
    target_id: TargetId
    entry_url: NormalizedUrl
    scope: Scope
