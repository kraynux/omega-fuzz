# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from typing import Any

from omega_fuzz.domain.services.scope_service import decide_redirect
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


def test_relative_internal_redirect_is_followed() -> None:
    scope = _scope()
    decision = decide_redirect(
        current_url="https://example.com/old-page",
        location="/new-page",
        scope=scope,
        depth=0,
    )
    assert decision.accepted
    assert decision.reason == ACCEPTED_REASON
    assert decision.normalized_url == "https://example.com/new-page"


def test_absolute_external_redirect_is_ignored_with_external_redirect_reason() -> None:
    scope = _scope()
    decision = decide_redirect(
        current_url="https://example.com/old-page",
        location="https://evil.tld/phishing",
        scope=scope,
        depth=0,
    )
    assert not decision.accepted
    assert decision.reason == ExclusionReason.EXTERNAL_REDIRECT.value
