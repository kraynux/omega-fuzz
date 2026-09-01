# Copyright (c) 2026 kraynux - Licence MIT
"""Preuve reelle (threads, pas de simulation) qu'aucun depassement de
`max_total_requests` n'est possible avec plusieurs workers concurrents
(OMEGA-FUZZ_PLAN_DEV.md Phase 3, tests indispensables)."""
from __future__ import annotations

import threading

from omega_fuzz.application.services.limit_orchestrator import LimitOrchestrator


def test_sequential_reservation_exhausts_budget() -> None:
    orchestrator = LimitOrchestrator(max_total_requests=3)

    assert orchestrator.try_reserve()
    assert orchestrator.try_reserve()
    assert orchestrator.try_reserve()
    assert not orchestrator.try_reserve()
    assert orchestrator.reserved_count == 3


def test_a_real_retry_consumes_an_additional_reservation() -> None:
    orchestrator = LimitOrchestrator(max_total_requests=2)

    assert orchestrator.try_reserve()  # requete originale
    assert orchestrator.try_reserve()  # retry reellement envoye
    assert not orchestrator.try_reserve()
    assert orchestrator.reserved_count == 2


def test_concurrent_workers_never_exceed_the_total_budget() -> None:
    max_total_requests = 100
    worker_count = 32
    attempts_per_worker = 10  # 320 tentatives au total pour un budget de 100
    orchestrator = LimitOrchestrator(max_total_requests=max_total_requests)
    granted = 0
    granted_lock = threading.Lock()

    def worker() -> None:
        nonlocal granted
        for _ in range(attempts_per_worker):
            if orchestrator.try_reserve():
                with granted_lock:
                    granted += 1

    threads = [threading.Thread(target=worker) for _ in range(worker_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert granted == max_total_requests
    assert orchestrator.reserved_count == max_total_requests
