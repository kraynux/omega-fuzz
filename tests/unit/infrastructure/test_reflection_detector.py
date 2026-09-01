# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.infrastructure.analyzers.reflection_detector import detect_reflection


def test_detection_pattern_match_is_corroborated() -> None:
    observation = detect_reflection(
        response_body="<html><script>alert('omegafuzz-marker')</script></html>",
        request_id="req_sigxss_example_root_000001_0001",
        payload_value="<script>alert('omegafuzz-marker')</script>",
        detection_pattern=r"<script>alert\('omegafuzz-marker'\)</script>",
    )
    assert observation is not None
    assert observation.kind == "reflection"
    assert observation.confidence is ConfidenceLevel.CORROBORATED


def test_detection_pattern_no_match_returns_none() -> None:
    observation = detect_reflection(
        response_body="<html>rien ici</html>",
        request_id="req_sigxss_example_root_000001_0001",
        payload_value="<script>alert('omegafuzz-marker')</script>",
        detection_pattern=r"<script>alert\('omegafuzz-marker'\)</script>",
    )
    assert observation is None


def test_substring_match_without_pattern_is_inferred() -> None:
    observation = detect_reflection(
        response_body="valeur=abc123marker",
        request_id="req_fuzzhttp_example_root_000001_0001",
        payload_value="abc123marker",
    )
    assert observation is not None
    assert observation.confidence is ConfidenceLevel.INFERRED


def test_empty_payload_never_matches() -> None:
    observation = detect_reflection(
        response_body="anything at all",
        request_id="req_fuzzhttp_example_root_000001_0001",
        payload_value="",
    )
    assert observation is None
