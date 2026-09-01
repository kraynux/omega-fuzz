# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from dataclasses import replace

from omega_fuzz.domain.profiles.limits import Limits
from omega_fuzz.domain.reports.scan_statistics import ScanStatistics
from omega_fuzz.domain.reports.termination import TerminationTrigger
from omega_fuzz.domain.services.limit_service import (
    can_reserve_request,
    determine_termination,
    is_param_request_limit_reached,
    is_path_request_limit_reached,
)

_LIMITS = Limits(
    max_duration_seconds=300,
    max_total_requests=1000,
    max_tests=500,
    max_concurrent_requests=2,
    max_requests_per_path=50,
    max_requests_per_param=20,
    max_paths_per_target=100,
    max_params_per_path=10,
    max_errors_before_pause=10,
)


def test_can_reserve_request_true_below_budget() -> None:
    stats = ScanStatistics(total_requests=999)
    assert can_reserve_request(stats=stats, limits=_LIMITS)


def test_can_reserve_request_false_at_budget() -> None:
    stats = ScanStatistics(total_requests=1000)
    assert not can_reserve_request(stats=stats, limits=_LIMITS)


def test_path_and_param_limits_isolate_the_endpoint_without_stopping_scan() -> None:
    assert is_path_request_limit_reached(requests_for_path=50, limits=_LIMITS)
    assert not is_path_request_limit_reached(requests_for_path=49, limits=_LIMITS)
    assert is_param_request_limit_reached(requests_for_param=20, limits=_LIMITS)
    assert not is_param_request_limit_reached(requests_for_param=19, limits=_LIMITS)


def test_determine_termination_none_when_no_limit_reached() -> None:
    stats = ScanStatistics(total_requests=1)
    assert determine_termination(stats=stats, limits=_LIMITS, elapsed_seconds=1.0) is None


def test_determine_termination_on_duration() -> None:
    stats = ScanStatistics()
    reason = determine_termination(stats=stats, limits=_LIMITS, elapsed_seconds=300.0)
    assert reason is not None
    assert reason.trigger is TerminationTrigger.LIMIT_REACHED
    assert reason.limit_name == "max_duration_seconds"
    assert reason.configured_value == 300
    assert reason.observed_value == 300


def test_determine_termination_on_total_requests() -> None:
    stats = ScanStatistics(total_requests=1000)
    reason = determine_termination(stats=stats, limits=_LIMITS, elapsed_seconds=1.0)
    assert reason is not None
    assert reason.limit_name == "max_total_requests"
    assert reason.configured_value == 1000
    assert reason.observed_value == 1000


def test_duration_takes_priority_over_total_requests_when_both_are_reached() -> None:
    stats = ScanStatistics(total_requests=1000)
    reason = determine_termination(stats=stats, limits=_LIMITS, elapsed_seconds=300.0)
    assert reason is not None
    assert reason.limit_name == "max_duration_seconds"


def test_determine_termination_on_tests_executed() -> None:
    limits = replace(_LIMITS, max_total_requests=1_000_000)
    stats = ScanStatistics(total_requests=1, tests_executed=500)
    reason = determine_termination(stats=stats, limits=limits, elapsed_seconds=1.0)
    assert reason is not None
    assert reason.limit_name == "max_tests"
    assert reason.observed_value == 500
