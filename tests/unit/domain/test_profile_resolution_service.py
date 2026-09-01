# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import pytest

from omega_fuzz.core.errors import ValidationError
from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.hard_caps import HARD_MAX_TOTAL_REQUESTS
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName
from omega_fuzz.domain.services.profile_resolution_service import (
    resolve_manual,
    resolve_preset,
)
from omega_fuzz.domain.services.url_normalization_service import normalize_url

_ENTRY_URL = normalize_url("https://example.com/")


@pytest.mark.parametrize(
    "preset_name",
    list(PresetName),
)
def test_every_preset_resolves_to_an_effective_configuration(preset_name: PresetName) -> None:
    config = resolve_preset(preset_name, entry_url=_ENTRY_URL)
    assert config.preset is preset_name
    assert config.scope.root_host == "example.com"
    assert config.scope.scope_port == 443


def test_lab_extreme_preset_requires_confirmation() -> None:
    config = resolve_preset(PresetName.LAB_EXTREME, entry_url=_ENTRY_URL)
    assert config.requires_confirmation is True


def test_prod_safe_preset_does_not_require_confirmation() -> None:
    config = resolve_preset(PresetName.PROD_SAFE, entry_url=_ENTRY_URL)
    assert config.requires_confirmation is False
    assert config.warnings == ()


def test_valid_override_is_recorded_and_applied() -> None:
    config = resolve_preset(
        PresetName.PROD_SAFE, entry_url=_ENTRY_URL, overrides={"max_total_requests": 1500}
    )
    assert config.limits.max_total_requests == 1500
    assert config.overrides == {"max_total_requests": 1500}


def test_override_beyond_hard_cap_raises() -> None:
    with pytest.raises(ValidationError):
        resolve_preset(
            PresetName.PROD_SAFE,
            entry_url=_ENTRY_URL,
            overrides={"max_total_requests": HARD_MAX_TOTAL_REQUESTS + 1},
        )


def test_manual_strict_violent_triggers_warning_and_confirmation() -> None:
    config = resolve_manual(
        entry_url=_ENTRY_URL,
        aggressiveness=AggressivenessLevel.VIOLENT,
        scope_profile=ScopeProfileName.STRICT,
    )
    assert config.requires_confirmation is True
    assert len(config.warnings) == 1
    assert "strict" in config.warnings[0]
    assert "violent" in config.warnings[0]


def test_manual_standard_standard_does_not_trigger_warning() -> None:
    config = resolve_manual(
        entry_url=_ENTRY_URL,
        aggressiveness=AggressivenessLevel.STANDARD,
        scope_profile=ScopeProfileName.STANDARD,
    )
    assert config.requires_confirmation is False
    assert config.warnings == ()
