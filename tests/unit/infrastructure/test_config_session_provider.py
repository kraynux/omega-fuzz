# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from omega_fuzz.core.errors import DependencyError
from omega_fuzz.domain.auth.auth_context import AuthContext, AuthMode
from omega_fuzz.infrastructure.configuration.config_session_provider import ConfigSessionProvider
from omega_fuzz.infrastructure.network.httpx_http_client import HttpxHttpClient


async def test_none_mode_returns_empty_session() -> None:
    session = await ConfigSessionProvider(AuthContext(mode=AuthMode.NONE)).get_session()
    assert dict(session.cookies) == {}
    assert dict(session.headers) == {}


async def test_cookie_mode_returns_session_with_cookie() -> None:
    context = AuthContext(mode=AuthMode.COOKIE, cookie="abc123")
    session = await ConfigSessionProvider(context).get_session()
    assert dict(session.cookies) == {"session": "abc123"}


async def test_bearer_token_mode_returns_authorization_header() -> None:
    context = AuthContext(mode=AuthMode.BEARER_TOKEN, bearer_token="tok-xyz")
    session = await ConfigSessionProvider(context).get_session()
    assert dict(session.headers) == {"Authorization": "Bearer tok-xyz"}


async def test_login_form_without_http_client_raises() -> None:
    context = AuthContext(
        mode=AuthMode.LOGIN_FORM,
        login_url="https://example.com/login",
        username_field="user",
        password_field="pass",
        username="alice",
        password="secret",
    )
    with pytest.raises(DependencyError):
        await ConfigSessionProvider(context).get_session()


_LOGIN_CALL_COUNT = {"count": 0}


class _LoginHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_POST(self) -> None:
        _LOGIN_CALL_COUNT["count"] += 1
        self.send_response(200)
        self.send_header("Set-Cookie", "sessionid=abc123; Path=/; HttpOnly")
        self.end_headers()
        self.wfile.write(b"ok")


@pytest.fixture
def login_server() -> Iterator[ThreadingHTTPServer]:
    _LOGIN_CALL_COUNT["count"] = 0
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _LoginHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd
    finally:
        httpd.shutdown()
        thread.join()


async def test_login_form_performs_real_post_and_extracts_cookie(
    login_server: ThreadingHTTPServer,
) -> None:
    port = login_server.server_address[1]
    context = AuthContext(
        mode=AuthMode.LOGIN_FORM,
        login_url=f"http://127.0.0.1:{port}/login",
        username_field="user",
        password_field="pass",
        username="alice",
        password="secret",
    )
    provider = ConfigSessionProvider(context, http_client=HttpxHttpClient())

    session = await provider.get_session()

    assert dict(session.cookies) == {"sessionid": "abc123"}
    assert _LOGIN_CALL_COUNT["count"] == 1


async def test_login_form_session_is_cached_across_calls(
    login_server: ThreadingHTTPServer,
) -> None:
    port = login_server.server_address[1]
    context = AuthContext(
        mode=AuthMode.LOGIN_FORM,
        login_url=f"http://127.0.0.1:{port}/login",
        username_field="user",
        password_field="pass",
        username="alice",
        password="secret",
    )
    provider = ConfigSessionProvider(context, http_client=HttpxHttpClient())

    await provider.get_session()
    await provider.get_session()

    assert _LOGIN_CALL_COUNT["count"] == 1
