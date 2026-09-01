# Copyright (c) 2026 kraynux - Licence MIT
"""Verifie le pipeline bout-en-bout (Phase 10a) sur un site synthetique
reel (meme patron de serveur threade que Phase 4/7) : la decouverte
alimente reellement la generation de tests, un endpoint reflechissant
un parametre de query produit un finding XSS suspecte, et un budget
tres bas (`max_tests=1`) arrete proprement le scan avant d'avoir
traite tous les tests generables."""
from __future__ import annotations

import threading
from collections.abc import Iterator
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest

from omega_fuzz.application.services.scan_orchestrator import run_scan
from omega_fuzz.domain.auth.auth_context import AuthContext, AuthMode
from omega_fuzz.domain.findings.payload_catalog import PayloadCatalog, PayloadEntry
from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
from omega_fuzz.domain.profiles.effective_configuration import EffectiveConfiguration
from omega_fuzz.domain.profiles.limits import Limits
from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName
from omega_fuzz.domain.scans.scan import Scan
from omega_fuzz.domain.scans.scan_id import ScanId
from omega_fuzz.domain.scans.scan_status import ScanStatus
from omega_fuzz.domain.services.url_normalization_service import normalize_url
from omega_fuzz.domain.targets.scope import build_scope
from omega_fuzz.domain.targets.scope_mode import ScopeMode
from omega_fuzz.domain.targets.target import Target
from omega_fuzz.domain.targets.target_id import TargetId, build_target_id
from omega_fuzz.infrastructure.analyzers.response_analyzer import CompositeResponseAnalyzer
from omega_fuzz.infrastructure.configuration.config_session_provider import ConfigSessionProvider
from omega_fuzz.infrastructure.network.bs4_url_discoverer import Bs4UrlDiscoverer
from omega_fuzz.infrastructure.network.httpx_http_client import HttpxHttpClient
from omega_fuzz.plugins.test_plan_generator import CompositeTestPlanGenerator

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


class _FixedClock:
    def now(self) -> datetime:
        return _NOW


class _FakeLogger:
    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict[str, Any]]] = []

    def info(self, event: str, **fields: Any) -> None:
        self.events.append(("info", event, fields))

    def warning(self, event: str, **fields: Any) -> None:
        self.events.append(("warning", event, fields))

    def error(self, event: str, **fields: Any) -> None:
        self.events.append(("error", event, fields))


