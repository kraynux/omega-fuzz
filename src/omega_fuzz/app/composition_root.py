# Copyright (c) 2026 kraynux - Licence MIT
"""Construit les adaptateurs concrets et le Container
(OMEGA-FUZZ_ARBORESCENCE.md §4.3). Seul module autorise a importer a la
fois infrastructure/ ET app/container.py.

Phase 10b : cable les adaptateurs reels (reseau, decouverte, analyse,
generation de plans, stockage, export, logs) independants des arguments
d'un scan particulier. `session_provider`/`confirmation_provider`
restent construits par la commande CLI (dependent de `--auth-config`/
d'une interaction terminal, pas de dependances globales).

Stockage par defaut : `./var/` relatif au repertoire courant d'execution
(`infrastructure.config.paths`, porte depuis omega-check D-007/D-008) —
corrige un `~/.omega-fuzz/` invente en Phase 10b sans avoir verifie la
convention deja etablie par le reste de la suite (bug reel rapporte :
"ou va l'export ? pas de dossier var/export").

Deux `CompositeResponseAnalyzer` distincts (trouve par smoke-test
manuel, voir `application.services.scan_orchestrator`) : `response_analyzer`
(sans `security_headers_catalog`) pour XSS/injection, jamais partage
avec le test dedie aux headers de securite (`security_headers_analyzer`)
— sinon chaque reponse XSS/injection generait aussi une observation
« header manquant » qui ecrasait le titre du finding reel.

Phase 10c : `+ settings_store` et `console_logging` (transmis a
`StdlibLogger`) — `False` sous le TUI, Textual controle l'ecran en mode
alternatif.

Phase 10j : `+ target_repository` (cibles favorites, `var/targets.json`)."""
from __future__ import annotations

from pathlib import Path

from omega_lib.infrastructure.terminal.detector import SystemTerminalDetector

from omega_fuzz.app.container import Container, ScanRuntime
from omega_fuzz.domain.auth.auth_context import AuthContext, AuthMode
from omega_fuzz.infrastructure.analyzers.response_analyzer import CompositeResponseAnalyzer
from omega_fuzz.infrastructure.clock import SystemClock
from omega_fuzz.infrastructure.config import paths
from omega_fuzz.infrastructure.configuration.auth_config_loader import load_auth_context
from omega_fuzz.infrastructure.configuration.config_session_provider import ConfigSessionProvider
from omega_fuzz.infrastructure.exporters.html_exporter.html_exporter import HtmlReportExporter
from omega_fuzz.infrastructure.exporters.json_exporter import JsonReportExporter
from omega_fuzz.infrastructure.exporters.markdown_exporter import MarkdownReportExporter
from omega_fuzz.infrastructure.exporters.report_exporter import CompositeReportExporter
from omega_fuzz.infrastructure.ids import SystemIdGenerator
from omega_fuzz.infrastructure.logging import StdlibLogger
from omega_fuzz.infrastructure.network.bs4_url_discoverer import Bs4UrlDiscoverer
from omega_fuzz.infrastructure.network.httpx_http_client import HttpxHttpClient
from omega_fuzz.infrastructure.payloads.payload_loader import (
    load_payload_catalog,
    load_security_headers_catalog,
)
from omega_fuzz.infrastructure.storage.files.json_settings_store import JsonSettingsStore
from omega_fuzz.infrastructure.storage.files.json_target_repository import JsonTargetRepository
from omega_fuzz.infrastructure.storage.sqlite.connection import open_connection
from omega_fuzz.infrastructure.storage.sqlite.finding_repository import SqliteFindingRepository
from omega_fuzz.infrastructure.storage.sqlite.scan_repository import SqliteScanRepository
from omega_fuzz.interfaces.cli.prompts.confirmation_prompt import CliConfirmationPrompt
from omega_fuzz.interfaces.tui.prompts.already_confirmed import AlreadyConfirmedProvider
from omega_fuzz.plugins.test_plan_generator import CompositeTestPlanGenerator
from omega_fuzz.ports.http_client import HttpClient
from omega_fuzz.ports.url_discoverer import UrlDiscoverer

