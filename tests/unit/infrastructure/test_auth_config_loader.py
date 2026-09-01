# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from pathlib import Path

import pytest

from omega_fuzz.core.errors import ConfigurationError
from omega_fuzz.domain.auth.auth_context import AuthMode
from omega_fuzz.infrastructure.configuration.auth_config_loader import load_auth_context


def test_missing_mode_defaults_to_none(tmp_path: Path) -> None:
    path = tmp_path / "auth.yaml"
    path.write_text("", encoding="utf-8")
    context = load_auth_context(path)
    assert context.mode is AuthMode.NONE


def test_cookie_mode_loads_cookie(tmp_path: Path) -> None:
    path = tmp_path / "auth.yaml"
    path.write_text("mode: cookie\ncookie: abc123\n", encoding="utf-8")
    context = load_auth_context(path)
    assert context.mode is AuthMode.COOKIE
    assert context.cookie == "abc123"


def test_cookie_mode_without_cookie_field_raises(tmp_path: Path) -> None:
    path = tmp_path / "auth.yaml"
    path.write_text("mode: cookie\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_auth_context(path)


def test_unknown_mode_raises(tmp_path: Path) -> None:
    path = tmp_path / "auth.yaml"
    path.write_text("mode: telepathy\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_auth_context(path)


def test_non_mapping_yaml_raises(tmp_path: Path) -> None:
    path = tmp_path / "auth.yaml"
    path.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_auth_context(path)
