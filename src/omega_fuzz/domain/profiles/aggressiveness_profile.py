# Copyright (c) 2026 kraynux - Licence MIT
"""Tables des 4 profils d'agressivite (OMEGA-FUZZ_SPECIFICATIONS.md
§15.1-15.4, valeurs YAML reprises exactement). `max_evidence_storage_per_scan`
n'est redefini par aucun profil — reste au defaut de `Limits` (300 Mo)."""
from __future__ import annotations

from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.limits import Limits

AGGRESSIVENESS_PROFILES: dict[AggressivenessLevel, Limits] = {
    AggressivenessLevel.DOUX: Limits(
        max_duration_seconds=300,
        max_total_requests=1000,
        max_tests=500,
        max_requests_per_path=200,
        max_requests_per_param=50,
        max_paths_per_target=50,
        max_params_per_path=20,
        max_concurrent_requests=2,
        max_errors_before_pause=20,
        max_response_body_size=5_242_880,
    ),
    AggressivenessLevel.STANDARD: Limits(
        max_duration_seconds=1800,
        max_total_requests=20_000,
        max_tests=10_000,
        max_requests_per_path=2000,
        max_requests_per_param=500,
        max_paths_per_target=500,
        max_params_per_path=20,
        max_concurrent_requests=8,
        max_errors_before_pause=100,
        max_response_body_size=10_485_760,
    ),
    AggressivenessLevel.AGRESSIF: Limits(
        max_duration_seconds=3600,
        max_total_requests=100_000,
        max_tests=50_000,
        max_requests_per_path=10_000,
        max_requests_per_param=2000,
        max_paths_per_target=2000,
        max_params_per_path=20,
        max_concurrent_requests=16,
        max_errors_before_pause=500,
        max_response_body_size=20_971_520,
    ),
    AggressivenessLevel.VIOLENT: Limits(
        max_duration_seconds=7200,
        max_total_requests=500_000,
        max_tests=250_000,
        max_requests_per_path=50_000,
        max_requests_per_param=10_000,
        max_paths_per_target=5000,
        max_params_per_path=20,
        max_concurrent_requests=32,
        max_errors_before_pause=2000,
        max_response_body_size=52_428_800,
    ),
}
