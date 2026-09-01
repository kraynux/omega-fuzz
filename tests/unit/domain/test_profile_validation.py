# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import pytest

from omega_fuzz.core.errors import ValidationError
from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.aggressiveness_profile import AGGRESSIVENESS_PROFILES
from omega_fuzz.domain.profiles.hard_caps import HARD_MAX_TOTAL_REQUESTS
from omega_fuzz.domain.profiles.profile_validation import apply_overrides


def test_override_within_hard_caps_is_applied() -> None:
    base = AGGRESSIVENESS_PROFILES[AggressivenessLevel.DOUX]
    effective = apply_overrides(base, {"max_total_requests": 2000})
    assert effective.max_total_requests == 2000
    assert effective.max_duration_seconds == base.max_duration_seconds


def test_override_beyond_hard_cap_raises() -> None:
    base = AGGRESSIVENESS_PROFILES[AggressivenessLevel.DOUX]
    with pytest.raises(ValidationError):
        apply_overrides(base, {"max_total_requests": HARD_MAX_TOTAL_REQUESTS + 1})


def test_unknown_field_name_raises() -> None:
    base = AGGRESSIVENESS_PROFILES[AggressivenessLevel.DOUX]
    with pytest.raises(ValidationError):
        apply_overrides(base, {"max_bananas": 10})
