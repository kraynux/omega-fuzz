# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.domain.findings.payload_catalog import RequiredHeader, SecurityHeadersCatalog
from omega_fuzz.infrastructure.analyzers.header_analyzer import analyze_headers

_CATALOG = SecurityHeadersCatalog(
    version="1.0.0",
    required_headers=(
        RequiredHeader(name="Content-Security-Policy"),
        RequiredHeader(name="X-Content-Type-Options", expected_value="nosniff"),
    ),
)


def test_missing_header_is_verified() -> None:
    observations = analyze_headers(headers={}, catalog=_CATALOG, request_id="req_1")
    kinds = {o.kind for o in observations}
    assert "missing_security_header" in kinds
    assert all(o.confidence is ConfidenceLevel.VERIFIED for o in observations if o.kind == "missing_security_header")
    assert len(observations) == 2  # les 2 headers requis sont absents


def test_present_headers_with_correct_values_produce_no_observation() -> None:
    observations = analyze_headers(
        headers={"Content-Security-Policy": "default-src 'self'", "X-Content-Type-Options": "nosniff"},
        catalog=_CATALOG,
        request_id="req_1",
    )
    assert observations == ()


def test_wrong_expected_value_is_declared() -> None:
    observations = analyze_headers(
        headers={"Content-Security-Policy": "default-src 'self'", "X-Content-Type-Options": "sniff-anyway"},
        catalog=_CATALOG,
        request_id="req_1",
    )
    assert len(observations) == 1
    assert observations[0].kind == "misconfigured_security_header"
    assert observations[0].confidence is ConfidenceLevel.DECLARED


def test_header_name_lookup_is_case_insensitive() -> None:
    observations = analyze_headers(
        headers={"content-security-policy": "x", "x-content-type-options": "nosniff"},
        catalog=_CATALOG,
        request_id="req_1",
    )
    assert observations == ()
