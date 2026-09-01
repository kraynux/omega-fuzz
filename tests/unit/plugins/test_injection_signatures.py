# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_fuzz.domain.findings.payload_catalog import PayloadCatalog, PayloadEntry
from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.plugins.signatures.injection_signatures import build_plan

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)

_CATALOG = PayloadCatalog(
    category="injection",
    version="1.0.0",
    payloads=(PayloadEntry(value="' OR '1'='1"), PayloadEntry(value="'; --")),
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
    assert test.module == "sigsqli"
    for request in requests:
        assert request.context.phase is RequestPhase.TEST
        assert request.test_id == test.test_id
        assert request.metadata.detection_pattern is None
