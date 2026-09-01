# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran de revue de la configuration effective + confirmation avant
lancement (Phase 10d, fusionne les ecrans "Review configuration" et
"Confirmation required" de OMEGA-FUZZ_PLAN_DEV.md Phase 10 — la
confirmation renforcee n'a de sens qu'apres avoir vu la config
effective).

La confirmation se fait ICI, dans les widgets Textual — pas via
`ConfirmationProvider.confirm()` (bloquant, incompatible avec
push_screen()+callback asynchrone). `start_scan()` recevra donc un
`ConfirmationProvider` toujours-vrai (`AlreadyConfirmedProvider`,
construit par `scan_runtime_factory`, deja resolu par
`scan_setup_screen.py`)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, Static

from omega_fuzz.application.commands.start_scan import required_confirmation_phrase
from omega_fuzz.interfaces.cli.presenters.configuration_presenter import render_configuration
from omega_fuzz.interfaces.tui.screens._base import OmegaScreen
from omega_fuzz.interfaces.tui.screens.scan_progress_screen import ScanProgressScreen

if TYPE_CHECKING:
    from omega_fuzz.app.container import Container as AppContainer
    from omega_fuzz.app.container import ScanRuntime
    from omega_fuzz.application.commands.prepare_scan import PreparedScan


class ScanReviewScreen(OmegaScreen):
    """Revue + confirmation avant lancement reel du scan."""

    def __init__(
        self, *, prepared: PreparedScan, scan_runtime: ScanRuntime, container: AppContainer
    ) -> None:
        super().__init__()
        self._prepared = prepared
        self._scan_runtime = scan_runtime
        self._container = container
        self._required_phrase = required_confirmation_phrase(prepared)

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static("REVUE AVANT LANCEMENT", classes="omega-title")
            yield Static(render_configuration(self._prepared))

            needs_confirmation = self._prepared.configuration.requires_confirmation
            launch_disabled = False
            if needs_confirmation:
                yield Static("Confirmation requise avant lancement.", classes="omega-subtitle")
                if self._required_phrase is not None:
                    yield Static(f"Tapez exactement : {self._required_phrase}", classes="omega-hint")
                    yield Input(placeholder=self._required_phrase, id="confirm-input")
                    launch_disabled = True

            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Lancer", id="launch", variant="primary", disabled=launch_disabled)
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "confirm-input":
            return
        self.query_one("#launch", Button).disabled = event.value != self._required_phrase

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id != "launch":
            return
        self.app.push_screen(
            ScanProgressScreen(
                prepared=self._prepared, scan_runtime=self._scan_runtime, container=self._container
            )
        )
