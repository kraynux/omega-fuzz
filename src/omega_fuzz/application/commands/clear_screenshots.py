# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : vider le dossier de captures d'ecran (ecran Reglages).
Housekeeping filesystem simple, pas d'etat de domaine — meme patron que
`clear_exports.py`."""
from __future__ import annotations

import shutil
from pathlib import Path


def clear_screenshots(screenshots_dir: Path) -> None:
    shutil.rmtree(screenshots_dir, ignore_errors=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)
