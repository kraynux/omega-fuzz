# Copyright (c) 2026 kraynux - Licence MIT
"""URL rencontree pendant la decouverte, avec sa decision de scope et son
etat (OMEGA-FUZZ_ARBORESCENCE.md §8). `state` empeche structurellement la
re-decouverte infinie d'une URL deja vue : une fois `ACCEPTED`/
`REJECTED`/`OUT_OF_DEPTH`, elle n'est plus jamais reevaluee ni remise en
file (voir aussi §7.2/§7.3 de OMEGA-FUZZ_SPECIFICATIONS.md — protection
contre les boucles de redirection)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from omega_fuzz.domain.targets.scope_decision import ScopeDecision


class DiscoveredUrlState(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    OUT_OF_DEPTH = "out_of_depth"


@dataclass(frozen=True, slots=True)
class DiscoveredUrl:
    url: str
    depth: int
    state: DiscoveredUrlState
    decision: ScopeDecision
