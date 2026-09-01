# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : vider le dossier d'export (ecran Reglages). Housekeeping
filesystem simple, pas d'etat de domaine — pas de port dedie (stdlib
`shutil` directement), porte depuis omega-check (D-007/D-008)."""
from __future__ import annotations

import shutil
from pathlib import Path


def clear_exports(exports_dir: Path) -> None:
    shutil.rmtree(exports_dir, ignore_errors=True)
    exports_dir.mkdir(parents=True, exist_ok=True)
