# Copyright (c) 2026 kraynux - Licence MIT
"""Serveur de test threade (meme patron que Phase 4/7a) — verifie
l'execution reelle d'une signature Phase 7b (`plugins/signatures/`) a
travers `application.services.test_orchestrator.run_signature_test`."""
from __future__ import annotations

import threading
from collections.abc import Iterator
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

from omega_fuzz.application.services.test_orchestrator import run_signature_test
from omega_fuzz.domain.profiles.limits import Limits
from omega_fuzz.domain.tests.test_result import TestResult
from omega_fuzz.infrastructure.analyzers.response_analyzer import CompositeResponseAnalyzer
from omega_fuzz.infrastructure.network.httpx_http_client import HttpxHttpClient
from omega_fuzz.infrastructure.payloads.payload_loader import (
    load_payload_catalog,
    load_security_headers_catalog,
)
from omega_fuzz.plugins.signatures.security_headers_signature import (
    build_plan as build_headers_plan,
)
from omega_fuzz.plugins.signatures.xss_signatures import build_plan as build_xss_plan

_CATALOGS_DIR = Path(__file__).parents[2] / "src/omega_fuzz/infrastructure/payloads/catalogs"

_SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'self'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Strict-Transport-Security": "max-age=63072000",
}


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        parts = urlsplit(self.path)
        if parts.path == "/reflect":
            query = dict(parse_qsl(parts.query, keep_blank_values=True))
            body = f"<html><body>{query.get('q', '')}</body></html>".encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)
        elif parts.path == "/clean":
            self.send_response(200)
            for name, value in _SECURITY_HEADERS.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(b"<html><body>rien a signaler</body></html>")
        elif parts.path == "/no-headers":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html><body>rien a signaler</body></html>")
        else:
            self.send_response(404)
            self.end_headers()


class _FakeClock:
    def now(self) -> datetime:
        return datetime(2026, 1, 1, tzinfo=timezone.utc)


class _FakeLogger:
    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict[str, Any]]] = []

    def info(self, event: str, **fields: Any) -> None:
        self.events.append(("info", event, fields))

    def warning(self, event: str, **fields: Any) -> None:
        self.events.append(("warning", event, fields))

    def error(self, event: str, **fields: Any) -> None:
        self.events.append(("error", event, fields))


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


def _limits() -> Limits:
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


async def test_reflected_xss_is_suspected_against_echoing_endpoint(
    server: ThreadingHTTPServer,
) -> None:
    port = server.server_address[1]
    catalog = load_payload_catalog(_CATALOGS_DIR / "xss.yaml", category="xss")
    test, requests = build_xss_plan(
        target_short="example_root",
        sequence=1,
        url=f"http://127.0.0.1:{port}/reflect?q=hello",
        parameter_name="q",
        catalog=catalog,
        now=_FakeClock().now(),
    )

    updated_test, stats, observations = await run_signature_test(
        http_client=HttpxHttpClient(),
        response_analyzer=CompositeResponseAnalyzer(),
        test=test,
        requests=requests,
        limits=_limits(),
        clock=_FakeClock(),
        logger=_FakeLogger(),
    )

    assert updated_test.result is TestResult.FINDING_SUSPECTED
    assert any(o.kind == "reflection" for o in observations)
    assert stats.findings_total >= 1


async def test_clean_endpoint_with_all_security_headers_is_no_finding(
    server: ThreadingHTTPServer,
) -> None:
    port = server.server_address[1]
    headers_catalog = load_security_headers_catalog(_CATALOGS_DIR / "headers.yaml")
    test, requests = build_headers_plan(
        target_short="example_root",
        sequence=1,
        url=f"http://127.0.0.1:{port}/clean",
        now=_FakeClock().now(),
    )

    updated_test, _stats, observations = await run_signature_test(
        http_client=HttpxHttpClient(),
        response_analyzer=CompositeResponseAnalyzer(security_headers_catalog=headers_catalog),
        test=test,
        requests=requests,
        limits=_limits(),
        clock=_FakeClock(),
        logger=_FakeLogger(),
    )

    assert updated_test.result is TestResult.NO_FINDING
    assert observations == ()


async def test_missing_security_headers_are_reported(server: ThreadingHTTPServer) -> None:
    port = server.server_address[1]
    headers_catalog = load_security_headers_catalog(_CATALOGS_DIR / "headers.yaml")
    test, requests = build_headers_plan(
        target_short="example_root",
        sequence=1,
        url=f"http://127.0.0.1:{port}/no-headers",
        now=_FakeClock().now(),
    )

    updated_test, _stats, observations = await run_signature_test(
        http_client=HttpxHttpClient(),
        response_analyzer=CompositeResponseAnalyzer(security_headers_catalog=headers_catalog),
        test=test,
        requests=requests,
        limits=_limits(),
        clock=_FakeClock(),
        logger=_FakeLogger(),
    )

    assert updated_test.result is TestResult.FINDING_SUSPECTED
    assert len(observations) == len(headers_catalog.required_headers)
    assert all(o.kind == "missing_security_header" for o in observations)
