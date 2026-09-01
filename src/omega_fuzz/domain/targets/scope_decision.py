# Copyright (c) 2026 kraynux - Licence MIT
"""Decision de scope explicable (OMEGA-FUZZ_ARBORESCENCE.md §8) :
chaque URL evaluee produit une decision tracable, jamais un simple
booleen — `reason` vaut "accepted" pour une acceptation, ou la valeur
d'un `ExclusionReason` pour un rejet."""
from __future__ import annotations

from dataclasses import dataclass

ACCEPTED_REASON = "accepted"


@dataclass(frozen=True, slots=True)
class ScopeDecision:
    accepted: bool
    normalized_url: str | None
    reason: str
    rule: str
    depth: int | None
