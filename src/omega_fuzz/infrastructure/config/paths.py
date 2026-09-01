# Copyright (c) 2026 kraynux - Licence MIT
"""Resolution des chemins runtime (var/), la seule source de verite pour
ces chemins. Porte depuis omega-check (D-007/D-008) : tout doit vivre par
defaut dans le dossier de l'application (`./var`), rien dans le
filesystem utilisateur (`~/.config`, `~/.local/share`) sauf choix
explicite (override via `$OMEGA_FUZZ_VAR_DIR`).

Corrige `app/composition_root.py` (Phase 10b/10c), qui utilisait a tort
`~/.omega-fuzz/` — invente sans avoir verifie la convention deja
etablie par le reste de la suite (bug reel rapporte : "ou va l'export ?
pas de dossier var/export")."""
from __future__ import annotations

import os
from pathlib import Path

DEFAULT_VAR_DIRNAME = "var"
ENV_VAR_DIR = "OMEGA_FUZZ_VAR_DIR"


def resolve_var_dir() -> Path:
    """Racine des fichiers runtime : `$OMEGA_FUZZ_VAR_DIR` si defini,
    sinon `./var` relatif au repertoire courant d'execution."""
    override = os.environ.get(ENV_VAR_DIR)
    if override:
        return Path(override)
    return Path.cwd() / DEFAULT_VAR_DIRNAME


def default_db_path(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "db" / "omega-fuzz.db"


def default_settings_path(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "settings.json"


def default_exports_dir(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "exports"


def default_targets_path(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "targets.json"


def default_screenshots_dir(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "screenshots"
