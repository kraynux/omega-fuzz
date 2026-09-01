# Copyright (c) 2026 kraynux - Licence MIT
"""Resolution du dossier de captures d'ecran effectif — meme patron que
`report_orchestrator.resolve_exports_dir` (surcharge persistee par
l'ecran Reglages si presente, sinon `Container.default_screenshots_dir`).
Fichier dedie plutot qu'ajoute a `report_orchestrator.py` : une capture
d'ecran n'est pas un export de rapport, aucun lien avec `ReportModel`."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omega_fuzz.ports.settings_store import SettingsStore

_SCREENSHOTS_DIR_OVERRIDE_KEY = "screenshots_dir_override"


def resolve_screenshots_dir(*, settings_store: SettingsStore, default_screenshots_dir: Path) -> Path:
    override = settings_store.get(_SCREENSHOTS_DIR_OVERRIDE_KEY, "")
    return Path(override) if override else default_screenshots_dir
