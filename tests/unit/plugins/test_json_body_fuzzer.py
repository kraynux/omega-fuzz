# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import json
from datetime import datetime, timezone

from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.plugins.fuzzers.common.mutation_context import GENERIC_MUTATIONS
from omega_fuzz.plugins.fuzzers.json_body_fuzzer import build_plan

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_one_request_per_mutation_with_json_content_type() -> None:
    test, requests = build_plan(
        target_short="api_example_v1",
        sequence=3,
        url="https://example.com/api/v1/users",
        template={"username": "alice", "age": 30},
        key_name="username",
        now=NOW,
    )
    assert len(requests) == len(GENERIC_MUTATIONS)
    for request in requests:
        assert request.method == "POST"
        assert request.context.phase is RequestPhase.TEST
        assert request.test_id == test.test_id
        assert request.headers["Content-Type"] == "application/json"


def test_mutations_applied_to_target_key_only() -> None:
    _test, requests = build_plan(
        target_short="api_example_v1",
        sequence=3,
        url="https://example.com/api/v1/users",
        template={"username": "alice", "age": 30},
        key_name="username",
        now=NOW,
    )
    applied = []
    for request in requests:
        assert isinstance(request.body, bytes)
        body = json.loads(request.body.decode("utf-8"))
        applied.append(body["username"])
        assert body["age"] == 30
    assert applied == list(GENERIC_MUTATIONS)
