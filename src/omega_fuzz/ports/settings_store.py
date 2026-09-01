# Copyright (c) 2026 kraynux - Licence MIT
"""Re-export depuis omega_lib (D-008), meme convention que
ports/terminal_detector.py : garde `omega_fuzz.ports.X` uniforme dans le
reste du code plutot que d'importer omega_lib directement partout."""
from __future__ import annotations

from omega_lib.ports.settings_store import SettingsStore

__all__ = ["SettingsStore"]
