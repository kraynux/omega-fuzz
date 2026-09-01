# Copyright (c) 2026 kraynux - Licence MIT
"""Limites d'execution (OMEGA-FUZZ_SPECIFICATIONS.md §14.2). Les limites
sont cumulatives : le scan s'arrete des qu'une limite bloquante est
atteinte (§14.1). `max_response_body_size`/`max_evidence_storage_per_scan`
ne provoquent jamais l'arret du scan, seulement une troncature de preuve
(§14.3bis) — traite par le module de preuves (Phase 8), pas par
`limit_service`."""
from __future__ import annotations

from dataclasses import dataclass

_TEN_MEGABYTES = 10 * 1024 * 1024
_THREE_HUNDRED_MEGABYTES = 300 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class Limits:
    max_duration_seconds: int
    max_total_requests: int
    max_tests: int
    max_concurrent_requests: int
    max_requests_per_path: int
    max_requests_per_param: int
    max_paths_per_target: int
    max_params_per_path: int
    max_errors_before_pause: int
    max_response_body_size: int = _TEN_MEGABYTES
    max_evidence_storage_per_scan: int = _THREE_HUNDRED_MEGABYTES
