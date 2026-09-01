# Copyright (c) 2026 kraynux - Licence MIT
"""Perimetre autorise pour une cible (OMEGA-FUZZ_ARBORESCENCE.md §8,
PLAN_DEV Phase 1). Le port fait partie du scope par defaut (decision
metier explicite du plan) : une URL sur un port different du port de
depart est hors scope sauf configuration contraire future."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from omega_fuzz.core.errors import ValidationError
from omega_fuzz.domain.targets.depth import HARD_MAX_DEPTH, validate_depth
from omega_fuzz.domain.targets.scope_mode import ScopeMode


@dataclass(frozen=True, slots=True)
class Scope:
    root_host: str
    mode: ScopeMode
    allowed_schemes: frozenset[str]
    scope_port: int
    allowed_subdomains: frozenset[str] = field(default_factory=frozenset)
    blocked_subdomains: frozenset[str] = field(default_factory=frozenset)
    allowed_paths: tuple[str, ...] = ()
    blocked_paths: tuple[str, ...] = ()
    blocked_url_patterns: tuple[re.Pattern[str], ...] = ()
    max_depth: int = HARD_MAX_DEPTH


def build_scope(
    *,
    root_host: str,
    mode: ScopeMode,
    allowed_schemes: frozenset[str],
    scope_port: int,
    allowed_subdomains: frozenset[str] = frozenset(),
    blocked_subdomains: frozenset[str] = frozenset(),
    allowed_paths: tuple[str, ...] = (),
    blocked_paths: tuple[str, ...] = (),
    blocked_url_pattern_strings: tuple[str, ...] = (),
    max_depth: int = HARD_MAX_DEPTH,
) -> Scope:
    """Point d'entree unique de construction d'un `Scope` : valide les
    regex de `blocked_url_pattern_strings` immediatement (une regex
    invalide doit empecher le lancement du scan, pas etre decouverte en
    cours de crawl) et la profondeur maximale."""
    compiled_patterns: list[re.Pattern[str]] = []
    for raw_pattern in blocked_url_pattern_strings:
        try:
            compiled_patterns.append(re.compile(raw_pattern))
        except re.error as exc:
            raise ValidationError(f"regex de scope invalide : {raw_pattern!r} ({exc})") from exc

    validate_depth(max_depth)

    return Scope(
        root_host=root_host.strip().lower(),
        mode=mode,
        allowed_schemes=allowed_schemes,
        scope_port=scope_port,
        allowed_subdomains=frozenset(s.lower() for s in allowed_subdomains),
        blocked_subdomains=frozenset(s.lower() for s in blocked_subdomains),
        allowed_paths=allowed_paths,
        blocked_paths=blocked_paths,
        blocked_url_patterns=tuple(compiled_patterns),
        max_depth=max_depth,
    )
