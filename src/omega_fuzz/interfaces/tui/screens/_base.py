# Copyright (c) 2026 kraynux - Licence MIT
"""Classe de base partagee par tous les ecrans navigables (retour clavier).
Portee verbatim depuis omega-check (D-007/D-008)."""
from __future__ import annotations

from typing import ClassVar

from textual.binding import Binding, BindingType
from textual.screen import Screen


class OmegaScreen(Screen[None]):
    """Ecran navigable standard : ajoute `echap` -> retour, sans qu'aucun
    ecran n'ait a redeclarer son propre binding. `home.py` et
    `quit_confirm.py` n'en heritent pas (voir leurs propres fichiers)."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "back", "Retour", show=True),
        Binding("up", "focus_previous_item", "Monter", show=False),
        Binding("down", "focus_next_item", "Descendre", show=False),
    ]

    def action_back(self) -> None:
        self.dismiss()

    def action_focus_previous_item(self) -> None:
        self.focus_previous()

    def action_focus_next_item(self) -> None:
        self.focus_next()
