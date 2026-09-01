# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran de resultats : resume, findings, export de rapport (Phase 10d).
`export_report`/`build_scan_report` sont partages avec la CLI
(`application/services/report_orchestrator.py`) — meme logique, pas de
duplication.

Phase 10f : `Select` de theme d'export (bug reel rapporte : "export pas
de theme propose" — catalogue `omega_lib.theme.policies.EXPORT_PALETTES`,
deja utilise ailleurs dans la suite mais jamais cable cote omega-fuzz)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_lib.theme.policies import DEFAULT_EXPORT_THEME, EXPORT_PALETTES
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Select, Static

from omega_fuzz.application.services.report_orchestrator import (
    build_scan_report,
    export_report,
    resolve_exports_dir,
)
from omega_fuzz.core.version import __version__
from omega_fuzz.interfaces.tui.screens._base import OmegaScreen

if TYPE_CHECKING:
    from omega_fuzz.app.container import Container as AppContainer
    from omega_fuzz.application.commands.prepare_scan import PreparedScan
    from omega_fuzz.application.services.scan_orchestrator import ScanRunResult

_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
_FORMAT_LABELS: tuple[tuple[str, str], ...] = (
    ("json", "Exporter JSON"),
    ("markdown", "Exporter Markdown"),
    ("html", "Exporter HTML"),
)


class ScanResultsScreen(OmegaScreen):
    """Resultats d'un scan termine, avec export de rapport."""

    def __init__(
        self, *, result: ScanRunResult, prepared: PreparedScan, container: AppContainer
    ) -> None:
        super().__init__()
        self._result = result
        self._prepared = prepared
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static("RESULTATS DU SCAN", classes="omega-title")

            stats = self._result.statistics
            yield Static(f"Statut : {self._result.scan.status.value}", classes="omega-subtitle")
            yield Static(
                f"Requetes : {stats.total_requests} "
                f"(decouverte {stats.discovery_requests}, test {stats.test_requests}) — "
                f"Tests executes : {stats.tests_executed} — "
                f"Findings : {len(self._result.findings)}"
            )

            yield DataTable(id="findings-table")

            yield Static("Theme d'export (HTML)", classes="omega-subtitle")
            yield Select(
                [(name, name) for name in sorted(EXPORT_PALETTES)],
                value=DEFAULT_EXPORT_THEME,
                id="export-theme-select",
            )

            with Horizontal(classes="omega-actions"):
                for format_name, label in _FORMAT_LABELS:
                    with Container(classes="omega-btn-frame"):
                        yield Button(label, id=f"export-{format_name}")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour au menu", id="home")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#findings-table", DataTable)
        table.add_columns("Severite", "Type", "Endpoint", "Parametre", "Titre")
        findings = sorted(
            self._result.findings, key=lambda finding: _SEVERITY_ORDER[finding.severity.value]
        )
        for finding in findings:
            table.add_row(
                finding.severity.value,
                finding.type,
                finding.target.endpoint,
                finding.target.parameter or "",
                finding.title,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "home":
            # Bug reel rapporte (ecran vide, ctrl+q necessaire pour quitter) :
            # `screen_stack` porte l'ecran par defaut IMPLICITE de Textual en
            # position 0 (jamais compose, jamais visible), HomeScreen en
            # position 1 (seul ecran pousse par app.py::_show_home(), jamais
            # remplace/deplace ensuite) — vider jusqu'a longueur 1 (comme un
            # premier essai le faisait) depile aussi HomeScreen et laisse cet
            # ecran par defaut vide affiche a sa place. Longueur 2 = retour a
            # HomeScreen exactement.
            while len(self.app.screen_stack) > 2:
                self.app.pop_screen()
            return
        if event.button.id and event.button.id.startswith("export-"):
            self._export(event.button.id.removeprefix("export-"))

    def _export(self, format_name: str) -> None:
        termination = self._result.scan.termination_reason
        assert termination is not None  # toujours renseigne en sortie de run_scan (Phase 10a)

        report = build_scan_report(
            scan=self._result.scan,
            target_url=self._prepared.entry_url.to_str(),
            version=__version__,
            configuration=self._prepared.configuration,
            termination=termination,
            tests=self._result.tests,
            findings=self._result.findings,
            statistics=self._result.statistics,
            catalog_versions=self._container.catalog_versions,
            verify_tls=self._prepared.verify_tls,
            now=self._container.clock.now(),
        )
        output_dir = resolve_exports_dir(
            settings_store=self._container.settings_store,
            default_exports_dir=self._container.default_exports_dir,
        )
        theme_name = str(self.query_one("#export-theme-select", Select).value)
        output_paths = export_report(
            report=report,
            formats=(format_name,),
            output_dir=output_dir,
            report_exporter=self._container.report_exporter,
            theme_name=theme_name,
        )
        self.app.notify(f"Rapport {format_name} : {output_paths[0]}", title="Export termine")
