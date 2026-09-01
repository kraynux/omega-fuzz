# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.profiles.profile_policies import (
    is_unusual_combination,
    requires_confirmation,
)
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName


def test_strict_violent_is_unusual() -> None:
    assert is_unusual_combination(
        scope_profile=ScopeProfileName.STRICT,
        aggressiveness=AggressivenessLevel.VIOLENT,
        via_explicit_preset=False,
    )


def test_strict_agressif_is_unusual() -> None:
    assert is_unusual_combination(
        scope_profile=ScopeProfileName.STRICT,
        aggressiveness=AggressivenessLevel.AGRESSIF,
        via_explicit_preset=False,
    )


def test_large_violent_is_unusual_only_without_explicit_preset() -> None:
    assert is_unusual_combination(
        scope_profile=ScopeProfileName.LARGE,
        aggressiveness=AggressivenessLevel.VIOLENT,
        via_explicit_preset=False,
    )
    assert not is_unusual_combination(
        scope_profile=ScopeProfileName.LARGE,
        aggressiveness=AggressivenessLevel.VIOLENT,
        via_explicit_preset=True,
    )


def test_standard_standard_is_not_unusual() -> None:
    assert not is_unusual_combination(
        scope_profile=ScopeProfileName.STANDARD,
        aggressiveness=AggressivenessLevel.STANDARD,
        via_explicit_preset=False,
    )


def test_violent_always_requires_confirmation() -> None:
    assert requires_confirmation(
        aggressiveness=AggressivenessLevel.VIOLENT, preset=None, unusual_combination=False
    )


def test_lab_extreme_preset_requires_confirmation_even_if_not_flagged_unusual() -> None:
    assert requires_confirmation(
        aggressiveness=AggressivenessLevel.AGRESSIF,
        preset=PresetName.LAB_EXTREME,
        unusual_combination=False,
    )


def test_unusual_combination_requires_confirmation() -> None:
    assert requires_confirmation(
        aggressiveness=AggressivenessLevel.AGRESSIF, preset=None, unusual_combination=True
    )


def test_ordinary_combination_does_not_require_confirmation() -> None:
    assert not requires_confirmation(
        aggressiveness=AggressivenessLevel.STANDARD, preset=None, unusual_combination=False
    )
