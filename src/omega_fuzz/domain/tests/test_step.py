# Copyright (c) 2026 kraynux - Licence MIT
"""Une etape d'un test multi-etapes (OMEGA-FUZZ_SPECIFICATIONS.md §9.4 —
ex. recuperer un token CSRF, poster le payload, verifier la reflexion).
`request_id` est `None` tant que l'etape n'a pas encore ete executee."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TestStep:
    step_index: int
    purpose: str
    request_id: str | None = None
