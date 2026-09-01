# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : choisir et persister le theme actif.
Porte depuis omega-check (D-007/D-008)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_lib.theme.policies import TUI_THEMES

from omega_fuzz.application.exceptions import UnknownThemeError

if TYPE_CHECKING:
    from omega_fuzz.ports.settings_store import SettingsStore

_THEME_KEY = "theme"


def select_theme(*, settings_store: SettingsStore, theme_name: str) -> None:
    if theme_name not in TUI_THEMES:
        raise UnknownThemeError(theme_name)
    settings_store.set(_THEME_KEY, theme_name)
