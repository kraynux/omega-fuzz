# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlsplit

from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.plugins.logic_tests.idor_checks import build_plan

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_one_request_per_candidate_value() -> None:
    test, requests = build_plan(
        target_short="example_root",
        sequence=11,
        url="https://example.com/api/orders?order_id=1",
        id_parameter_name="order_id",
        candidate_foreign_values=["2", "3", "9999"],
        now=NOW,
    )
    assert len(requests) == 3
    assert test.module == "logic"
    assert test.subtype == "idor"
    for request in requests:
        assert request.method == "GET"
        assert request.context.phase is RequestPhase.TEST
        assert request.test_id == test.test_id


def test_candidate_values_applied_to_id_parameter() -> None:
    _test, requests = build_plan(
        target_short="example_root",
        sequence=11,
        url="https://example.com/api/orders?order_id=1",
        id_parameter_name="order_id",
        candidate_foreign_values=["2", "3"],
        now=NOW,
    )
    applied = [
        dict(parse_qsl(urlsplit(r.url).query))["order_id"] for r in requests
    ]
    assert applied == ["2", "3"]


def test_description_documents_the_assumption() -> None:
    test, _requests = build_plan(
        target_short="example_root",
        sequence=11,
        url="https://example.com/api/orders?order_id=1",
        id_parameter_name="order_id",
        candidate_foreign_values=["2"],
        now=NOW,
    )
    assert "order_id" in test.description
