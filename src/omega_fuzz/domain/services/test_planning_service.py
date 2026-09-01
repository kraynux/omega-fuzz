# Copyright (c) 2026 kraynux - Licence MIT
"""Construction du plan estimatif pre-vol (OMEGA-FUZZ_ARBORESCENCE.md
§14, OMEGA-FUZZ_PLAN_DEV.md Phase 6). L'estimation est une heuristique
assumee (aucune decouverte HTTP reelle n'a lieu avant/pendant un
dry-run) — plafonnee par les limites effectives, qui restent de toute
facon le vrai garde-fou. A affiner en Phase 7 quand le volume reel de
payloads/signatures existera."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_fuzz.domain.auth.auth_context import AuthMode
from omega_fuzz.domain.reports.scan_plan import ScanPlan

if TYPE_CHECKING:
    from omega_fuzz.domain.auth.auth_context import AuthContext
    from omega_fuzz.domain.profiles.effective_configuration import EffectiveConfiguration
    from omega_fuzz.domain.targets.url import NormalizedUrl

# Facteurs heuristiques (Phase 6, a affiner en Phase 7) :
_BRANCHING_FACTOR = 5  # liens sortants moyens par page
_TESTS_PER_ENDPOINT_PER_MODULE = 10
_AVG_REQUESTS_PER_TEST = 3


def determine_active_modules(*, auth_context: AuthContext) -> dict[str, bool]:
    """`logic_tests` (IDOR/logique metier) necessite une authentification
    (OMEGA-FUZZ_PLAN_DEV.md Phase 4/7c) — desactive tant qu'aucune
    authentification n'est configuree."""
    return {
        "discovery": True,
        "http_fuzzing": True,
        "signatures": True,
        "logic_tests": auth_context.mode is not AuthMode.NONE,
    }


def estimate_scan_plan(
    *,
    entry_url: NormalizedUrl,
    configuration: EffectiveConfiguration,
    auth_context: AuthContext,
) -> ScanPlan:
    active_modules = determine_active_modules(auth_context=auth_context)
    test_generating_modules = sum(
        1 for module in ("http_fuzzing", "signatures", "logic_tests") if active_modules[module]
    )

    estimated_pages = _BRANCHING_FACTOR**configuration.scope.max_depth
    estimated_tests = min(
        estimated_pages * _TESTS_PER_ENDPOINT_PER_MODULE * test_generating_modules,
        configuration.limits.max_tests,
    )
    estimated_requests = min(
        estimated_tests * _AVG_REQUESTS_PER_TEST, configuration.limits.max_total_requests
    )

    return ScanPlan(
        target_url=entry_url.to_str(),
        active_modules=active_modules,
        estimated_tests=estimated_tests,
        estimated_requests=estimated_requests,
        estimated_depth=configuration.scope.max_depth,
    )
