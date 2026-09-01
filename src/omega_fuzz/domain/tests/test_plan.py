# Copyright (c) 2026 kraynux - Licence MIT
"""Ensemble de tests planifies pour un scan (OMEGA-FUZZ_ARBORESCENCE.md
§9). Conteneur immuable minimal — la planification reelle (choix des
tests, budgets) arrive avec `domain.services.test_planning_service`
(Phase 6)."""
from __future__ import annotations

from dataclasses import dataclass, field

from omega_fuzz.domain.tests.test import Test


@dataclass(frozen=True, slots=True)
class TestPlan:
    scan_id: str
    tests: tuple[Test, ...] = field(default_factory=tuple)
