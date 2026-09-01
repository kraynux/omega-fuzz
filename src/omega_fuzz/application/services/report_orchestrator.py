# Copyright (c) 2026 kraynux - Licence MIT
"""Assemblage du modele de rapport (Phase 10a) a partir du resultat
d'un scan termine — reste un assemblage fin de types deja construits
(`domain.reports.report_model`, Phase 9), reutilisable telle quelle par
la future commande `show` de la CLI pour reconstruire un rapport a
partir de donnees persistees (`ScanRepository`/`FindingRepository`).

Phase 10d : `+ export_report`, extrait de `interfaces/cli/commands/
scan_command.py` (boucle d'export identique necessaire cote TUI,
`interfaces/tui/screens/scan_results_screen.py` — evite de dupliquer la
meme logique dans les deux interfaces).

Phase 10f : `+ resolve_exports_dir` — meme raison (CLI et TUI doivent
tous deux respecter la surcharge `exports_dir_override` de l'ecran
Reglages, pas seulement `Container.default_exports_dir`).

Phase 10i : noms de fichier simplifies (bug/demande reels : "annuler la
creation du dossier avec des numeros a outrance... preset-horodatage.html
directement dans var/exports/") — remplace le sous-dossier par
`scan_id` (ex. `var/exports/<uuid>/report.html`) par un fichier plat
`<preset>-<horodatage>.<extension>` directement sous le dossier
d'export, aucune imbrication."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from omega_fuzz.domain.reports.report_model import ReportModel, build_report_header

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from datetime import datetime

    from omega_fuzz.domain.findings.finding import Finding
    from omega_fuzz.domain.profiles.effective_configuration import EffectiveConfiguration
    from omega_fuzz.domain.reports.scan_statistics import ScanStatistics
    from omega_fuzz.domain.reports.termination import TerminationReason
    from omega_fuzz.domain.scans.scan import Scan
    from omega_fuzz.domain.tests.test import Test
    from omega_fuzz.ports.report_exporter import ReportExporter
    from omega_fuzz.ports.settings_store import SettingsStore

_EXTENSION_BY_FORMAT = {"json": "json", "markdown": "md", "html": "html"}
_EXPORTS_DIR_OVERRIDE_KEY = "exports_dir_override"


def build_scan_report(
    *,
    scan: Scan,
    target_url: str,
    version: str,
    configuration: EffectiveConfiguration,
    termination: TerminationReason,
    tests: tuple[Test, ...],
    findings: tuple[Finding, ...],
    statistics: ScanStatistics,
    catalog_versions: Mapping[str, str],
    verify_tls: bool,
    now: datetime,
) -> ReportModel:
    header = build_report_header(
        scan_id=scan.scan_id.value,
        version=version,
        target_url=target_url,
        configuration=configuration,
        catalog_versions=catalog_versions,
        verify_tls=verify_tls,
        now=now,
    )
    return ReportModel(
        header=header,
        configuration=configuration,
        termination=termination,
        statistics=statistics,
        tests=tests,
        findings=findings,
    )


def resolve_exports_dir(*, settings_store: SettingsStore, default_exports_dir: Path) -> Path:
    """Dossier d'export effectif : la surcharge persistee dans l'ecran
    Reglages (`exports_dir_override`) si presente, sinon
    `Container.default_exports_dir` (`./var/exports/` par defaut)."""
    override = settings_store.get(_EXPORTS_DIR_OVERRIDE_KEY, "")
    return Path(override) if override else default_exports_dir


def _export_filename_stem(report: ReportModel) -> str:
    """`<preset>-<horodatage>` (ex. `prod-safe-2026-09-01_14-30-22`) —
    `report.header.preset` vaut deja le nom du preset resolu ou
    "custom" (`build_report_header`), `report.header.generated_at` est
    l'horodatage de generation du rapport. Ecrase silencieusement un
    export precedent avec le meme preset a la meme seconde : compromis
    assume au profit d'un nom simple et lisible, pas un sous-dossier
    par scan_id."""
    timestamp = report.header.generated_at.strftime("%Y-%m-%d_%H-%M-%S")
    return f"{report.header.preset}-{timestamp}"


def export_report(
    *,
    report: ReportModel,
    formats: Sequence[str],
    output_dir: Path,
    report_exporter: ReportExporter,
    theme_name: str | None = None,
) -> tuple[Path, ...]:
    """Exporte `report` dans chaque format demande, sous
    `output_dir/<preset>-<horodatage>.<extension>` — cree `output_dir`
    au besoin, jamais de sous-dossier par scan. `theme_name` (theme
    d'export, Phase 10f) n'a d'effet que sur le format HTML, transmis
    sans condition aux autres exporteurs qui l'ignorent (meme signature
    unifiee pour les trois formats)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = _export_filename_stem(report)
    paths: list[Path] = []
    for format_name in formats:
        output_path = output_dir / f"{stem}.{_EXTENSION_BY_FORMAT[format_name]}"
        report_exporter.export(
            report=report, format_name=format_name, output_path=output_path, theme_name=theme_name
        )
        paths.append(output_path)
    return tuple(paths)
