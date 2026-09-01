# Copyright (c) 2026 kraynux - Licence MIT
"""Resolution preset/scope profile/agressivite -> configuration
effective (OMEGA-FUZZ_ARBORESCENCE.md §14, OMEGA-FUZZ_PLAN_DEV.md
Phase 5). `overrides` ne cible que les champs de `Limits` (les hard caps
mentionnes en critere d'acceptation) — `max_depth` reste fixe au preset/
profil de scope dans cette tranche, pas encore surchargeable
individuellement (pas necessaire aux criteres d'acceptation Phase 5).

Deviation par rapport a la signature envisagee dans le plan : les
fonctions prennent `entry_url: NormalizedUrl` (pas un simple
`root_host: str`) — `Scope.scope_port` doit venir du port reel de la
cible, que les profils de scope eux-memes ne connaissent pas (absent de
leurs tables §17.1-17.5, qui ne definissent ni host ni port)."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.aggressiveness_profile import AGGRESSIVENESS_PROFILES
from omega_fuzz.domain.profiles.effective_configuration import EffectiveConfiguration
from omega_fuzz.domain.profiles.preset import PRESETS, PresetName
from omega_fuzz.domain.profiles.profile_policies import (
    is_unusual_combination,
)
from omega_fuzz.domain.profiles.profile_policies import (
    requires_confirmation as compute_requires_confirmation,
)
from omega_fuzz.domain.profiles.profile_validation import apply_overrides
from omega_fuzz.domain.profiles.scope_profile import SCOPE_PROFILES, ScopeProfileName
from omega_fuzz.domain.targets.scope import Scope, build_scope
from omega_fuzz.domain.targets.url import NormalizedUrl


def _build_scope(
    *, entry_url: NormalizedUrl, scope_profile: ScopeProfileName, max_depth: int
) -> Scope:
    definition = SCOPE_PROFILES[scope_profile]
    return build_scope(
        root_host=entry_url.host,
        mode=definition.scope_mode,
        allowed_schemes=definition.allowed_schemes,
        scope_port=entry_url.port,
        allowed_subdomains=frozenset(definition.allowed_subdomains),
        blocked_subdomains=frozenset(definition.blocked_subdomains),
        allowed_paths=definition.allowed_paths,
        blocked_paths=definition.blocked_paths,
        blocked_url_pattern_strings=definition.blocked_url_patterns,
        max_depth=max_depth,
    )


def _unusual_warning(*, scope_profile: ScopeProfileName, aggressiveness: AggressivenessLevel) -> tuple[str, ...]:
    return (f"combinaison inhabituelle : {scope_profile.value} + {aggressiveness.value}",)


def resolve_preset(
    name: PresetName,
    *,
    entry_url: NormalizedUrl,
    overrides: Mapping[str, Any] | None = None,
) -> EffectiveConfiguration:
    """Un preset est resolu en configuration effective
    (OMEGA-FUZZ_PLAN_DEV.md Phase 5, critere d'acceptation explicite)."""
    overrides = overrides or {}
    definition = PRESETS[name]

    base_limits = AGGRESSIVENESS_PROFILES[definition.aggressiveness]
    preset_limits = replace(
        base_limits,
        max_duration_seconds=definition.max_duration_seconds,
        max_total_requests=definition.max_total_requests,
        max_tests=definition.max_tests,
        max_concurrent_requests=definition.max_concurrent_requests,
    )
    effective_limits = apply_overrides(preset_limits, overrides) if overrides else preset_limits

    scope = _build_scope(
        entry_url=entry_url, scope_profile=definition.scope_profile, max_depth=definition.max_depth
    )

    unusual = is_unusual_combination(
        scope_profile=definition.scope_profile,
        aggressiveness=definition.aggressiveness,
        via_explicit_preset=True,
    )

    return EffectiveConfiguration(
        aggressiveness=definition.aggressiveness,
        scope_profile=definition.scope_profile,
        limits=effective_limits,
        scope=scope,
        requires_confirmation=compute_requires_confirmation(
            aggressiveness=definition.aggressiveness, preset=name, unusual_combination=unusual
        ),
        preset=name,
        overrides=dict(overrides),
        warnings=_unusual_warning(
            scope_profile=definition.scope_profile, aggressiveness=definition.aggressiveness
        )
        if unusual
        else (),
    )


def resolve_manual(
    *,
    entry_url: NormalizedUrl,
    aggressiveness: AggressivenessLevel,
    scope_profile: ScopeProfileName,
    overrides: Mapping[str, Any] | None = None,
) -> EffectiveConfiguration:
    """Combinaison directe profil de scope + agressivite, sans preset."""
    overrides = overrides or {}
    base_limits = AGGRESSIVENESS_PROFILES[aggressiveness]
    effective_limits = apply_overrides(base_limits, overrides) if overrides else base_limits

    scope_definition = SCOPE_PROFILES[scope_profile]
    scope = _build_scope(
        entry_url=entry_url, scope_profile=scope_profile, max_depth=scope_definition.max_depth
    )

    unusual = is_unusual_combination(
        scope_profile=scope_profile, aggressiveness=aggressiveness, via_explicit_preset=False
    )

    return EffectiveConfiguration(
        aggressiveness=aggressiveness,
        scope_profile=scope_profile,
        limits=effective_limits,
        scope=scope,
        requires_confirmation=compute_requires_confirmation(
            aggressiveness=aggressiveness, preset=None, unusual_combination=unusual
        ),
        preset=None,
        overrides=dict(overrides),
        warnings=_unusual_warning(scope_profile=scope_profile, aggressiveness=aggressiveness)
        if unusual
        else (),
    )
