# Copyright (c) 2026 kraynux - Licence MIT
"""Valeurs exactes de OMEGA-FUZZ_SPECIFICATIONS.md §20.1-20.5."""
from __future__ import annotations

from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.preset import PRESETS, PresetName
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName


def test_prod_safe_matches_spec() -> None:
    preset = PRESETS[PresetName.PROD_SAFE]
    assert preset.scope_profile is ScopeProfileName.STRICT
    assert preset.aggressiveness is AggressivenessLevel.DOUX
    assert preset.max_duration_seconds == 300
    assert preset.max_total_requests == 1000
    assert preset.max_tests == 500
    assert preset.max_depth == 1
    assert preset.max_concurrent_requests == 2
    assert preset.requires_confirmation is False


def test_staging_full_matches_spec() -> None:
    preset = PRESETS[PresetName.STAGING_FULL]
    assert preset.scope_profile is ScopeProfileName.STANDARD
    assert preset.aggressiveness is AggressivenessLevel.STANDARD
    assert preset.max_total_requests == 20_000
    assert preset.max_depth == 2


def test_lab_deep_matches_spec() -> None:
    preset = PRESETS[PresetName.LAB_DEEP]
    assert preset.scope_profile is ScopeProfileName.LARGE
    assert preset.aggressiveness is AggressivenessLevel.AGRESSIF
    assert preset.max_total_requests == 100_000
    assert preset.max_depth == 4


def test_lab_extreme_matches_spec_and_requires_confirmation() -> None:
    preset = PRESETS[PresetName.LAB_EXTREME]
    assert preset.scope_profile is ScopeProfileName.LARGE
    assert preset.aggressiveness is AggressivenessLevel.VIOLENT
    assert preset.max_total_requests == 500_000
    assert preset.max_depth == 5
    assert preset.requires_confirmation is True


def test_api_hardened_matches_spec_and_diverges_from_raw_agressif() -> None:
    preset = PRESETS[PresetName.API_HARDENED]
    assert preset.scope_profile is ScopeProfileName.API
    assert preset.aggressiveness is AggressivenessLevel.AGRESSIF
    assert preset.max_duration_seconds == 1800
    assert preset.max_total_requests == 50_000
    assert preset.max_tests == 25_000
    assert preset.max_depth == 3
    assert preset.max_concurrent_requests == 12


def test_only_lab_extreme_requires_confirmation_by_default() -> None:
    for name, preset in PRESETS.items():
        expected = name is PresetName.LAB_EXTREME
        assert preset.requires_confirmation is expected
