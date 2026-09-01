# Copyright (c) 2026 kraynux - Licence MIT
"""Reservation de budget de requetes reellement thread-safe
(OMEGA-FUZZ_SPECIFICATIONS.md §14.4, OMEGA-FUZZ_ARBORESCENCE.md §16.2 —
`application/services/limit_orchestrator.py`). Complement operationnel
de la decision pure `domain.services.limit_service.can_reserve_request` :
ici, un vrai verrou empeche plusieurs workers concurrents de depasser
`max_total_requests`, ce qu'une fonction pure sans etat mutable partage
ne peut pas garantir a elle seule."""
from __future__ import annotations

import threading


class LimitOrchestrator:
    def __init__(self, *, max_total_requests: int) -> None:
        self._max_total_requests = max_total_requests
        self._lock = threading.Lock()
        self._reserved = 0

    def try_reserve(self) -> bool:
        """Reserve atomiquement une unite de budget. Un retry reellement
        envoye est une nouvelle requete : il doit appeler `try_reserve`
        a nouveau, comme n'importe quelle autre requete
        (OMEGA-FUZZ_SPECIFICATIONS.md §9.1)."""
        with self._lock:
            if self._reserved >= self._max_total_requests:
                return False
            self._reserved += 1
            return True

    @property
    def reserved_count(self) -> int:
        with self._lock:
            return self._reserved
