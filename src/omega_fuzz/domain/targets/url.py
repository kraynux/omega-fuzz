# Copyright (c) 2026 kraynux - Licence MIT
"""URL normalisee : schema, host, port, path et fragment strippe
(OMEGA-FUZZ_ARBORESCENCE.md §8, PLAN_DEV Phase 1). Le fragment n'a pas de
signification cote serveur, il est supprime a la normalisation — jamais
conserve dans `NormalizedUrl`."""
from __future__ import annotations

from dataclasses import dataclass

from omega_fuzz.domain.targets.exclusions import ExclusionReason
from omega_fuzz.domain.targets.scheme import DEFAULT_PORTS


class UrlNormalizationError(ValueError):
    """Porte un `ExclusionReason` structure plutot qu'un message libre —
    consomme directement par `domain.services.scope_service` pour
    construire une `ScopeDecision` de rejet."""

    def __init__(self, reason: ExclusionReason, message: str = "") -> None:
        super().__init__(message or reason.value)
        self.reason = reason


@dataclass(frozen=True, slots=True)
class NormalizedUrl:
    scheme: str
    host: str
    port: int
    path: str
    query: str

    def to_str(self) -> str:
        netloc = self.host
        if DEFAULT_PORTS.get(self.scheme) != self.port:
            netloc = f"{self.host}:{self.port}"
        result = f"{self.scheme}://{netloc}{self.path}"
        if self.query:
            result = f"{result}?{self.query}"
        return result
