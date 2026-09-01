# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/report_exporter.py::ReportExporter pour le format
HTML (OMEGA-FUZZ_SPECIFICATIONS.md §27, OMEGA-FUZZ_ARBORESCENCE.md §23 :
« ne pas recalculer la severite ou les statistiques »). `jinja2` est
confine a cette sous-couche (contrat import-linter dedie).

`autoescape=True` est obligatoire : un `Finding.evidence.evidence_summary`
peut contenir un payload capture tel quel (ex. un payload XSS du
catalogue Phase 7b) — sans echappement automatique, le rapport HTML
lui-meme deviendrait vulnerable au contenu qu'il documente.

Phase 10f : theme d'export (`html_theme_resolver.py`, catalogue
`omega_lib.theme.policies.EXPORT_PALETTES`) — independant du theme
d'interface actif au moment du scan, meme mecanisme que le reste de la
suite (bug reel rapporte : "export pas de theme propose")."""
from __future__ import annotations

from pathlib import Path

import jinja2

from omega_fuzz.domain.reports.report_model import (
    ReportModel,
    count_tests_by_type,
    findings_by_severity,
    requests_by_module,
)
from omega_fuzz.domain.reports.termination import describe_termination
from omega_fuzz.infrastructure.exporters.html_exporter.html_theme_resolver import (
    resolve_export_palette,
)

_TEMPLATES_DIR = Path(__file__).parent / "templates"


class HtmlReportExporter:
    """Implemente ports/report_exporter.py::ReportExporter."""

    def __init__(self) -> None:
        self._environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(_TEMPLATES_DIR)),
            autoescape=True,
        )

    def export(
        self,
        *,
        report: ReportModel,
        format_name: str,
        output_path: Path,
        theme_name: str | None = None,
    ) -> None:
        if format_name != "html":
            raise ValueError(f"format non supporte par HtmlReportExporter : {format_name!r}")

        template = self._environment.get_template("report.html.j2")
        html = template.render(
            header=report.header,
            configuration=report.configuration,
            statistics=report.statistics,
            tests=report.tests,
            findings=report.findings,
            requests_by_module=requests_by_module(report.tests),
            tests_by_type=count_tests_by_type(report.tests),
            severities=findings_by_severity(report.findings),
            termination_sentence=describe_termination(report.termination),
            palette=resolve_export_palette(theme_name),
        )
        output_path.write_text(html, encoding="utf-8")
