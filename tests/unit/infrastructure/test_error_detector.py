# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.infrastructure.analyzers.error_detector import detect_error


def test_5xx_status_is_verified_http_error() -> None:
    observation = detect_error(status_code=500, response_body="", request_id="req_1")
    assert observation is not None
    assert observation.kind == "http_error"
    assert observation.confidence is ConfidenceLevel.VERIFIED


def test_error_signature_in_body_is_inferred() -> None:
    observation = detect_error(
        status_code=200,
        response_body="Warning: mysql_fetch_array() expects parameter 1",
        request_id="req_1",
    )
    assert observation is not None
    assert observation.kind == "error_disclosure"
    assert observation.confidence is ConfidenceLevel.INFERRED


def test_clean_response_returns_none() -> None:
    observation = detect_error(status_code=200, response_body="<html>ok</html>", request_id="req_1")
    assert observation is None


def test_4xx_status_alone_is_not_an_error_observation() -> None:
    observation = detect_error(status_code=404, response_body="Not Found", request_id="req_1")
    assert observation is None
