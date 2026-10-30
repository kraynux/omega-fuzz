# Copyright (c) 2026 kraynux - Licence MIT
"""Cas d'usage : vider le dossier d'exports ou de captures d'ecran (ecran Reglages).

Remplace clear_exports.py / clear_screenshots.py (correctif 2026-10-27, commun a la suite
omega-*) :
- le dossier vide est le dossier CONFIGURE dans Reglages (plus le dossier par defaut quand un
  autre est choisi) ;
- seul le CONTENU est supprime, le dossier reste ; un lien symbolique est supprime sans suivre
  sa cible ;
- dossiers systeme, personnels, dossier de l'application et ses parents refuses : le champ est
  libre, une faute de frappe (`/`, `/etc`) ne doit jamais vider le systeme ;
- un element qui resiste (droits) est signale, jamais retente avec `sudo` : une demande de mot
  de passe dans la TUI figerait l'application."""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from omega_fuzz.shared.i18n import _

_SYSTEM_DIRS = frozenset(Path(p) for p in (
    "/", "/bin", "/boot", "/dev", "/etc", "/home", "/lib", "/lib32", "/lib64", "/media", "/mnt",
    "/opt", "/proc", "/root", "/run", "/sbin", "/srv", "/sys", "/tmp", "/usr", "/var",
    "/var/lib", "/var/log", "/usr/local",
))


class UnsafeDirectoryError(Exception):
    """Dossier qu'on refuse de vider."""

    def __init__(self, path: str, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(_("Dossier refusé ({reason}) : {path}").format(reason=reason, path=path))


@dataclass(frozen=True)
class ClearResult:
    directory: Path
    removed: int
    failed: tuple[str, ...]


def check_clearable(directory: Path, app_root: Path) -> Path:
    """Chemin reel du dossier a vider, ou UnsafeDirectoryError s'il ne doit jamais l'etre."""
    target = directory.resolve()
    root = app_root.resolve()
    if target in _SYSTEM_DIRS or target.parent == Path("/home"):
        raise UnsafeDirectoryError(str(target), _("dossier système ou personnel"))
    if target == root or target in root.parents:
        raise UnsafeDirectoryError(str(target), _("contient l'installation de omega-fuzz"))
    if target.exists() and not target.is_dir():
        raise UnsafeDirectoryError(str(target), _("ce n'est pas un dossier"))
    return target


def clear_directory(directory: Path, app_root: Path) -> ClearResult:
    """Supprime tout le contenu du dossier (cree s'il n'existe pas) ; continue apres un echec.
    Peut etre long : a appeler hors du thread de l'interface."""
    target = check_clearable(directory, app_root)
    target.mkdir(parents=True, exist_ok=True)
    removed = 0
    failed: list[str] = []
    for entry in sorted(target.iterdir()):
        try:
            if entry.is_dir() and not entry.is_symlink():
                shutil.rmtree(entry)
            else:
                entry.unlink()
        except OSError as exc:
            failed.append(f"{entry.name} ({exc.strerror or exc})")
        else:
            removed += 1
    return ClearResult(target, removed, tuple(failed))
