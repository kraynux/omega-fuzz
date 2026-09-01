# Copyright (c) 2026 kraynux - Licence MIT
"""Criteres d'acceptation de la Phase 2 (OMEGA-FUZZ_PLAN_DEV.md §5)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from omega_fuzz.domain.requests.request_context import RequestContext
from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.domain.requests.scan_request import ScanRequest
from omega_fuzz.domain.scans.scan import Scan
from omega_fuzz.domain.scans.scan_id import ScanId
from omega_fuzz.domain.scans.scan_status import ScanStatus
from omega_fuzz.infrastructure.ids import SystemIdGenerator

NOW = datetime.now(timezone.utc)


def _context(*, phase: RequestPhase) -> RequestContext:
    return RequestContext(phase=phase, module="fuzzhttp", purpose="mutate", target_id="example_root", depth=1)


def test_scan_id_generated_in_production_is_a_valid_uuid_hex() -> None:
    scan_id_value = SystemIdGenerator().new_scan_id()
    assert len(scan_id_value) == 32
    assert all(c in "0123456789abcdef" for c in scan_id_value)
    Scan(
        scan_id=ScanId(scan_id_value),
        target_id="example_root",
        status=ScanStatus.PLANNED,
        created_at=NOW,
    )


def test_test_phase_request_requires_non_empty_test_id() -> None:
    with pytest.raises(ValueError):
        ScanRequest(
            request_id="req_fuzzhttp_example_root_000001_0001",
            method="GET",
            url="https://example.com/search?q=x",
            normalized_url="https://example.com/search?q=x",
            context=_context(phase=RequestPhase.TEST),
            created_at=NOW,
            test_id=None,
        )


def test_discovery_phase_request_does_not_require_test_id() -> None:
    request = ScanRequest(
        request_id="req_crawler_example_root_000001_0001",
        method="GET",
        url="https://example.com/",
        normalized_url="https://example.com/",
        context=_context(phase=RequestPhase.DISCOVERY),
        created_at=NOW,
    )
    assert request.test_id is None
    assert request.context.phase is RequestPhase.DISCOVERY
