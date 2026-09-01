# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import pytest

from omega_fuzz.core.errors import ValidationError
from omega_fuzz.domain.profiles.hard_caps import HARD_MAX_TOTAL_REQUESTS
from omega_fuzz.domain.profiles.limits import Limits
from omega_fuzz.domain.services.limit_service import validate_limits


def _limits(**overrides: int) -> Limits:
    defaults: dict[str, int] = {
        "max_duration_seconds": 300,
        "max_total_requests": 1000,
        "max_tests": 500,
        "max_concurrent_requests": 2,
        "max_requests_per_path": 50,
        "max_requests_per_param": 20,
        "max_paths_per_target": 100,
        "max_params_per_path": 10,
        "max_errors_before_pause": 10,
    }
    defaults.update(overrides)
    return Limits(**defaults)


def test_validate_limits_accepts_values_within_hard_caps() -> None:
    validate_limits(_limits())


def test_validate_limits_rejects_value_beyond_hard_cap() -> None:
    with pytest.raises(ValidationError):
        validate_limits(_limits(max_total_requests=HARD_MAX_TOTAL_REQUESTS + 1))


def test_limits_default_evidence_and_body_size_are_within_hard_caps() -> None:
    limits = _limits()
    validate_limits(limits)
    assert limits.max_response_body_size == 10 * 1024 * 1024
    assert limits.max_evidence_storage_per_scan == 300 * 1024 * 1024
