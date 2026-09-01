# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Cibles : liste de cibles favorites (URLs), Phase 10j. Concept
absent des documents OMEGA-FUZZ_* d'origine (herite du menu de
reference CHECK/omega-scan, adapte : des URLs completes enregistrees
manuellement, pas des IP/hosts nus derives d'un autre stockage — voir
ports/target_repository.py)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from omega_fuzz.application.commands.pin_target import pin_target
from omega_fuzz.application.commands.unpin_target import unpin_target
from omega_fuzz.application.queries.list_pinned_targets import list_pinned_targets
from omega_fuzz.domain.targets.url import UrlNormalizationError
from omega_fuzz.interfaces.tui.screens._base import OmegaScreen
from omega_fuzz.interfaces.tui.screens.scan_setup_screen import ScanSetupScreen

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from omega_fuzz.app.container import Container as AppContainer
    from omega_fuzz.app.container import ScanRuntime


class TargetsScreen(OmegaScreen):
    """Cibles favorites : ajouter/supprimer/lancer un scan dessus."""

    def __init__(
        self,
        *,
        container: AppContainer,
        scan_runtime_factory: Callable[[Path | None], ScanRuntime],
    ) -> None:
        super().__init__()
        self._container = container
        self._scan_runtime_factory = scan_runtime_factory
        self._selected_url: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("CIBLES", classes="omega-title")
            with Horizontal(classes="omega-target-add-row"):
                yield Input(placeholder="https://example.com/", id="new-target-input")
                with Container(classes="omega-btn-frame"):
                    yield Button("Ajouter", id="add", variant="primary")

            yield DataTable(id="targets-table")

            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Scanner cette cible", id="scan-target", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Supprimer", id="remove", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#targets-table", DataTable)
        table.add_columns("Cible")
        table.cursor_type = "row"
        self._refresh()

    def _refresh(self) -> None:
        table = self.query_one("#targets-table", DataTable)
        table.clear()
        for url in list_pinned_targets(target_repository=self._container.target_repository):
            table.add_row(url, key=url)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._selected_url = str(event.row_key.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "new-target-input":
            self._add_target()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id == "add":
            self._add_target()
            return
        if self._selected_url is None:
            self.app.notify("Selectionnez d'abord une cible.", severity="warning")
            return
        if event.button.id == "remove":
            unpin_target(target_repository=self._container.target_repository, url=self._selected_url)
            self._selected_url = None
            self._refresh()
            return
        if event.button.id == "scan-target":
            self.app.push_screen(
                ScanSetupScreen(
                    container=self._container,
                    scan_runtime_factory=self._scan_runtime_factory,
                    initial_target=self._selected_url,
                )
            )

    def _add_target(self) -> None:
        input_widget = self.query_one("#new-target-input", Input)
        raw = input_widget.value.strip()
        if not raw:
            self.app.notify("Saisissez une URL.", severity="warning")
            return
        try:
            pin_target(target_repository=self._container.target_repository, raw_url=raw)
        except UrlNormalizationError as exc:
            self.app.notify(str(exc), severity="error")
            return
        input_widget.value = ""
        self._refresh()
