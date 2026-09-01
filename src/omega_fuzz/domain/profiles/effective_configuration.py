# Copyright (c) 2026 kraynux - Licence MIT
"""Configuration effective resolue (sortie de
`domain.services.profile_resolution_service`) — pas nomme explicitement
dans OMEGA-FUZZ_ARBORESCENCE.md mais necessaire comme sortie de
`ProfileResolutionService` (OMEGA-FUZZ_PLAN_DEV.md Phase 5 : « le
rapport conserve preset, profils et surcharges »). `overrides` ne
retient que les champs reellement fournis par l'utilisateur — consomme
par le dry-run (Phase 6), pas affiche ici."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.limits import Limits
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName
from omega_fuzz.domain.targets.scope import Scope


@dataclass(frozen=True, slots=True)
class EffectiveConfiguration:
    aggressiveness: AggressivenessLevel
    scope_profile: ScopeProfileName
    limits: Limits
    scope: Scope
    requires_confirmation: bool
    preset: PresetName | None = None
    overrides: Mapping[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
