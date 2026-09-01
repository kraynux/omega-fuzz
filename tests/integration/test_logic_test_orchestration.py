# Copyright (c) 2026 kraynux - Licence MIT
"""Serveur de test threade (meme patron que Phase 4/7a/7b) — verifie
l'execution reelle d'un `logic_test` de Phase 7c a travers
`application.services.test_orchestrator.run_logic_test`, y compris que
la session courante est bien appliquee aux requetes emises."""
from __future__ import annotations

import threading
from collections.abc import Iterator
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

import pytest

from omega_fuzz.application.services.test_orchestrator import run_logic_test
from omega_fuzz.domain.auth.session import Session
from omega_fuzz.domain.profiles.limits import Limits
from omega_fuzz.domain.tests.test_result import TestResult
from omega_fuzz.infrastructure.analyzers.access_control_analyzer import HttpAccessControlAnalyzer
from omega_fuzz.infrastructure.network.httpx_http_client import HttpxHttpClient
from omega_fuzz.plugins.logic_tests.authorization_checks import build_plan as build_authz_plan
from omega_fuzz.plugins.logic_tests.idor_checks import build_plan as build_idor_plan


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        parts = urlsplit(self.path)
        cookie_header = self.headers.get("Cookie", "")

        if parts.path == "/orders":
            # Endpoint IDOR-vulnerable : accorde l'acces des qu'une session
            # quelconque est presente, sans verifier a qui appartient la
            # commande demandee.
            if "sessionid=" in cookie_header:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"order data")
            else:
                self.send_response(401)
                self.end_headers()
        elif parts.path == "/admin":
            # Correctement protege : seule la session admin passe.
            if "sessionid=admin" in cookie_header:
                self.send_response(200)
                self.end_headers()
            else:
                self.send_response(403)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


class _OwnerSessionProvider:
    """Implemente ports/session_provider.py::SessionProvider — session
    d'un utilisateur ordinaire, pas administrateur."""

    async def get_session(self) -> Session:
        return Session(cookies={"sessionid": "owner1"})


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


async def test_idor_vulnerable_endpoint_is_suspected(server: ThreadingHTTPServer) -> None:
    port = server.server_address[1]
    test, requests = build_idor_plan(
        target_short="example_root",
        sequence=11,
        url=f"http://127.0.0.1:{port}/orders?order_id=1",
        id_parameter_name="order_id",
        candidate_foreign_values=["2", "3"],
        now=_FakeClock().now(),
    )

    updated_test, stats, observations = await run_logic_test(
        http_client=HttpxHttpClient(),
        session_provider=_OwnerSessionProvider(),
        access_control_analyzer=HttpAccessControlAnalyzer(),
        test=test,
        requests=requests,
        limits=_limits(),
        clock=_FakeClock(),
        logger=_FakeLogger(),
    )

    assert updated_test.result is TestResult.FINDING_SUSPECTED
    assert len(observations) == 2  # les 2 candidats etrangers ont ete acceptes a tort
    assert stats.findings_total >= 1


async def test_properly_protected_admin_endpoint_is_no_finding(
    server: ThreadingHTTPServer,
) -> None:
    port = server.server_address[1]
    test, requests = build_authz_plan(
        target_short="example_root",
        sequence=10,
        protected_url=f"http://127.0.0.1:{port}/admin",
        now=_FakeClock().now(),
    )

    updated_test, _stats, observations = await run_logic_test(
        http_client=HttpxHttpClient(),
        session_provider=_OwnerSessionProvider(),
        access_control_analyzer=HttpAccessControlAnalyzer(),
        test=test,
        requests=requests,
        limits=_limits(),
        clock=_FakeClock(),
        logger=_FakeLogger(),
    )

    assert updated_test.result is TestResult.NO_FINDING
    assert observations == ()


async def test_session_cookie_is_actually_sent(server: ThreadingHTTPServer) -> None:
    """Sans cookie de session, /orders repond 401 — verifie indirectement
    que `run_logic_test` applique bien la session a chaque requete
    emise (sinon le test IDOR-vulnerable ci-dessus renverrait aussi 401,
    pas 200)."""
    port = server.server_address[1]
    test, requests = build_authz_plan(
        target_short="example_root",
        sequence=10,
        protected_url=f"http://127.0.0.1:{port}/orders",
        now=_FakeClock().now(),
    )

    class _NoSession:
        async def get_session(self) -> Session:
            return Session()

    updated_test, _stats, _observations = await run_logic_test(
        http_client=HttpxHttpClient(),
        session_provider=_NoSession(),
        access_control_analyzer=HttpAccessControlAnalyzer(),
        test=test,
        requests=requests,
        limits=_limits(),
        clock=_FakeClock(),
        logger=_FakeLogger(),
        expected_denial_status_codes=(401,),
    )

    assert updated_test.result is TestResult.NO_FINDING  # 401 est bien le refus attendu
