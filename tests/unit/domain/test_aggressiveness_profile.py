# Copyright (c) 2026 kraynux - Licence MIT
"""Valeurs exactes de OMEGA-FUZZ_SPECIFICATIONS.md §15.1-15.4."""
from __future__ import annotations

from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.aggressiveness_profile import AGGRESSIVENESS_PROFILES


def test_doux_matches_spec() -> None:
    limits = AGGRESSIVENESS_PROFILES[AggressivenessLevel.DOUX]
    assert limits.max_duration_seconds == 300
    assert limits.max_total_requests == 1000
    assert limits.max_tests == 500
    assert limits.max_requests_per_path == 200
    assert limits.max_requests_per_param == 50
    assert limits.max_paths_per_target == 50
    assert limits.max_params_per_path == 20
    assert limits.max_concurrent_requests == 2
    assert limits.max_errors_before_pause == 20
    assert limits.max_response_body_size == 5_242_880


def test_standard_matches_spec() -> None:
    limits = AGGRESSIVENESS_PROFILES[AggressivenessLevel.STANDARD]
    assert limits.max_duration_seconds == 1800
    assert limits.max_total_requests == 20_000
    assert limits.max_tests == 10_000
    assert limits.max_concurrent_requests == 8
    assert limits.max_response_body_size == 10_485_760


def test_agressif_matches_spec() -> None:
    limits = AGGRESSIVENESS_PROFILES[AggressivenessLevel.AGRESSIF]
    assert limits.max_duration_seconds == 3600
    assert limits.max_total_requests == 100_000
    assert limits.max_tests == 50_000
    assert limits.max_concurrent_requests == 16
    assert limits.max_response_body_size == 20_971_520


def test_violent_matches_spec() -> None:
    limits = AGGRESSIVENESS_PROFILES[AggressivenessLevel.VIOLENT]
    assert limits.max_duration_seconds == 7200
    assert limits.max_total_requests == 500_000
    assert limits.max_tests == 250_000
    assert limits.max_concurrent_requests == 32
    assert limits.max_response_body_size == 52_428_800


def test_no_profile_redefines_evidence_storage() -> None:
    for limits in AGGRESSIVENESS_PROFILES.values():
        assert limits.max_evidence_storage_per_scan == 300 * 1024 * 1024
