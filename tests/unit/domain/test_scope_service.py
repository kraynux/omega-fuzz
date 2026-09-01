# Copyright (c) 2026 kraynux - Licence MIT
"""Tests indispensables de la Phase 1 (OMEGA-FUZZ_PLAN_DEV.md §5, Phase
1) — repris tels quels."""
from __future__ import annotations

from typing import Any

import pytest

from omega_fuzz.core.errors import ValidationError
from omega_fuzz.domain.services.scope_service import evaluate_scope
from omega_fuzz.domain.targets.exclusions import ExclusionReason
from omega_fuzz.domain.targets.scope import build_scope
from omega_fuzz.domain.targets.scope_decision import ACCEPTED_REASON
from omega_fuzz.domain.targets.scope_mode import ScopeMode


def _scope(**overrides: Any) -> Any:
    defaults: dict[str, Any] = {
        "root_host": "example.com",
        "mode": ScopeMode.EXACT,
        "allowed_schemes": frozenset({"https"}),
        "scope_port": 443,
    }
    defaults.update(overrides)
    return build_scope(**defaults)


def test_example_com_allows_example_com_in_exact_mode() -> None:
    scope = _scope(mode=ScopeMode.EXACT)
    decision = evaluate_scope(raw_url="https://example.com/", scope=scope, depth=0)
    assert decision.accepted
    assert decision.reason == ACCEPTED_REASON


def test_example_com_rejects_www_example_com_in_exact_mode() -> None:
    scope = _scope(mode=ScopeMode.EXACT)
    decision = evaluate_scope(raw_url="https://www.example.com/", scope=scope, depth=0)
    assert not decision.accepted
    assert decision.reason == ExclusionReason.SUBDOMAIN_NOT_ALLOWED.value


def test_example_com_accepts_www_example_com_in_subdomains_mode() -> None:
    scope = _scope(mode=ScopeMode.SUBDOMAINS)
    decision = evaluate_scope(raw_url="https://www.example.com/", scope=scope, depth=0)
    assert decision.accepted


def test_example_com_rejects_example_com_evil_tld() -> None:
    scope = _scope(mode=ScopeMode.SUBDOMAINS)
    decision = evaluate_scope(raw_url="https://example.com.evil.tld/", scope=scope, depth=0)
    assert not decision.accepted
    assert decision.reason == ExclusionReason.HOST_OUT_OF_SCOPE.value


def test_https_example_com_rejects_non_default_port_by_default() -> None:
    scope = _scope()
    decision = evaluate_scope(raw_url="https://example.com:8443/", scope=scope, depth=0)
    assert not decision.accepted
    assert decision.reason == ExclusionReason.PORT_OUT_OF_SCOPE.value


def test_blocked_path_is_rejected_even_when_host_is_valid() -> None:
    scope = _scope(blocked_paths=("/admin",))
    decision = evaluate_scope(raw_url="https://example.com/admin/panel", scope=scope, depth=0)
    assert not decision.accepted
    assert decision.reason == ExclusionReason.PATH_BLOCKED.value


def test_allowed_path_restricts_everything_else() -> None:
    scope = _scope(allowed_paths=("/api/",))
    accepted = evaluate_scope(raw_url="https://example.com/api/v1", scope=scope, depth=0)
    rejected = evaluate_scope(raw_url="https://example.com/other", scope=scope, depth=0)
    assert accepted.accepted
    assert not rejected.accepted
    assert rejected.reason == ExclusionReason.PATH_NOT_ALLOWED.value


def test_invalid_regex_prevents_launch() -> None:
    with pytest.raises(ValidationError):
        _scope(blocked_url_pattern_strings=("(unclosed",))


def test_url_beyond_max_depth_is_ignored_with_reason() -> None:
    scope = _scope(max_depth=2)
    decision = evaluate_scope(raw_url="https://example.com/deep", scope=scope, depth=3)
    assert not decision.accepted
    assert decision.reason == ExclusionReason.MAX_DEPTH_EXCEEDED.value


def test_external_redirect_is_always_refused() -> None:
    scope = _scope()
    decision = evaluate_scope(
        raw_url="https://evil.tld/", scope=scope, depth=0, is_redirect=True
    )
    assert not decision.accepted
    assert decision.reason == ExclusionReason.EXTERNAL_REDIRECT.value


def test_unsupported_scheme_is_rejected() -> None:
    scope = _scope(allowed_schemes=frozenset({"https"}))
    decision = evaluate_scope(raw_url="ftp://example.com/", scope=scope, depth=0)
    assert not decision.accepted
    assert decision.reason == ExclusionReason.UNSUPPORTED_SCHEME.value


def test_invalid_url_is_rejected() -> None:
    scope = _scope()
    decision = evaluate_scope(raw_url="not a url", scope=scope, depth=0)
    assert not decision.accepted
    assert decision.reason == ExclusionReason.INVALID_URL.value


def test_iso_extension_is_always_blocked_regardless_of_profile() -> None:
    scope = _scope()  # aucun blocked_url_patterns configure
    decision = evaluate_scope(
        raw_url="https://example.com/downloads/ubuntu.iso", scope=scope, depth=0
    )
    assert not decision.accepted
    assert decision.reason == ExclusionReason.PATTERN_BLOCKED.value


def test_binary_extension_blocked_even_within_allowed_paths() -> None:
    scope = _scope(allowed_paths=("/downloads/",))
    decision = evaluate_scope(
        raw_url="https://example.com/downloads/archive.zip", scope=scope, depth=0
    )
    assert not decision.accepted
    assert decision.reason == ExclusionReason.PATTERN_BLOCKED.value


def test_html_path_resembling_an_extension_is_not_blocked() -> None:
    scope = _scope()
    decision = evaluate_scope(raw_url="https://example.com/isolation/page", scope=scope, depth=0)
    assert decision.accepted
