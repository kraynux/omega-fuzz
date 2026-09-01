# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_fuzz.domain.services.redaction_service import redact_body_snippet, redact_headers


def test_sensitive_headers_are_redacted() -> None:
    headers = {
        "Cookie": "sessionid=abc123",
        "Authorization": "Bearer secrettoken",
        "Content-Type": "text/html",
    }
    redacted = redact_headers(headers)
    assert redacted["Cookie"] == "[EXPURGE]"
    assert redacted["Authorization"] == "[EXPURGE]"
    assert redacted["Content-Type"] == "text/html"  # non sensible, inchange


def test_header_redaction_is_case_insensitive() -> None:
    redacted = redact_headers({"set-cookie": "abc=123"})
    assert redacted["set-cookie"] == "[EXPURGE]"


def test_password_field_in_json_body_is_redacted() -> None:
    body = '{"username": "alice", "password": "hunter2"}'
    redacted = redact_body_snippet(body)
    assert "hunter2" not in redacted
    assert "alice" in redacted
    assert "[EXPURGE]" in redacted


def test_token_and_api_key_fields_are_redacted() -> None:
    body = '{"token": "abc.def.ghi", "api_key": "sk-12345"}'
    redacted = redact_body_snippet(body)
    assert "abc.def.ghi" not in redacted
    assert "sk-12345" not in redacted


def test_body_truncated_beyond_max_length() -> None:
    body = "x" * 500
    redacted = redact_body_snippet(body, max_length=50)
    assert len(redacted) == 50 + len("...[tronque]")
    assert redacted.endswith("...[tronque]")


def test_short_body_not_truncated() -> None:
    body = "clean response body"
    assert redact_body_snippet(body) == body
