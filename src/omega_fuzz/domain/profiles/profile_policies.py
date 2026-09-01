# Copyright (c) 2026 kraynux - Licence MIT
"""Combinaisons inhabituelles et regle de confirmation renforcee
(OMEGA-FUZZ_SPECIFICATIONS.md §16, §19.1). Une combinaison inhabituelle
declenche a la fois un avertissement (§19.1) ET une confirmation
renforcee obligatoire (§16 la liste explicitement comme condition,
"Combinaison inhabituelle, par exemple strict + violent")."""
from __future__ import annotations

from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName

UNUSUAL_COMBINATIONS: frozenset[tuple[ScopeProfileName, AggressivenessLevel]] = frozenset(
    {
        (ScopeProfileName.STRICT, AggressivenessLevel.VIOLENT),
        (ScopeProfileName.STRICT, AggressivenessLevel.AGRESSIF),
        (ScopeProfileName.LARGE, AggressivenessLevel.VIOLENT),
    }
)


def is_unusual_combination(
    *,
    scope_profile: ScopeProfileName,
    aggressiveness: AggressivenessLevel,
    via_explicit_preset: bool,
) -> bool:
    """`large + violent` n'est pas inhabituel via le preset `lab-extreme`
    explicite (§19.1 : "hors preset explicite") — seulement en
    combinaison manuelle."""
    if (
        scope_profile is ScopeProfileName.LARGE
        and aggressiveness is AggressivenessLevel.VIOLENT
        and via_explicit_preset
    ):
        return False
    return (scope_profile, aggressiveness) in UNUSUAL_COMBINATIONS


def requires_confirmation(
    *,
    aggressiveness: AggressivenessLevel,
    preset: PresetName | None,
    unusual_combination: bool,
) -> bool:
    return (
        aggressiveness is AggressivenessLevel.VIOLENT
        or preset is PresetName.LAB_EXTREME
        or unusual_combination
    )
