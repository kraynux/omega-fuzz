# Copyright (c) 2026 kraynux - Licence MIT
"""Valeurs exactes de OMEGA-FUZZ_SPECIFICATIONS.md §17.1-17.5."""
from __future__ import annotations

from omega_fuzz.domain.profiles.scope_profile import SCOPE_PROFILES, ScopeProfileName
from omega_fuzz.domain.targets.scope import build_scope
from omega_fuzz.domain.targets.scope_mode import ScopeMode


def test_strict_matches_spec() -> None:
    definition = SCOPE_PROFILES[ScopeProfileName.STRICT]
    assert definition.scope_mode is ScopeMode.EXACT
    assert definition.max_depth == 1
    assert definition.blocked_paths == (
        "/health",
        "/ready",
        "/metrics",
        "/favicon.ico",
        "/robots.txt",
    )
    assert definition.blocked_url_patterns == ()


def test_standard_matches_spec() -> None:
    definition = SCOPE_PROFILES[ScopeProfileName.STANDARD]
    assert definition.scope_mode is ScopeMode.SUBDOMAINS
    assert definition.max_depth == 2
    assert "cdn.example.com" in definition.blocked_subdomains
    assert len(definition.blocked_url_patterns) == 1


def test_large_matches_spec() -> None:
    definition = SCOPE_PROFILES[ScopeProfileName.LARGE]
    assert definition.max_depth == 4
    assert definition.blocked_subdomains == ()


def test_api_matches_spec() -> None:
    definition = SCOPE_PROFILES[ScopeProfileName.API]
    assert definition.scope_mode is ScopeMode.EXACT
    assert definition.max_depth == 3
    assert definition.allowed_paths == ("/api", "/v1", "/v2")


def test_custom_matches_spec() -> None:
    definition = SCOPE_PROFILES[ScopeProfileName.CUSTOM]
    assert definition.max_depth == 3
    assert definition.blocked_paths == ()
    assert definition.blocked_url_patterns == ()


def test_every_profiles_patterns_compile_via_build_scope() -> None:
    for name, definition in SCOPE_PROFILES.items():
        scope = build_scope(
            root_host="example.com",
            mode=definition.scope_mode,
            allowed_schemes=definition.allowed_schemes,
            scope_port=443,
            allowed_subdomains=frozenset(definition.allowed_subdomains),
            blocked_subdomains=frozenset(definition.blocked_subdomains),
            allowed_paths=definition.allowed_paths,
            blocked_paths=definition.blocked_paths,
            blocked_url_pattern_strings=definition.blocked_url_patterns,
            max_depth=definition.max_depth,
        )
        assert len(scope.blocked_url_patterns) == len(definition.blocked_url_patterns), name
