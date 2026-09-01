# Copyright (c) 2026 kraynux - Licence MIT
"""Regroupe les dependances resolues (OMEGA-FUZZ_ARBORESCENCE.md §4.3) —
consomme uniquement par app/composition_root.py et par interfaces/ (sous
TYPE_CHECKING uniquement, jamais a l'execution).

Phase 10b : etendu avec les adaptateurs independants des arguments d'un
scan particulier (reseau/decouverte/analyse/generation de plans/
stockage/export/logs). `session_provider` (depend de `--auth-config`,
un argument CLI) et `confirmation_provider` (interaction terminal, vit
dans `interfaces/cli/prompts/`) restent construits par la commande CLI
elle-meme, pas ici.

Phase 10c : `+ settings_store`, partage par la CLI (aucun usage pour
l'instant) et le TUI (theme actif, profil de rendu — voir interfaces/tui/).

Phase 10f : `+ default_exports_dir` (`./var/exports/` par defaut,
`infrastructure.config.paths`, corrige un `~/.omega-fuzz/` invente sans
verifier la convention deja etablie par le reste de la suite).

Phase 10j : `+ target_repository` (cibles favorites, ecran Cibles).

Phase 10k : `+ default_screenshots_dir` (`./var/screenshots/` par
defaut, meme patron que `default_exports_dir`)."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from omega_fuzz.domain.auth.auth_context import AuthContext
from omega_fuzz.ports.clock import Clock
from omega_fuzz.ports.confirmation_provider import ConfirmationProvider
from omega_fuzz.ports.finding_repository import FindingRepository
from omega_fuzz.ports.http_client import HttpClient
from omega_fuzz.ports.id_generator import IdGenerator
from omega_fuzz.ports.logger import Logger
from omega_fuzz.ports.report_exporter import ReportExporter
from omega_fuzz.ports.response_analyzer import ResponseAnalyzer
from omega_fuzz.ports.scan_repository import ScanRepository
from omega_fuzz.ports.session_provider import SessionProvider
from omega_fuzz.ports.settings_store import SettingsStore
from omega_fuzz.ports.target_repository import TargetRepository
from omega_fuzz.ports.terminal_detector import TerminalDetector
from omega_fuzz.ports.test_plan_generator import TestPlanGenerator
from omega_fuzz.ports.url_discoverer import UrlDiscoverer


@dataclass
class Container:
    clock: Clock
    id_generator: IdGenerator
    terminal_detector: TerminalDetector
    http_client: HttpClient
    url_discoverer: UrlDiscoverer
    response_analyzer: ResponseAnalyzer
    security_headers_analyzer: ResponseAnalyzer
    test_plan_generator: TestPlanGenerator
    scan_repository: ScanRepository
    finding_repository: FindingRepository
    report_exporter: ReportExporter
    logger: Logger
    catalog_versions: Mapping[str, str]
    settings_store: SettingsStore
    default_exports_dir: Path
    target_repository: TargetRepository
    default_screenshots_dir: Path


@dataclass
class ScanRuntime:
    """Adaptateurs propres a un scan particulier (dependent de
    `--auth-config`/d'une interaction terminal) — construits par
    `app.composition_root.build_scan_runtime`, jamais par `Container`
    (partage entre toutes les commandes)."""

    auth_context: AuthContext
    session_provider: SessionProvider
    confirmation_provider: ConfirmationProvider
