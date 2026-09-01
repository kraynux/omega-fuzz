# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Historique : liste des scans passes + detail (Phase 10h). Adapte
du patron screens/history.py d'omega-check (D-007/D-008) — sans
"Comparer"/"Rejouer" : aucune URL d'entree ni configuration effective
n'est persistee pour un scan passe (`target_id` est un slug court, pas
une URL), donc ni relancer un scan identique ni reconstruire un second
`ReportModel` complet pour comparaison n'est possible avec les donnees
reellement disponibles."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from omega_fuzz.application.queries.get_scan_history import get_scan_history
from omega_fuzz.application.queries.list_findings_for_scan import list_findings_for_scan
from omega_fuzz.interfaces.tui.screens._base import OmegaScreen
from omega_fuzz.interfaces.tui.screens.history_detail_screen import HistoryDetailScreen

if TYPE_CHECKING:
    from omega_fuzz.app.container import Container as AppContainer
    from omega_fuzz.domain.scans.scan import Scan


class HistoryScreen(OmegaScreen):
    """Liste des scans passes, filtrable par cible."""

    def __init__(self, *, container: AppContainer) -> None:
        super().__init__()
        self._container = container
        self._scans_by_id: dict[str, Scan] = {}
        self._selected_scan_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("HISTORIQUE", classes="omega-title")
            yield Input(placeholder="Filtrer par cible...", id="target-filter")
            yield DataTable(id="history-table")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Voir le detail", id="view")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#history-table", DataTable)
        table.add_columns("Scan", "Cible", "Statut", "Cree le", "Findings")
        table.cursor_type = "row"
        self._refresh(None)

    def _refresh(self, target_filter: str | None) -> None:
        scans = list(get_scan_history(scan_repository=self._container.scan_repository))
        if target_filter:
            needle = target_filter.lower()
            scans = [scan for scan in scans if needle in scan.target_id.lower()]
        self._scans_by_id = {scan.scan_id.value: scan for scan in scans}

        table = self.query_one("#history-table", DataTable)
        table.clear()
        for scan in scans:
            findings_count = len(
                list_findings_for_scan(
                    finding_repository=self._container.finding_repository,
                    scan_id=scan.scan_id.value,
                )
            )
            table.add_row(
                scan.scan_id.value[:12],
                scan.target_id,
                scan.status.value,
                scan.created_at.strftime("%Y-%m-%d %H:%M"),
                str(findings_count),
                key=scan.scan_id.value,
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "target-filter":
            self._refresh(event.value.strip())

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._selected_scan_id = str(event.row_key.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id != "view":
            return
        if self._selected_scan_id is None:
            self.app.notify("Selectionnez d'abord une ligne.", severity="warning")
            return
        scan = self._scans_by_id.get(self._selected_scan_id)
        if scan is None:
            return
        self.app.push_screen(HistoryDetailScreen(scan=scan, container=self._container))
