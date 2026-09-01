# Copyright (c) 2026 kraynux - Licence MIT
"""Serveur de test threade (decision Q de la passe de coherence : un
serveur single-thread bloquerait/fausserait des scenarios necessitant
plusieurs requetes) — verifie la resilience reseau et la troncature de
`HttpxHttpClient`."""
from __future__ import annotations

import threading
import time
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from omega_fuzz.core.version import __version__
from omega_fuzz.infrastructure.network.httpx_http_client import HttpxHttpClient

_HUGE_CHUNK = b"x" * 1_000_000  # 1 Mo par ecriture


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        if self.path == "/slow":
            time.sleep(2)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"too late")
        elif self.path == "/big":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"x" * 1000)
        elif self.path == "/huge":
            # Simule un fichier volumineux (ISO, etc.) : 50 Mo au total,
            # ecrits par petits blocs avec une pause — verifie que le
            # client coupe la connexion des que son plafond est atteint
            # plutot que de telecharger l'integralite en memoire (bug
            # reel rapporte, voir infrastructure/network/httpx_http_client.py).
            self.send_response(200)
            self.end_headers()
            try:
                for _ in range(50):
                    self.wfile.write(_HUGE_CHUNK)
                    time.sleep(0.01)
            except (BrokenPipeError, ConnectionResetError):
                pass
        elif self.path == "/echo-user-agent":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(self.headers.get("User-Agent", "").encode())
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")


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


async def test_slow_response_times_out_as_soft_failure(server: ThreadingHTTPServer) -> None:
    port = server.server_address[1]
    client = HttpxHttpClient()
    response = await client.send(
        method="GET", url=f"http://127.0.0.1:{port}/slow", timeout=0.2
    )
    assert response.status_code == 0
    assert response.fetch_error is not None


async def test_connection_refused_is_a_soft_failure() -> None:
    client = HttpxHttpClient()
    response = await client.send(method="GET", url="http://127.0.0.1:1/", timeout=1.0)
    assert response.status_code == 0
    assert response.fetch_error is not None


async def test_response_body_truncated_beyond_max_size(server: ThreadingHTTPServer) -> None:
    port = server.server_address[1]
    client = HttpxHttpClient()
    response = await client.send(
        method="GET", url=f"http://127.0.0.1:{port}/big", max_response_body_size=100
    )
    assert response.status_code == 200
    assert response.truncated is True
    assert len(response.body) == 100


async def test_response_not_truncated_when_within_limit(server: ThreadingHTTPServer) -> None:
    port = server.server_address[1]
    client = HttpxHttpClient()
    response = await client.send(
        method="GET", url=f"http://127.0.0.1:{port}/", max_response_body_size=1000
    )
    assert response.status_code == 200
    assert response.truncated is False
    assert response.body == b"ok"


async def test_large_response_never_fully_buffered(server: ThreadingHTTPServer) -> None:
    """Bug reel rapporte (consommation memoire ~6.5 Go sur un dossier
    contenant des ISOs de plusieurs Go) : `/huge` sert 50 Mo, plafond a
    1 Mo — la connexion doit etre coupee bien avant la fin des 50
    iterations de 0.01s (0.5s au total si tout etait lu), jamais apres
    avoir lu plus que le plafond configure."""
    port = server.server_address[1]
    client = HttpxHttpClient()
    started_at = time.monotonic()
    response = await client.send(
        method="GET",
        url=f"http://127.0.0.1:{port}/huge",
        timeout=5.0,
        max_response_body_size=1_000_000,
    )
    elapsed = time.monotonic() - started_at
    assert response.status_code == 200
    assert response.truncated is True
    assert len(response.body) == 1_000_000
    assert elapsed < 0.4  # tres inferieur aux ~0.5s necessaires pour lire les 50 Mo


async def test_default_user_agent_is_omega_fuzz(server: ThreadingHTTPServer) -> None:
    port = server.server_address[1]
    client = HttpxHttpClient()
    response = await client.send(method="GET", url=f"http://127.0.0.1:{port}/echo-user-agent")
    assert response.body == f"omega-fuzz-httpx/{__version__}".encode()


async def test_custom_user_agent_header_overrides_default(server: ThreadingHTTPServer) -> None:
    port = server.server_address[1]
    client = HttpxHttpClient()
    response = await client.send(
        method="GET",
        url=f"http://127.0.0.1:{port}/echo-user-agent",
        headers={"User-Agent": "custom-agent"},
    )
    assert response.body == b"custom-agent"


async def test_invalid_url_control_character_is_a_soft_failure() -> None:
    """Meme categorie de bug que celui deja rencontre et corrige cote
    omega-fold (infrastructure/network/aiohttp_crawler.py) : un
    caractere non imprimable dans une URL (ex. extrait d'un href HTML
    casse) ne doit jamais faire planter le scan."""
    client = HttpxHttpClient()
    response = await client.send(method="GET", url="http://example.com/\x00\x01")
    assert response.status_code == 0
    assert response.fetch_error is not None
