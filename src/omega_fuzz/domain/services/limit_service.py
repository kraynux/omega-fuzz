# Copyright (c) 2026 kraynux - Licence MIT
"""Validation des limites, decision de reservation pure et
determination de la raison de terminaison (OMEGA-FUZZ_ARBORESCENCE.md
§14, OMEGA-FUZZ_SPECIFICATIONS.md §14). `can_reserve_request` est une
decision pure (sans effet de bord) : la reservation reellement
thread-safe vit dans `application.services.limit_orchestrator`, qui
s'appuie sur cette meme regle mais sous verrou."""
from __future__ import annotations

from omega_fuzz.core.errors import ValidationError
from omega_fuzz.domain.profiles.hard_caps import (
    HARD_MAX_CONCURRENT_REQUESTS,
    HARD_MAX_DURATION_SECONDS,
    HARD_MAX_EVIDENCE_STORAGE_PER_SCAN,
    HARD_MAX_PARAMS_PER_PATH,
    HARD_MAX_PATHS_PER_TARGET,
    HARD_MAX_RESPONSE_BODY_SIZE,
    HARD_MAX_TOTAL_REQUESTS,
)
from omega_fuzz.domain.profiles.limits import Limits
from omega_fuzz.domain.reports.scan_statistics import ScanStatistics
from omega_fuzz.domain.reports.termination import TerminationReason, TerminationTrigger

_HARD_CAPS: dict[str, int] = {
    "max_duration_seconds": HARD_MAX_DURATION_SECONDS,
    "max_total_requests": HARD_MAX_TOTAL_REQUESTS,
    "max_concurrent_requests": HARD_MAX_CONCURRENT_REQUESTS,
    "max_paths_per_target": HARD_MAX_PATHS_PER_TARGET,
    "max_params_per_path": HARD_MAX_PARAMS_PER_PATH,
    "max_response_body_size": HARD_MAX_RESPONSE_BODY_SIZE,
    "max_evidence_storage_per_scan": HARD_MAX_EVIDENCE_STORAGE_PER_SCAN,
}


def validate_limits(limits: Limits) -> None:
    """Leve `ValidationError` si un champ ayant un hard cap le depasse.
    `max_tests`/`max_requests_per_path`/`max_requests_per_param`/
    `max_errors_before_pause` n'ont pas de hard cap documente
    (OMEGA-FUZZ_PLAN_DEV.md Phase 3) : non verifies ici."""
    for field_name, hard_cap in _HARD_CAPS.items():
        value = getattr(limits, field_name)
        if value > hard_cap:
            raise ValidationError(
                f"{field_name}={value} depasse le hard cap absolu ({hard_cap})"
            )


def can_reserve_request(*, stats: ScanStatistics, limits: Limits) -> bool:
    return stats.total_requests < limits.max_total_requests


def is_path_request_limit_reached(*, requests_for_path: int, limits: Limits) -> bool:
    return requests_for_path >= limits.max_requests_per_path


def is_param_request_limit_reached(*, requests_for_param: int, limits: Limits) -> bool:
    return requests_for_param >= limits.max_requests_per_param


def determine_termination(
    *, stats: ScanStatistics, limits: Limits, elapsed_seconds: float
) -> TerminationReason | None:
    """La premiere limite bloquante devient la raison officielle de fin
    de scan (OMEGA-FUZZ_SPECIFICATIONS.md §14.1) — verifiee dans l'ordre
    duree puis requetes puis tests. Retourne `None` si aucune limite
    n'est atteinte (le scan continue normalement)."""
    if elapsed_seconds >= limits.max_duration_seconds:
        return TerminationReason(
            trigger=TerminationTrigger.LIMIT_REACHED,
            limit_name="max_duration_seconds",
            configured_value=limits.max_duration_seconds,
            observed_value=int(elapsed_seconds),
        )
    if stats.total_requests >= limits.max_total_requests:
        return TerminationReason(
            trigger=TerminationTrigger.LIMIT_REACHED,
            limit_name="max_total_requests",
            configured_value=limits.max_total_requests,
            observed_value=stats.total_requests,
        )
    if stats.tests_executed >= limits.max_tests:
        return TerminationReason(
            trigger=TerminationTrigger.LIMIT_REACHED,
            limit_name="max_tests",
            configured_value=limits.max_tests,
            observed_value=stats.tests_executed,
        )
    return None
