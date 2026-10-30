# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran de detail d'un scan passe (Phase 10h) : statut, dates, raison de
terminaison, findings. Pas de bouton d'export ici (contrairement a
scan_results_screen.py) : `build_scan_report` exige une
`EffectiveConfiguration` et des `Test` — aucun des deux n'est persiste
pour un scan recharge (seuls `Scan` et `Finding` le sont, Phase 9b) —
fabriquer des valeurs de substitution produirait un rapport mensonger
(limites/preset inventes).

Phase 10i : bug reel rapporte ("rien ne s'affiche dans le tableau du
bas") — les metadonnees (cible/statut/3 dates/terminaison/avertissement
export) etalees sur jusqu'a 7 lignes + le cadre de `.omega-title`
(bordure + marge) poussaient le tableau des findings hors de la zone
visible sur un terminal de taille courante, meme si les lignes etaient
bien presentes (verifie : `DataTable.row_count`/cellules corrects,
seulement la POSITION du tableau posait probleme). Metadonnees
consolidees sur une seule ligne, avertissement d'export deplace APRES
le tableau (info secondaire, ne doit pas le repousser)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Static

from omega_fuzz.application.queries.list_findings_for_scan import list_findings_for_scan
from omega_fuzz.domain.reports.termination import describe_termination
from omega_fuzz.interfaces.tui.screens._base import OmegaScreen
from omega_fuzz.shared.i18n import _

if TYPE_CHECKING:
    from omega_fuzz.app.container import Container as AppContainer
    from omega_fuzz.domain.scans.scan import Scan

_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class HistoryDetailScreen(OmegaScreen):
    """Detail en lecture seule d'un scan passe."""

    def __init__(self, *, scan: Scan, container: AppContainer) -> None:
        super().__init__()
        self._scan = scan
        self._container = container

    def compose(self) -> ComposeResult:
        scan = self._scan
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static(_("SCAN {value}").format(value=scan.scan_id.value[:12]), classes="omega-title")
            yield Static(
                _("Cible : {target_id} — Statut : {value} — Créé le : {strftime}").format(target_id=scan.target_id, value=scan.status.value, strftime=scan.created_at.strftime('%Y-%m-%d %H:%M')),
                classes="omega-subtitle",
            )

            yield DataTable(id="history-findings-table")

            if scan.termination_reason is not None:
                yield Static(_("Terminaison : {value}").format(value=describe_termination(scan.termination_reason)))
            yield Static(
                _("Export indisponible depuis l'historique : la configuration effective "
                  "(preset/limites) et le détail des tests d'un scan passé ne sont pas "
                  "persistés — seuls le scan et ses findings le sont."),
                classes="omega-hint",
            )

            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#history-findings-table", DataTable)
        table.add_columns(_("Sévérité"), _("Type"), _("Endpoint"), _("Paramètre"), _("Titre"))
        findings = list_findings_for_scan(
            finding_repository=self._container.finding_repository, scan_id=self._scan.scan_id.value
        )
        for finding in sorted(findings, key=lambda f: _SEVERITY_ORDER[f.severity.value]):
            table.add_row(
                finding.severity.value,
                finding.type,
                finding.target.endpoint,
                finding.target.parameter or "",
                _(finding.title),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
