# Copyright (c) 2026 kraynux - Licence MIT
"""Etat d'authentification a injecter dans une requete
(OMEGA-FUZZ_ARBORESCENCE.md §45) — fourni/rafraichi par
`ports.session_provider.SessionProvider`."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Session:
    cookies: Mapping[str, str] = field(default_factory=dict)
    headers: Mapping[str, str] = field(default_factory=dict)
