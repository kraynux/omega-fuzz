# Copyright (c) 2026 kraynux - Licence MIT
"""Racine des erreurs applicatives (meme motif D-007 que
core/errors.py/domain/errors.py — voir OMEGA-FUZZ_ARBORESCENCE.md
§5.3/§6)."""
from __future__ import annotations

from omega_fuzz.core.errors import OmegaFuzzError


class ApplicationError(OmegaFuzzError):
    """Racine des erreurs de la couche application."""


class ScanNotFoundError(ApplicationError):
    def __init__(self, scan_id: str) -> None:
        super().__init__(f"scan introuvable : {scan_id}")
        self.scan_id = scan_id


class InvalidScanTransitionError(ApplicationError):
    def __init__(self, current: object, target: object) -> None:
        super().__init__(f"transition de scan invalide : {current} -> {target}")
        self.current = current
        self.target = target


class IncompleteScanConfigurationError(ApplicationError):
    """Ni un preset, ni une combinaison complete (agressivite + scope
    profile) n'ont ete fournis a `prepare_scan` (OMEGA-FUZZ_PLAN_DEV.md
    Phase 6 : « les incoherences de configuration sont bloquantes »)."""

    def __init__(self) -> None:
        super().__init__(
            "configuration incomplete : fournir un preset, ou une agressivite ET "
            "un scope profile"
        )


class UnknownThemeError(ApplicationError):
    """Nom de theme absent du catalogue `omega_lib.theme.policies.TUI_THEMES`
    (Phase 10c, meme erreur que omega-check)."""

    def __init__(self, theme_name: str) -> None:
        super().__init__(f"theme inconnu : {theme_name!r}")
        self.theme_name = theme_name
