# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import pytest

from omega_fuzz.domain.targets.depth import HARD_MAX_DEPTH, validate_depth
from omega_fuzz.domain.targets.host import normalize_host
from omega_fuzz.domain.targets.port import normalize_port


def test_normalize_host_lowercases() -> None:
    assert normalize_host("Example.COM") == "example.com"


def test_normalize_host_rejects_empty() -> None:
    with pytest.raises(ValueError):
        normalize_host("   ")


def test_normalize_port_uses_scheme_default_when_absent() -> None:
    assert normalize_port(scheme="https", explicit_port=None) == 443
    assert normalize_port(scheme="http", explicit_port=None) == 80


def test_normalize_port_keeps_explicit_port() -> None:
    assert normalize_port(scheme="https", explicit_port=8443) == 8443


def test_validate_depth_accepts_boundaries() -> None:
    assert validate_depth(0) == 0
    assert validate_depth(HARD_MAX_DEPTH) == HARD_MAX_DEPTH


def test_validate_depth_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        validate_depth(-1)
    with pytest.raises(ValueError):
        validate_depth(HARD_MAX_DEPTH + 1)
