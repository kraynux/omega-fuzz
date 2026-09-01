# Copyright (c) 2026 kraynux - Licence MIT
"""Verifie la sous-commande `scan` (Phase 10b) : `--dry-run` n'emet
aucune requete (meme garantie structurelle que `prepare_scan`,
Phase 6) et une configuration incomplete (ni preset, ni combinaison
manuelle complete) renvoie une erreur claire, code de sortie
`CLI_EXIT_ERROR`, jamais une trace brute — via `interfaces.cli.main.run`,
le point d'entree reel qui capture les erreurs."""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from omega_fuzz.app.container import Container, ScanRuntime
from omega_fuzz.core.constants import CLI_EXIT_ERROR, CLI_EXIT_OK
from omega_fuzz.domain.auth.auth_context import AuthContext, AuthMode
from omega_fuzz.domain.auth.session import Session
from omega_fuzz.interfaces.cli.commands.scan_command import run as run_scan_command
from omega_fuzz.interfaces.cli.main import run as run_cli
from omega_fuzz.interfaces.cli.parser import build_parser
from omega_fuzz.interfaces.cli.prompts.confirmation_prompt import CliConfirmationPrompt

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


class _AssertNeverCalledHttpClient:
    async def send(self, **_kwargs: Any) -> Any:
        raise AssertionError("--dry-run ne doit emettre aucune requete HTTP")


class _NullUrlDiscoverer:
    def discover_urls(self, *, base_url: str, html_body: str) -> Sequence[str]:
        raise AssertionError("non attendu en --dry-run")

    def discover_forms(self, *, base_url: str, html_body: str) -> Sequence[Any]:
        raise AssertionError("non attendu en --dry-run")


class _NullResponseAnalyzer:
    def analyze(self, **_kwargs: Any) -> Sequence[Any]:
        raise AssertionError("non attendu en --dry-run")


class _NullTestPlanGenerator:
    def generate_for_url(self, **_kwargs: Any) -> Sequence[Any]:
        raise AssertionError("non attendu en --dry-run")


class _NullScanRepository:
    def save(self, scan: Any) -> None:
        raise AssertionError("non attendu en --dry-run")

    def get(self, scan_id: str) -> Any:
        return None

    def list_history(self) -> Sequence[Any]:
        return ()

    def clear(self) -> None:
        pass

    def save_state(self, state: Any) -> None:
        raise AssertionError("non attendu en --dry-run")

    def get_state(self, scan_id: str) -> Any:
        return None


class _NullFindingRepository:
    def save(self, finding: Any) -> None:
        raise AssertionError("non attendu en --dry-run")

    def list_for_scan(self, scan_id: str) -> Sequence[Any]:
        return ()

    def clear_for_scan(self, scan_id: str) -> None:
        pass


class _NullReportExporter:
    def export(self, *, report: Any, format_name: str, output_path: Path) -> None:
        raise AssertionError("non attendu en --dry-run")


class _FixedClock:
    def now(self) -> datetime:
        return _NOW


class _NullLogger:
    def info(self, event: str, **fields: Any) -> None:
        pass

    def warning(self, event: str, **fields: Any) -> None:
        pass

    def error(self, event: str, **fields: Any) -> None:
        pass


class _FixedIdGenerator:
    def new_scan_id(self) -> str:
        return "fixed-scan-id"


class _NullSessionProvider:
    async def get_session(self) -> Session:
        return Session()


class _NullSettingsStore:
    def get(self, key: str, default: str | None = None) -> str | None:
        return default

    def set(self, key: str, value: str) -> None:
        raise AssertionError("non attendu en --dry-run")

    def all(self) -> dict[str, str]:
        return {}


class _NullTargetRepository:
    def add(self, url: str) -> None:
        raise AssertionError("non attendu en --dry-run")

    def remove(self, url: str) -> None:
        raise AssertionError("non attendu en --dry-run")

    def list_all(self) -> list[str]:
        return []


def _container() -> Container:
    return Container(
        clock=_FixedClock(),
        id_generator=_FixedIdGenerator(),
        terminal_detector=None,  # type: ignore[arg-type]  # jamais consomme par `scan`
        http_client=_AssertNeverCalledHttpClient(),
        url_discoverer=_NullUrlDiscoverer(),
        response_analyzer=_NullResponseAnalyzer(),
        security_headers_analyzer=_NullResponseAnalyzer(),
        test_plan_generator=_NullTestPlanGenerator(),
        scan_repository=_NullScanRepository(),
        finding_repository=_NullFindingRepository(),
        report_exporter=_NullReportExporter(),
        logger=_NullLogger(),
        catalog_versions={},
        settings_store=_NullSettingsStore(),
        default_exports_dir=Path("/tmp/omega-fuzz-test-exports"),
        target_repository=_NullTargetRepository(),
        default_screenshots_dir=Path("/tmp/omega-fuzz-test-screenshots"),
    )


def _scan_runtime() -> ScanRuntime:
    return ScanRuntime(
        auth_context=AuthContext(mode=AuthMode.NONE),
        session_provider=_NullSessionProvider(),
        confirmation_provider=CliConfirmationPrompt(),
    )


def test_dry_run_never_emits_a_request(capsys: pytest.CaptureFixture[str]) -> None:
    args = build_parser().parse_args(
        ["scan", "--target", "https://example.com/", "--preset", "prod-safe", "--dry-run"]
    )

    exit_code = run_scan_command(_container(), args, _scan_runtime())

    assert exit_code == CLI_EXIT_OK
    printed = capsys.readouterr().out
    assert "example.com" in printed


def test_incomplete_configuration_returns_clean_error(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run_cli(
        _container(),
        ["scan", "--target", "https://example.com/"],
        scan_runtime_factory=lambda _auth_config_path: _scan_runtime(),
    )

    assert exit_code == CLI_EXIT_ERROR
    printed_err = capsys.readouterr().err
    assert "Traceback" not in printed_err
    assert "Erreur" in printed_err


def test_invalid_target_returns_clean_error(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run_cli(
        _container(),
        ["scan", "--target", "not a url", "--preset", "prod-safe"],
        scan_runtime_factory=lambda _auth_config_path: _scan_runtime(),
    )

    assert exit_code == CLI_EXIT_ERROR
    printed_err = capsys.readouterr().err
    assert "Traceback" not in printed_err
