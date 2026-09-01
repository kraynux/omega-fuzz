# Copyright (c) 2026 kraynux - Licence MIT
"""Plan estimatif pre-vol (OMEGA-FUZZ_PLAN_DEV.md Phase 6 — « Modele
TestPlan », ce que le dry-run affiche). Distinct de
`domain.tests.test_plan.TestPlan` (Phase 2 : conteneur immuable de
`Test` CONCRETS deja planifies pour un scan) — `ScanPlan` est une
ESTIMATION avant toute emission HTTP, jamais une liste reelle
d'endpoints/tests (le dry-run n'effectue justement aucune decouverte).
`endpoints`/`methods`/`parameters` restent vides tant qu'aucune
decouverte reelle n'a eu lieu."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScanPlan:
    target_url: str
    active_modules: Mapping[str, bool]
    estimated_tests: int
    estimated_requests: int
    estimated_depth: int
    endpoints: tuple[str, ...] = ()
    methods: tuple[str, ...] = ()
    parameters: tuple[str, ...] = ()
