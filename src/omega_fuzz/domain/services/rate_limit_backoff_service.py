# Copyright (c) 2026 kraynux - Licence MIT
"""Backoff adaptatif WAF/rate-limit (OMEGA-FUZZ_SPECIFICATIONS.md
§32.2/§32.4, decision N de la passe de coherence) : signal primaire code
`429` ou header `Retry-After` (priorite a la valeur du header si
present, sinon backoff exponentiel base 2s / plafond 60s) ; signal
secondaire heuristique de latence (fenetre glissante des N=20 dernieres
requetes, mediane > 3x la latence de reference). Fonction pure : le
delai retourne doit etre reellement attendu par l'appelant
(`await asyncio.sleep(...)`), jamais par ce module lui-meme — testable
sans ralentir la suite de tests.

Place en `domain.services` plutot que `infrastructure.network` (contrairement
a la premiere intention du plan Phase 4) : logique purement domaine (aucune
dependance a `httpx`), doit rester appelable depuis `application` sans
violer la Dependency Rule (`application` ne peut pas importer
`infrastructure`) — meme raisonnement que
`domain.services.scope_service.decide_redirect`."""
from __future__ import annotations

from collections.abc import Sequence

BASE_BACKOFF_DELAY_SECONDS = 2.0
MAX_BACKOFF_DELAY_SECONDS = 60.0
LATENCY_WINDOW_SIZE = 20
LATENCY_THRESHOLD_MULTIPLIER = 3.0


def _exponential_backoff(*, consecutive_backoff_triggers: int) -> float:
    delay = BASE_BACKOFF_DELAY_SECONDS * float(2**consecutive_backoff_triggers)
    return min(delay, MAX_BACKOFF_DELAY_SECONDS)


def compute_backoff_delay(
    *,
    status_code: int,
    retry_after_header: str | None,
    consecutive_backoff_triggers: int,
    recent_latencies: Sequence[float] = (),
    baseline_latency: float = 0.0,
) -> float | None:
    """Retourne le delai (secondes) a attendre avant la prochaine
    requete, ou `None` si aucun signal de ralentissement n'est detecte."""
    if status_code == 429 or retry_after_header is not None:
        if retry_after_header is not None:
            try:
                return float(retry_after_header)
            except ValueError:
                pass
        return _exponential_backoff(consecutive_backoff_triggers=consecutive_backoff_triggers)

    if baseline_latency > 0 and len(recent_latencies) >= LATENCY_WINDOW_SIZE:
        window = sorted(recent_latencies[-LATENCY_WINDOW_SIZE:])
        median_latency = window[len(window) // 2]
        if median_latency > baseline_latency * LATENCY_THRESHOLD_MULTIPLIER:
            return _exponential_backoff(consecutive_backoff_triggers=consecutive_backoff_triggers)

    return None
