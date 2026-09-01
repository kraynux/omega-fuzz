# Copyright (c) 2026 kraynux - Licence MIT
"""Mutations structurelles generiques (OMEGA-FUZZ_PLAN_DEV.md Phase 7a
: « moteur de fuzzing sans detection »). Pas des payloads de
vulnerabilite (XSS/SQLi/...) — ceux-la vivent dans les catalogues YAML
de `infrastructure/payloads/catalogs/` (Phase 7b, OMEGA-FUZZ_ARBORESCENCE.md
§21). Ces valeurs servent uniquement a exercer mecaniquement le moteur
de mutation (limites de type, encodage, longueur) sans chercher a
detecter quoi que ce soit."""
from __future__ import annotations

GENERIC_MUTATIONS: tuple[str, ...] = (
    "",
    "0",
    "-1",
    "true",
    "null",
    "a" * 5000,
    "%00",
    "..%2f..%2f",
    "9" * 20,
    "é™€",
)