_XSS_MARKER = "<script>alert('omegafuzz-marker')</script>"
_HOME_PAGE = b"""
<html><body>
<a href="/search?q=x">search</a>
<a href="/about">about</a>
<form action="/filter" method="get">
    <input type="text" name="tag" value="">
</form>
</body></html>
"""
_ABOUT_PAGE = b"<html><body>Page propre, sans parametre.</body></html>"


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        parts = urlsplit(self.path)
        if parts.path == "/":
            self._send_html(_HOME_PAGE)
        elif parts.path == "/about":
            self._send_html(_ABOUT_PAGE)
        elif parts.path == "/search":
            query_value = parse_qs(parts.query).get("q", [""])[0]
            body = f"<html><body>Resultats pour : {query_value}</body></html>".encode()
            self._send_html(body)
        elif parts.path == "/filter":
            tag_value = parse_qs(parts.query).get("tag", [""])[0]
            body = f"<html><body>Filtre : {tag_value}</body></html>".encode()
            self._send_html(body)
        else:
            self.send_response(404)
            self.end_headers()

    def _send_html(self, body: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture
def server() -> Iterator[ThreadingHTTPServer]:
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd
    finally:
        httpd.shutdown()
        thread.join()


def _target(port: int) -> Target:
    entry_url = normalize_url(f"http://127.0.0.1:{port}/")
    scope = build_scope(
        root_host="127.0.0.1",
        mode=ScopeMode.EXACT,
        allowed_schemes=frozenset({"http", "https"}),
        scope_port=port,
        max_depth=2,
    )
    target_id = TargetId(build_target_id(host="127.0.0.1"))
    return Target(target_id=target_id, entry_url=entry_url, scope=scope)


def _configuration(*, limits: Limits) -> EffectiveConfiguration:
    scope = build_scope(
        root_host="127.0.0.1",
        mode=ScopeMode.EXACT,
        allowed_schemes=frozenset({"http", "https"}),
        scope_port=80,
        max_depth=2,
    )
    return EffectiveConfiguration(
        aggressiveness=AggressivenessLevel.STANDARD,
        scope_profile=ScopeProfileName.CUSTOM,
        limits=limits,
        scope=scope,
        requires_confirmation=False,
    )


def _generous_limits() -> Limits:
    return Limits(
        max_duration_seconds=300,
        max_total_requests=1000,
        max_tests=500,
        max_concurrent_requests=2,
        max_requests_per_path=50,
        max_requests_per_param=20,
        max_paths_per_target=100,
        max_params_per_path=10,
        max_errors_before_pause=10,
    )


def _xss_catalog() -> PayloadCatalog:
    return PayloadCatalog(
        category="xss",
        version="1.0.0-test",
        payloads=(PayloadEntry(value=_XSS_MARKER),),
    )


def _scan() -> Scan:
    return Scan(
        scan_id=ScanId("scan-test-10a"),
        target_id="127.0.0.1_root",
        status=ScanStatus.RUNNING,
        created_at=_FixedClock().now(),
        started_at=_FixedClock().now(),
    )


async def test_reflected_xss_produces_a_finding(server: ThreadingHTTPServer) -> None:
    port = server.server_address[1]
    result = await run_scan(
        http_client=HttpxHttpClient(),
        url_discoverer=Bs4UrlDiscoverer(),
        session_provider=ConfigSessionProvider(AuthContext(mode=AuthMode.NONE)),
        response_analyzer=CompositeResponseAnalyzer(),
        security_headers_analyzer=CompositeResponseAnalyzer(),
        test_plan_generator=CompositeTestPlanGenerator(xss_catalog=_xss_catalog()),
        scan=_scan(),
        target=_target(port),
        configuration=_configuration(limits=_generous_limits()),
        clock=_FixedClock(),
        logger=_FakeLogger(),
    )

    assert result.scan.status is ScanStatus.COMPLETED
    assert result.findings
    finding = result.findings[0]
    assert finding.type == "reflected_xss"
    assert finding.target.parameter == "q"
    assert result.statistics.discovery_requests > 0
    assert result.statistics.test_requests > 0
    assert result.statistics.tests_executed >= len(result.tests) - 1  # aborted eventuel exclu


async def test_low_test_budget_stops_before_all_tests_run(server: ThreadingHTTPServer) -> None:
    port = server.server_address[1]
    limits = Limits(
        max_duration_seconds=300,
        max_total_requests=1000,
        max_tests=1,
        max_concurrent_requests=2,
        max_requests_per_path=50,
        max_requests_per_param=20,
        max_paths_per_target=100,
        max_params_per_path=10,
        max_errors_before_pause=10,
    )
    result = await run_scan(
        http_client=HttpxHttpClient(),
        url_discoverer=Bs4UrlDiscoverer(),
        session_provider=ConfigSessionProvider(AuthContext(mode=AuthMode.NONE)),
        response_analyzer=CompositeResponseAnalyzer(),
        security_headers_analyzer=CompositeResponseAnalyzer(),
        test_plan_generator=CompositeTestPlanGenerator(
            xss_catalog=_xss_catalog(),
            injection_catalog=PayloadCatalog(
                category="injection", version="1.0.0-test", payloads=(PayloadEntry(value="' OR 1=1"),)
            ),
        ),
        scan=_scan(),
        target=_target(port),
        configuration=_configuration(limits=limits),
        clock=_FixedClock(),
        logger=_FakeLogger(),
    )

    assert result.scan.status is ScanStatus.COMPLETED_TRUNCATED
    assert result.scan.termination_reason is not None
    assert result.scan.termination_reason.limit_name == "max_tests"
    assert len(result.tests) == 1


class _RecordingHttpClient:
    """Enveloppe `HttpxHttpClient` pour verifier que `verify_tls` est
    bien propage par `run_scan` jusqu'a chaque appel `send()` (gap
    corrige en Phase 10b — aucun orchestrateur ne le transmettait)."""

    def __init__(self) -> None:
        self._delegate = HttpxHttpClient()
        self.received_verify_tls: list[bool] = []

    async def send(self, *, verify_tls: bool = True, **kwargs: Any) -> Any:
        self.received_verify_tls.append(verify_tls)
        return await self._delegate.send(verify_tls=verify_tls, **kwargs)


async def test_verify_tls_false_propagates_to_every_http_call(server: ThreadingHTTPServer) -> None:
    port = server.server_address[1]
    http_client = _RecordingHttpClient()

    await run_scan(
        http_client=http_client,
        url_discoverer=Bs4UrlDiscoverer(),
        session_provider=ConfigSessionProvider(AuthContext(mode=AuthMode.NONE)),
        response_analyzer=CompositeResponseAnalyzer(),
        security_headers_analyzer=CompositeResponseAnalyzer(),
        test_plan_generator=CompositeTestPlanGenerator(xss_catalog=_xss_catalog()),
        scan=_scan(),
        target=_target(port),
        configuration=_configuration(limits=_generous_limits()),
        clock=_FixedClock(),
        logger=_FakeLogger(),
        verify_tls=False,
    )

    assert http_client.received_verify_tls
    assert all(value is False for value in http_client.received_verify_tls)


async def test_discovered_get_form_is_fuzzed(server: ThreadingHTTPServer) -> None:
    port = server.server_address[1]
    result = await run_scan(
        http_client=HttpxHttpClient(),
        url_discoverer=Bs4UrlDiscoverer(),
        session_provider=ConfigSessionProvider(AuthContext(mode=AuthMode.NONE)),
        response_analyzer=CompositeResponseAnalyzer(),
        security_headers_analyzer=CompositeResponseAnalyzer(),
        test_plan_generator=CompositeTestPlanGenerator(),
        scan=_scan(),
        target=_target(port),
        configuration=_configuration(limits=_generous_limits()),
        clock=_FixedClock(),
        logger=_FakeLogger(),
    )

    form_tests = [
        test
        for test in result.tests
        if test.module == "fuzzhttp" and test.subtype == "form_parameter"
    ]
    assert form_tests
    assert form_tests[0].target.parameters == ("tag",)
    assert all(test.requests_count > 0 for test in form_tests)