_CATALOGS_DIR = (
    Path(__file__).resolve().parent.parent / "infrastructure" / "payloads" / "catalogs"
)


def build_container(*, var_dir: Path | None = None, console_logging: bool = True) -> Container:
    xss_catalog = load_payload_catalog(_CATALOGS_DIR / "xss.yaml", category="xss")
    injection_catalog = load_payload_catalog(_CATALOGS_DIR / "injection.yaml", category="injection")
    headers_catalog = load_security_headers_catalog(_CATALOGS_DIR / "headers.yaml")

    base_dir = var_dir if var_dir is not None else paths.resolve_var_dir()
    connection = open_connection(paths.default_db_path(base_dir))

    http_client: HttpClient = HttpxHttpClient()
    url_discoverer: UrlDiscoverer = Bs4UrlDiscoverer()

    return Container(
        clock=SystemClock(),
        id_generator=SystemIdGenerator(),
        terminal_detector=SystemTerminalDetector(),
        http_client=http_client,
        url_discoverer=url_discoverer,
        response_analyzer=CompositeResponseAnalyzer(),
        security_headers_analyzer=CompositeResponseAnalyzer(security_headers_catalog=headers_catalog),
        test_plan_generator=CompositeTestPlanGenerator(
            xss_catalog=xss_catalog,
            injection_catalog=injection_catalog,
            security_headers_catalog=headers_catalog,
        ),
        scan_repository=SqliteScanRepository(connection),
        finding_repository=SqliteFindingRepository(connection),
        report_exporter=CompositeReportExporter(
            json_exporter=JsonReportExporter(),
            markdown_exporter=MarkdownReportExporter(),
            html_exporter=HtmlReportExporter(),
        ),
        logger=StdlibLogger(console=console_logging),
        catalog_versions={
            "xss": xss_catalog.version,
            "injection": injection_catalog.version,
            "headers": headers_catalog.version,
        },
        settings_store=JsonSettingsStore(paths.default_settings_path(base_dir)),
        default_exports_dir=paths.default_exports_dir(base_dir),
        target_repository=JsonTargetRepository(paths.default_targets_path(base_dir)),
        default_screenshots_dir=paths.default_screenshots_dir(base_dir),
    )


def _resolve_auth_context(auth_config_path: Path | None) -> AuthContext:
    return (
        load_auth_context(auth_config_path)
        if auth_config_path is not None
        else AuthContext(mode=AuthMode.NONE)
    )


def build_scan_runtime(auth_config_path: Path | None, *, container: Container) -> ScanRuntime:
    """Adaptateurs propres a un scan (dependent de `--auth-config`/
    d'une interaction terminal), construits a chaque invocation de la
    sous-commande `scan` CLI — jamais dans `build_container`. Reutilise
    `container.http_client` pour l'eventuelle requete POST du mode
    `login_form` (`ConfigSessionProvider`, Phase 7c) plutot que d'en
    construire un second."""
    auth_context = _resolve_auth_context(auth_config_path)
    return ScanRuntime(
        auth_context=auth_context,
        session_provider=ConfigSessionProvider(auth_context, http_client=container.http_client),
        confirmation_provider=CliConfirmationPrompt(),
    )


def build_tui_scan_runtime(auth_config_path: Path | None, *, container: Container) -> ScanRuntime:
    """Variante TUI de `build_scan_runtime` (Phase 10d) : seule
    difference, `AlreadyConfirmedProvider` au lieu de
    `CliConfirmationPrompt` — la confirmation renforcee se fait dans
    `interfaces/tui/screens/scan_review_screen.py` (widgets Textual),
    jamais via un `ConfirmationProvider.confirm()` bloquant (`input()`),
    incompatible avec le modele callback/push_screen() du TUI."""
    auth_context = _resolve_auth_context(auth_config_path)
    return ScanRuntime(
        auth_context=auth_context,
        session_provider=ConfigSessionProvider(auth_context, http_client=container.http_client),
        confirmation_provider=AlreadyConfirmedProvider(),
    )
