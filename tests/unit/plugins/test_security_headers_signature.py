# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.plugins.signatures.security_headers_signature import build_plan

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_single_request_no_mutation() -> None:
    test, requests = build_plan(
        target_short="example_root", sequence=1, url="https://example.com/", now=NOW
    )
    assert len(requests) == 1
    assert test.module == "sigheaders"
    assert test.target.parameters == ()
    request = requests[0]
    assert request.context.phase is RequestPhase.TEST
    assert request.test_id == test.test_id
    assert request.url == "https://example.com/"
