# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from dataclasses import dataclass, field

from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.infrastructure.analyzers.access_control_analyzer import HttpAccessControlAnalyzer


@dataclass(frozen=True, slots=True)
class _FakeResponse:
    status_code: int
    body: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)
    elapsed_seconds: float = 0.01
    final_url: str = "https://example.com/"
    truncated: bool = False
    fetch_error: str | None = None


def test_expected_denial_status_produces_no_observation() -> None:
    analyzer = HttpAccessControlAnalyzer()
    observation = analyzer.check(response=_FakeResponse(status_code=403), request_id="req_1")
    assert observation is None


def test_unexpected_success_status_is_verified_observation() -> None:
    analyzer = HttpAccessControlAnalyzer()
    observation = analyzer.check(response=_FakeResponse(status_code=200), request_id="req_1")
    assert observation is not None
    assert observation.kind == "unauthorized_access"
    assert observation.confidence is ConfidenceLevel.VERIFIED


def test_custom_expected_denial_codes() -> None:
    analyzer = HttpAccessControlAnalyzer()
    observation = analyzer.check(
        response=_FakeResponse(status_code=401),
        request_id="req_1",
        expected_denial_status_codes=(403,),
    )
    assert observation is not None  # 401 n'est pas dans la liste personnalisee


def test_fetch_error_produces_no_observation() -> None:
    analyzer = HttpAccessControlAnalyzer()
    observation = analyzer.check(
        response=_FakeResponse(status_code=0, fetch_error="Connection refused"),
        request_id="req_1",
    )
    assert observation is None
