# Copyright (c) 2026 kraynux - Licence MIT
"""Tables des 5 presets « quick pick » (OMEGA-FUZZ_SPECIFICATIONS.md
§20.1-20.5, valeurs YAML reprises exactement). Un preset surcharge
toujours `max_duration_seconds`/`max_total_requests`/`max_tests`/
`max_depth`/`max_concurrent_requests` par rapport au profil
d'agressivite de base (verifie sur `api-hardened`, qui diverge
nettement des valeurs brutes du profil `agressif`) — les 6 autres
champs de `Limits` viennent toujours du profil de base."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName


class PresetName(str, Enum):
    PROD_SAFE = "prod-safe"
    STAGING_FULL = "staging-full"
    LAB_DEEP = "lab-deep"
    LAB_EXTREME = "lab-extreme"
    API_HARDENED = "api-hardened"


@dataclass(frozen=True, slots=True)
class PresetDefinition:
    scope_profile: ScopeProfileName
    aggressiveness: AggressivenessLevel
    max_duration_seconds: int
    max_total_requests: int
    max_tests: int
    max_depth: int
    max_concurrent_requests: int
    requires_confirmation: bool = False


PRESETS: dict[PresetName, PresetDefinition] = {
    PresetName.PROD_SAFE: PresetDefinition(
        scope_profile=ScopeProfileName.STRICT,
        aggressiveness=AggressivenessLevel.DOUX,
        max_duration_seconds=300,
        max_total_requests=1000,
        max_tests=500,
        max_depth=1,
        max_concurrent_requests=2,
    ),
    PresetName.STAGING_FULL: PresetDefinition(
        scope_profile=ScopeProfileName.STANDARD,
        aggressiveness=AggressivenessLevel.STANDARD,
        max_duration_seconds=1800,
        max_total_requests=20_000,
        max_tests=10_000,
        max_depth=2,
        max_concurrent_requests=8,
    ),
    PresetName.LAB_DEEP: PresetDefinition(
        scope_profile=ScopeProfileName.LARGE,
        aggressiveness=AggressivenessLevel.AGRESSIF,
        max_duration_seconds=3600,
        max_total_requests=100_000,
        max_tests=50_000,
        max_depth=4,
        max_concurrent_requests=16,
    ),
    PresetName.LAB_EXTREME: PresetDefinition(
        scope_profile=ScopeProfileName.LARGE,
        aggressiveness=AggressivenessLevel.VIOLENT,
        max_duration_seconds=7200,
        max_total_requests=500_000,
        max_tests=250_000,
        max_depth=5,
        max_concurrent_requests=32,
        requires_confirmation=True,
    ),
    PresetName.API_HARDENED: PresetDefinition(
        scope_profile=ScopeProfileName.API,
        aggressiveness=AggressivenessLevel.AGRESSIF,
        max_duration_seconds=1800,
        max_total_requests=50_000,
        max_tests=25_000,
        max_depth=3,
        max_concurrent_requests=12,
    ),
}
