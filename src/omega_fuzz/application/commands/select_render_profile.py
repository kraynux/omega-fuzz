# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : surcharger (ou remettre en automatique) le profil de rendu.
Porte depuis omega-check (D-007/D-008) — meme cle que
`interfaces/tui/controllers/startup_controller.py::_effective_render_profile`
(Phase 10c)."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omega_lib.terminal.models import RenderProfile

    from omega_fuzz.ports.settings_store import SettingsStore

_RENDER_PROFILE_OVERRIDE_KEY = "render_profile_override"


def select_render_profile(
    *, settings_store: SettingsStore, render_profile: RenderProfile | None
) -> None:
    settings_store.set(_RENDER_PROFILE_OVERRIDE_KEY, render_profile.value if render_profile else "")
