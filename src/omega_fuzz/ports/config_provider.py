# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de chargement de configuration (OMEGA-FUZZ_ARBORESCENCE.md
§15.3). Couvre la configuration de scan (profil, scope, presets) et le
fichier `--auth-config` (OMEGA-FUZZ_SPECIFICATIONS.md §8.5) — le type de
retour est un mapping generique a ce stade (Phase 0), affine une fois les
modeles `domain.profiles`/`domain.auth` disponibles."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class ConfigProvider(Protocol):
    def load(self, path: Path) -> dict[str, Any]: ...
