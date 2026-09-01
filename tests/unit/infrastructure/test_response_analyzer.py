# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from dataclasses import dataclass, field

from omega_fuzz.domain.findings.payload_catalog import RequiredHeader, SecurityHeadersCatalog
from omega_fuzz.infrastructure.analyzers.response_analyzer import CompositeResponseAnalyzer


@dataclass(frozen=True, slots=True)
class _FakeResponse:
    status_code: int
    body: bytes
    headers: dict[str, str] = field(default_factory=dict)
    elapsed_seconds: float = 0.01
    final_url: str = "https://example.com/"
    truncated: bool = False
    fetch_error: str | None = None


_HEADERS_CATALOG = SecurityHeadersCatalog(
    version="1.0.0", required_headers=(RequiredHeader(name="Content-Security-Policy"),)
)


def test_reflection_and_error_combined() -> None:
    analyzer = CompositeResponseAnalyzer()
    response = _FakeResponse(status_code=500, body=b"<script>alert('m')</script>")
    observations = analyzer.analyze(
        response=response,
        request_id="req_1",
        payload_value="<script>alert('m')</script>",
        detection_pattern=r"<script>alert\('m'\)</script>",
    )
    kinds = {o.kind for o in observations}
    assert "reflection" in kinds
    assert "http_error" in kinds


def test_clean_response_produces_no_observation() -> None:
    analyzer = CompositeResponseAnalyzer()
    response = _FakeResponse(status_code=200, body=b"<html>tout va bien</html>")
    observations = analyzer.analyze(response=response, request_id="req_1")
    assert observations == ()


def test_fetch_error_short_circuits_to_no_observations() -> None:
    analyzer = CompositeResponseAnalyzer()
    response = _FakeResponse(status_code=0, body=b"", fetch_error="Connection refused")
    observations = analyzer.analyze(response=response, request_id="req_1", payload_value="x")
    assert observations == ()


def test_security_headers_catalog_only_checked_when_provided() -> None:
    response = _FakeResponse(status_code=200, body=b"ok", headers={})

    without_catalog = CompositeResponseAnalyzer().analyze(response=response, request_id="req_1")
    assert without_catalog == ()

    with_catalog = CompositeResponseAnalyzer(security_headers_catalog=_HEADERS_CATALOG).analyze(
        response=response, request_id="req_1"
    )
    assert any(o.kind == "missing_security_header" for o in with_catalog)
