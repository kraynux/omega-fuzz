# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlsplit

from omega_fuzz.domain.findings.payload_catalog import PayloadCatalog, PayloadEntry
from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.plugins.signatures.xss_signatures import build_plan

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)

_CATALOG = PayloadCatalog(
    category="xss",
    version="1.0.0",
    payloads=(
        PayloadEntry(value="<script>alert('m')</script>", detection_pattern=r"<script>alert\('m'\)</script>"),
        PayloadEntry(value="\"><svg onload=alert('m')>", detection_pattern=r"onload=alert\('m'\)"),
    ),
)


def test_one_request_per_catalog_entry() -> None:
    test, requests = build_plan(
        target_short="example_root",
        sequence=1,
        url="https://example.com/search?q=hello",
        parameter_name="q",
        catalog=_CATALOG,
        now=NOW,
    )
    assert len(requests) == len(_CATALOG.payloads)
    assert test.module == "sigxss"


def test_every_request_has_test_phase_test_id_and_metadata() -> None:
    test, requests = build_plan(
        target_short="example_root",
        sequence=1,
        url="https://example.com/search?q=hello",
        parameter_name="q",
        catalog=_CATALOG,
        now=NOW,
    )
    for request, entry in zip(requests, _CATALOG.payloads, strict=True):
        assert request.context.phase is RequestPhase.TEST
        assert request.test_id == test.test_id
        assert request.metadata.payload_value == entry.value
        assert request.metadata.detection_pattern == entry.detection_pattern
        query = dict(parse_qsl(urlsplit(request.url).query, keep_blank_values=True))
        assert query["q"] == entry.value


def test_no_payload_value_appears_in_ids() -> None:
    test, requests = build_plan(
        target_short="example_root",
        sequence=1,
        url="https://example.com/search?q=hello",
        parameter_name="q",
        catalog=_CATALOG,
        now=NOW,
    )
    for entry in _CATALOG.payloads:
        assert entry.value not in test.test_id
        for request in requests:
            assert entry.value not in request.request_id
