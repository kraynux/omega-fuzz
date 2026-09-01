# Copyright (c) 2026 kraynux - Licence MIT
"""Prepare un scan avant toute emission HTTP active
(OMEGA-FUZZ_ARBORESCENCE.md §16.3, OMEGA-FUZZ_PLAN_DEV.md Phase 6) :
normalise la cible, resout preset/profils, construit un plan estimatif,
retourne la configuration effective. Aucune dependance a `HttpClient`
dans ce module — garantie structurelle qu'aucune requete HTTP ne peut
etre emise par ce chemin ("--dry-run n'emet aucune requete")."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any

from omega_fuzz.application.exceptions import IncompleteScanConfigurationError
from omega_fuzz.domain.auth.auth_context import AuthContext
from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.effective_configuration import EffectiveConfiguration
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName
from omega_fuzz.domain.reports.scan_plan import ScanPlan
from omega_fuzz.domain.services.profile_resolution_service import (
    resolve_manual,
    resolve_preset,
)
from omega_fuzz.domain.services.test_planning_service import estimate_scan_plan
from omega_fuzz.domain.services.url_normalization_service import normalize_url
from omega_fuzz.domain.targets.target_id import build_target_id
from omega_fuzz.domain.targets.url import NormalizedUrl

_TLS_VERIFICATION_DISABLED_WARNING = (
    "verification TLS desactivee (--insecure-tls) : traitee comme une action a "
    "risque au meme titre qu'un profil violent (OMEGA-FUZZ_SPECIFICATIONS.md §16)"
)


@dataclass(frozen=True, slots=True)
class PreparedScan:
    target_id: str
    entry_url: NormalizedUrl
    configuration: EffectiveConfiguration
    plan: ScanPlan
    verify_tls: bool = True


def prepare_scan(
    *,
    raw_target: str,
    auth_context: AuthContext,
    preset: PresetName | None = None,
    aggressiveness: AggressivenessLevel | None = None,
    scope_profile: ScopeProfileName | None = None,
    overrides: Mapping[str, Any] | None = None,
    verify_tls: bool = True,
) -> PreparedScan:
    entry_url = normalize_url(raw_target)

    if preset is not None:
        configuration = resolve_preset(preset, entry_url=entry_url, overrides=overrides)
    elif aggressiveness is not None and scope_profile is not None:
        configuration = resolve_manual(
            entry_url=entry_url,
            aggressiveness=aggressiveness,
            scope_profile=scope_profile,
            overrides=overrides,
        )
    else:
        raise IncompleteScanConfigurationError

    if not verify_tls:
        configuration = replace(
            configuration,
            requires_confirmation=True,
            warnings=(*configuration.warnings, _TLS_VERIFICATION_DISABLED_WARNING),
        )

    target_id = build_target_id(host=entry_url.host)
    plan = estimate_scan_plan(
        entry_url=entry_url, configuration=configuration, auth_context=auth_context
    )

    return PreparedScan(
        target_id=target_id,
        entry_url=entry_url,
        configuration=configuration,
        plan=plan,
        verify_tls=verify_tls,
    )
