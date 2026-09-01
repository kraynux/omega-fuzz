# Copyright (c) 2026 kraynux - Licence MIT
"""Serveur de test threade (meme patron que Phase 4) — verifie
l'execution reelle d'un `Test` genere par un fuzzer de Phase 7a a
travers `application.services.test_orchestrator.run_test`."""
from __future__ import annotations

import threading
from collections.abc import Iterator
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest

from omega_fuzz.application.services.test_orchestrator import run_test
from omega_fuzz.domain.profiles.limits import Limits
from omega_fuzz.domain.tests.test_status import TestStatus
from omega_fuzz.infrastructure.network.httpx_http_client import HttpxHttpClient
from omega_fuzz.plugins.fuzzers.query_parameter_fuzzer import build_plan


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        if self.path.startswith("/broken"):
            self.send_response(500)
        else:
            self.send_response(200)
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


def _limits(**overrides: int) -> Limits:
    defaults: dict[str, int] = {
        "max_duration_seconds": 300,
        "max_total_requests": 1000,
        "max_tests": 500,
        "max_concurrent_requests": 2,
        "max_requests_per_path": 50,
        "max_requests_per_param": 20,
        "max_paths_per_target": 100,
        "max_params_per_path": 10,
        "max_errors_before_pause": 10,
    }
    defaults.update(overrides)
    return Limits(**defaults)


async def test_test_completes_successfully_against_ok_endpoint(
    server: ThreadingHTTPServer,
) -> None:
    port = server.server_address[1]
    test, requests = build_plan(
        target_short="example_root",
        sequence=1,
        url=f"http://127.0.0.1:{port}/ok?q=hello",
        parameter_name="q",
        now=_FakeClock().now(),
    )

    updated_test, stats = await run_test(
        http_client=HttpxHttpClient(),
        test=test,
        requests=requests,
        limits=_limits(),
        clock=_FakeClock(),
        logger=_FakeLogger(),
    )

    assert updated_test.status is TestStatus.COMPLETED
    assert updated_test.requests_count == len(requests)
    assert updated_test.errors_count == 0
    assert stats.test_requests == len(requests)
    assert stats.total_requests == len(requests)
    assert stats.tests_executed == 1


async def test_test_stops_cleanly_when_budget_exhausted(server: ThreadingHTTPServer) -> None:
    port = server.server_address[1]
    test, requests = build_plan(
        target_short="example_root",
        sequence=1,
        url=f"http://127.0.0.1:{port}/ok?q=hello",
        parameter_name="q",
        now=_FakeClock().now(),
    )
    assert len(requests) > 3

    updated_test, stats = await run_test(
        http_client=HttpxHttpClient(),
        test=test,
        requests=requests,
        limits=_limits(max_total_requests=3),
        clock=_FakeClock(),
        logger=_FakeLogger(),
    )

    assert updated_test.status is TestStatus.ABORTED
    assert updated_test.requests_count == 3
    assert stats.total_requests == 3


async def test_5xx_responses_are_counted_as_errors_without_stopping(
    server: ThreadingHTTPServer,
) -> None:
    port = server.server_address[1]
    test, requests = build_plan(
        target_short="example_root",
        sequence=1,
        url=f"http://127.0.0.1:{port}/broken?q=hello",
        parameter_name="q",
        now=_FakeClock().now(),
    )

    updated_test, _stats = await run_test(
        http_client=HttpxHttpClient(),
        test=test,
        requests=requests,
        limits=_limits(),
        clock=_FakeClock(),
        logger=_FakeLogger(),
    )

    assert updated_test.status is TestStatus.COMPLETED
    assert updated_test.errors_count == len(requests)
    assert updated_test.requests_count == len(requests)
