# Copyright (c) 2026 kraynux - Licence MIT
"""Reproduit l'exemple multi-etapes de OMEGA-FUZZ_SPECIFICATIONS.md
§9.4."""
from __future__ import annotations

from omega_fuzz.domain.reports.scan_statistics import (
    ScanStatistics,
    record_observation_found,
    record_redirect_external_ignored,
    record_redirect_followed,
    record_redirect_out_of_scope_ignored,
    record_request,
    record_response_status,
    record_test_executed,
    record_url_evaluated,
)
from omega_fuzz.domain.requests.request_phase import RequestPhase


def test_multi_step_test_counts_one_test_and_three_requests() -> None:
    stats = ScanStatistics()

    # GET /form (CSRF token), POST /form (payload), GET /result (verification)
    for _ in range(3):
        stats = record_request(stats, phase=RequestPhase.TEST)
    stats = record_test_executed(stats)

    assert stats.tests_executed == 1
    assert stats.test_requests == 3
    assert stats.total_requests == 3
    assert stats.discovery_requests == 0


def test_discovery_and_test_requests_are_counted_separately() -> None:
    stats = ScanStatistics()
    stats = record_request(stats, phase=RequestPhase.DISCOVERY)
    stats = record_request(stats, phase=RequestPhase.DISCOVERY)
    stats = record_request(stats, phase=RequestPhase.TEST)

    assert stats.total_requests == 3
    assert stats.discovery_requests == 2
    assert stats.test_requests == 1


def test_record_request_does_not_mutate_original() -> None:
    original = ScanStatistics()
    record_request(original, phase=RequestPhase.TEST)

    assert original.total_requests == 0


def test_record_url_evaluated_splits_into_exactly_one_category() -> None:
    stats = ScanStatistics()
    stats = record_url_evaluated(stats, decision_accepted=True, beyond_depth=False)
    stats = record_url_evaluated(stats, decision_accepted=False, beyond_depth=False)
    stats = record_url_evaluated(stats, decision_accepted=True, beyond_depth=True)

    assert stats.urls_seen == 3
    assert stats.urls_in_scope == 1
    assert stats.urls_out_of_scope == 1
    assert stats.urls_beyond_depth == 1


def test_record_redirect_functions_increment_the_right_counter() -> None:
    stats = ScanStatistics()
    stats = record_redirect_followed(stats)
    stats = record_redirect_external_ignored(stats)
    stats = record_redirect_external_ignored(stats)
    stats = record_redirect_out_of_scope_ignored(stats)

    assert stats.redirects_followed == 1
    assert stats.redirects_external_ignored == 2
    assert stats.redirects_out_of_scope_ignored == 1


def test_record_observation_found_only_increments_total() -> None:
    stats = ScanStatistics()
    stats = record_observation_found(stats)
    stats = record_observation_found(stats)

    assert stats.findings_total == 2
    assert stats.findings_critical == 0
    assert stats.findings_high == 0
    assert stats.findings_medium == 0
    assert stats.findings_low == 0


def test_record_response_status_classifies_by_family() -> None:
    stats = ScanStatistics()
    for code in (200, 301, 404, 404, 500):
        stats = record_response_status(stats, status_code=code)

    assert stats.status_2xx == 1
    assert stats.status_3xx == 1
    assert stats.status_4xx == 2
    assert stats.status_5xx == 1


def test_record_response_status_timeout_fetch_error() -> None:
    stats = ScanStatistics()
    stats = record_response_status(stats, status_code=0, fetch_error="TimeoutException: timed out")

    assert stats.timeouts == 1
    assert stats.transport_errors == 0


def test_record_response_status_non_timeout_fetch_error() -> None:
    stats = ScanStatistics()
    stats = record_response_status(stats, status_code=0, fetch_error="Connection refused")

    assert stats.transport_errors == 1
    assert stats.timeouts == 0
