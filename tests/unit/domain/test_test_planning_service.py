# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_fuzz.domain.auth.auth_context import AuthContext, AuthMode
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.services.profile_resolution_service import resolve_preset
from omega_fuzz.domain.services.test_planning_service import (
    determine_active_modules,
    estimate_scan_plan,
)
from omega_fuzz.domain.services.url_normalization_service import normalize_url

_ENTRY_URL = normalize_url("https://example.com/")


def test_logic_tests_disabled_without_authentication() -> None:
    modules = determine_active_modules(auth_context=AuthContext(mode=AuthMode.NONE))
    assert modules["logic_tests"] is False
    assert modules["discovery"] is True
    assert modules["http_fuzzing"] is True
    assert modules["signatures"] is True


def test_logic_tests_enabled_with_cookie_authentication() -> None:
    modules = determine_active_modules(
        auth_context=AuthContext(mode=AuthMode.COOKIE, cookie="abc")
    )
    assert modules["logic_tests"] is True


def test_estimate_never_exceeds_effective_limits() -> None:
    for preset_name in PresetName:
        configuration = resolve_preset(preset_name, entry_url=_ENTRY_URL)
        plan = estimate_scan_plan(
            entry_url=_ENTRY_URL,
            configuration=configuration,
            auth_context=AuthContext(mode=AuthMode.NONE),
        )
        assert plan.estimated_tests <= configuration.limits.max_tests
        assert plan.estimated_requests <= configuration.limits.max_total_requests
        assert plan.estimated_depth == configuration.scope.max_depth


def test_estimate_has_no_endpoints_before_real_discovery() -> None:
    configuration = resolve_preset(PresetName.PROD_SAFE, entry_url=_ENTRY_URL)
    plan = estimate_scan_plan(
        entry_url=_ENTRY_URL,
        configuration=configuration,
        auth_context=AuthContext(mode=AuthMode.NONE),
    )
    assert plan.endpoints == ()
    assert plan.methods == ()
    assert plan.parameters == ()
