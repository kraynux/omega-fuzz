# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.plugins.fuzzers.common.mutation_context import GENERIC_MUTATIONS
from omega_fuzz.plugins.fuzzers.header_fuzzer import build_plan

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_one_request_per_mutation_with_header_mutated() -> None:
    test, requests = build_plan(
        target_short="example_root",
        sequence=4,
        url="https://example.com/",
        header_name="User-Agent",
        now=NOW,
    )
    assert len(requests) == len(GENERIC_MUTATIONS)
    applied = [request.headers["User-Agent"] for request in requests]
    assert applied == list(GENERIC_MUTATIONS)
    for request in requests:
        assert request.context.phase is RequestPhase.TEST
        assert request.test_id == test.test_id


def test_unfuzzable_header_is_rejected() -> None:
    with pytest.raises(ValueError):
        build_plan(
            target_short="example_root",
            sequence=4,
            url="https://example.com/",
            header_name="Host",
            now=NOW,
        )
