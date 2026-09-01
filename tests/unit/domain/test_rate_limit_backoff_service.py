# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_fuzz.domain.services.rate_limit_backoff_service import (
    MAX_BACKOFF_DELAY_SECONDS,
    compute_backoff_delay,
)


def test_status_429_without_retry_after_triggers_exponential_backoff() -> None:
    delay = compute_backoff_delay(
        status_code=429, retry_after_header=None, consecutive_backoff_triggers=0
    )
    assert delay == 2.0


def test_retry_after_header_takes_priority() -> None:
    delay = compute_backoff_delay(
        status_code=429, retry_after_header="30", consecutive_backoff_triggers=0
    )
    assert delay == 30.0


def test_retry_after_present_even_without_429() -> None:
    delay = compute_backoff_delay(
        status_code=200, retry_after_header="5", consecutive_backoff_triggers=0
    )
    assert delay == 5.0


def test_backoff_doubles_and_caps_at_maximum() -> None:
    delay = compute_backoff_delay(
        status_code=429, retry_after_header=None, consecutive_backoff_triggers=10
    )
    assert delay == MAX_BACKOFF_DELAY_SECONDS


def test_latency_heuristic_triggers_backoff_when_median_exceeds_threshold() -> None:
    baseline = 0.1
    recent = [1.0] * 20  # bien au-dela de 3x la latence de reference
    delay = compute_backoff_delay(
        status_code=200,
        retry_after_header=None,
        consecutive_backoff_triggers=0,
        recent_latencies=recent,
        baseline_latency=baseline,
    )
    assert delay == 2.0


def test_no_signal_returns_none() -> None:
    delay = compute_backoff_delay(
        status_code=200,
        retry_after_header=None,
        consecutive_backoff_triggers=0,
        recent_latencies=[0.1] * 20,
        baseline_latency=0.1,
    )
    assert delay is None


def test_latency_window_not_yet_full_returns_none() -> None:
    delay = compute_backoff_delay(
        status_code=200,
        retry_after_header=None,
        consecutive_backoff_triggers=0,
        recent_latencies=[10.0] * 5,
        baseline_latency=0.1,
    )
    assert delay is None
