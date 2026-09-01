# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlsplit

from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.plugins.fuzzers.common.mutation_context import GENERIC_MUTATIONS
from omega_fuzz.plugins.fuzzers.form_parameter_fuzzer import build_plan

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_one_request_per_mutation_with_form_content_type() -> None:
    test, requests = build_plan(
        target_short="example_root",
        sequence=2,
        action_url="https://example.com/contact",
        method="post",
        fields={"email": "a@example.com", "message": "hi"},
        field_name="message",
        now=NOW,
    )
    assert len(requests) == len(GENERIC_MUTATIONS)
    for request in requests:
        assert request.method == "POST"
        assert request.context.phase is RequestPhase.TEST
        assert request.test_id == test.test_id
        assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"


def test_mutations_applied_to_target_field_only() -> None:
    _test, requests = build_plan(
        target_short="example_root",
        sequence=2,
        action_url="https://example.com/contact",
        method="POST",
        fields={"email": "a@example.com", "message": "hi"},
        field_name="message",
        now=NOW,
    )
    applied = []
    for request in requests:
        assert isinstance(request.body, bytes)
        fields = dict(parse_qsl(request.body.decode("utf-8"), keep_blank_values=True))
        applied.append(fields["message"])
        assert fields["email"] == "a@example.com"
    assert applied == list(GENERIC_MUTATIONS)


def test_get_form_serializes_fields_into_query_string() -> None:
    _test, requests = build_plan(
        target_short="example_root",
        sequence=3,
        action_url="https://example.com/search",
        method="GET",
        fields={"q": "hello", "category": "all"},
        field_name="q",
        now=NOW,
    )
    assert len(requests) == len(GENERIC_MUTATIONS)
    applied = []
    for request in requests:
        assert request.method == "GET"
        assert request.body is None
        assert not request.headers
        query_pairs = dict(parse_qsl(urlsplit(request.url).query, keep_blank_values=True))
        applied.append(query_pairs["q"])
        assert query_pairs["category"] == "all"
    assert applied == list(GENERIC_MUTATIONS)


def test_get_form_merges_with_existing_action_query_string() -> None:
    _test, requests = build_plan(
        target_short="example_root",
        sequence=3,
        action_url="https://example.com/search?lang=fr",
        method="GET",
        fields={"q": "hello"},
        field_name="q",
        now=NOW,
    )
    for request in requests:
        query_pairs = dict(parse_qsl(urlsplit(request.url).query, keep_blank_values=True))
        assert query_pairs["lang"] == "fr"
