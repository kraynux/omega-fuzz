# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/confirmation_provider.py::ConfirmationProvider pour le
TUI (Phase 10d) : toujours `True` — la confirmation reelle a deja eu lieu
dans `interfaces/tui/screens/scan_review_screen.py` (widgets Textual,
bouton "Lancer" desactive tant que la phrase stricte n'est pas saisie
correctement quand elle est exigee) avant que `start_scan()` ne soit
appelee. `ConfirmationProvider.confirm()` est une methode synchrone,
bloquante par nature (`input()` cote CLI) — incompatible avec le modele
callback/push_screen() du TUI, d'ou ce mecanisme distinct plutot qu'un
`CliConfirmationPrompt` reutilise tel quel."""
from __future__ import annotations


class AlreadyConfirmedProvider:
    """Implemente ports/confirmation_provider.py::ConfirmationProvider."""

    def confirm(self, *, message: str, required_phrase: str | None = None) -> bool:
        return True
