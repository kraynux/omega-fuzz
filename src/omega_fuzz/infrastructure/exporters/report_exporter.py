# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/report_exporter.py::ReportExporter en delegant vers
l'exporter concret correspondant au format demande (OMEGA-FUZZ_PLAN_DEV.md
Phase 9 : « les trois formats reposent sur un modele de rapport
commun »)."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omega_fuzz.domain.reports.report_model import ReportModel
    from omega_fuzz.ports.report_exporter import ReportExporter


class CompositeReportExporter:
    """Implemente ports/report_exporter.py::ReportExporter."""

    def __init__(
        self,
        *,
        json_exporter: ReportExporter,
        markdown_exporter: ReportExporter,
        html_exporter: ReportExporter,
    ) -> None:
        self._exporters: dict[str, ReportExporter] = {
            "json": json_exporter,
            "markdown": markdown_exporter,
            "html": html_exporter,
        }

    def export(
        self,
        *,
        report: ReportModel,
        format_name: str,
        output_path: Path,
        theme_name: str | None = None,
    ) -> None:
        exporter = self._exporters.get(format_name)
        if exporter is None:
            raise ValueError(
                f"format non supporte : {format_name!r} (attendu : "
                f"{sorted(self._exporters)})"
            )
        exporter.export(
            report=report, format_name=format_name, output_path=output_path, theme_name=theme_name
        )
