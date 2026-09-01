# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran d'accueil : menu principal. Adapte du patron screens/home.py
d'omega-check (D-007/D-008). Phase 10d : entree "Scanner" ajoutee
(ecran cible existe desormais, scan_setup_screen.py). Phase 10e : entree
"Reglages" ajoutee (settings_screen.py). Phase 10h : entree "Historique"
ajoutee (history_screen.py). Phase 10j : entree "Cibles" ajoutee
(targets_screen.py) — menu complet."""
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from omega_fuzz.interfaces.tui.screens.help_screen import HelpScreen
from omega_fuzz.interfaces.tui.screens.history_screen import HistoryScreen
from omega_fuzz.interfaces.tui.screens.quit_confirm import QuitConfirmScreen
from omega_fuzz.interfaces.tui.screens.scan_setup_screen import ScanSetupScreen
from omega_fuzz.interfaces.tui.screens.settings_screen import SettingsScreen
from omega_fuzz.interfaces.tui.screens.targets_screen import TargetsScreen
from omega_fuzz.interfaces.tui.widgets.home_wordmark import HomeWordmark

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from omega_fuzz.app.container import Container as AppContainer
    from omega_fuzz.app.container import ScanRuntime

_MENU_ITEMS: tuple[tuple[str, str], ...] = (
    ("scan", "Scanner"),
    ("targets", "Cibles"),
    ("settings", "Reglages"),
    ("history", "Historique"),
    ("help", "Aide"),
    ("quit", "Quitter"),
)


class HomeScreen(Screen[None]):
    """Menu principal, racine de la pile de navigation. N'herite pas de
    OmegaScreen : `echap` ici demande confirmation de sortie, pas un
    dismiss() (rien "en dessous" de cet ecran)."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "back", "Retour", show=True),
        Binding("up", "focus_previous_item", "Monter", show=False),
        Binding("down", "focus_next_item", "Descendre", show=False),
    ]

    def __init__(
        self,
        *,
        container: AppContainer,
        scan_runtime_factory: Callable[[Path | None], ScanRuntime],
    ) -> None:
        super().__init__()
        self._container = container
        self._scan_runtime_factory = scan_runtime_factory

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-home-root"):
            with Center():
                yield HomeWordmark()
            with Center():
                with Vertical(classes="omega-home-menu") as menu:
                    for item_id, label in _MENU_ITEMS:
                        with Container(classes="omega-btn-frame"):
                            yield Button(label.upper(), id=item_id)
                menu.border_title = "MENU PRINCIPAL"
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "scan":
            self.app.push_screen(
                ScanSetupScreen(
                    container=self._container, scan_runtime_factory=self._scan_runtime_factory
                )
            )
            return
        if event.button.id == "targets":
            self.app.push_screen(
                TargetsScreen(
                    container=self._container, scan_runtime_factory=self._scan_runtime_factory
                )
            )
            return
        if event.button.id == "settings":
            self.app.push_screen(SettingsScreen(container=self._container))
            return
        if event.button.id == "history":
            self.app.push_screen(HistoryScreen(container=self._container))
            return
        if event.button.id == "help":
            self.app.push_screen(HelpScreen())
            return
        if event.button.id == "quit":
            self.app.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)
            return

    def action_back(self) -> None:
        self.app.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)

    def action_focus_previous_item(self) -> None:
        self.focus_previous()

    def action_focus_next_item(self) -> None:
        self.focus_next()

    def _quit_if_confirmed(self, confirmed: bool | None) -> None:
        if confirmed:
            self.app.exit()
