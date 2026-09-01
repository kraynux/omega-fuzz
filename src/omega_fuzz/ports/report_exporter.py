# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'export de rapport (OMEGA-FUZZ_ARBORESCENCE.md §15.3, §23).
Revision Phase 9a : `ReportModel` reel (existe depuis
`domain.reports.report_model`) au lieu du placeholder `Any` de la
Phase 0 — meme moment que les revisions precedentes
(`ScanRepository`/`FindingRepository`). Implementations concretes
(JSON/Markdown/HTML) confinees a `infrastructure.exporters`.

Revision Phase 10f : `+ theme_name` (theme d'export, catalogue
`omega_lib.theme.policies.EXPORT_PALETTES` — bug reel rapporte : "export
pas de theme propose") — sans effet pour JSON/Markdown (pas de notion de
theme visuel), consomme uniquement par l'exporteur HTML."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from omega_fuzz.domain.reports.report_model import ReportModel


class ReportExporter(Protocol):
    def export(
        self,
        *,
        report: ReportModel,
        format_name: str,
        output_path: Path,
        theme_name: str | None = None,
    ) -> None: ...
