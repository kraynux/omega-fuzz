# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.plugins.logic_tests.workflow_checks import build_plan

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_single_read_only_request() -> None:
    test, requests = build_plan(
        target_short="example_root",
        sequence=12,
        skip_to_url="https://example.com/checkout/confirm",
        now=NOW,
    )
    assert len(requests) == 1
    assert test.module == "logic"
    assert test.subtype == "workflow"
    request = requests[0]
    assert request.method == "GET"
    assert request.context.phase is RequestPhase.TEST
    assert request.test_id == test.test_id
    assert "/checkout/confirm" in test.description
