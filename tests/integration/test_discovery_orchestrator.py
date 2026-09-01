# Copyright (c) 2026 kraynux - Licence MIT
"""Verifie les 5 criteres d'acceptation de OMEGA-FUZZ_PLAN_DEV.md
Phase 4 sur un site synthetique reel (serveur threade, decision Q de la
passe de coherence) : aucun lien externe suivi, redirection externe
journalisee et ignoree, compteurs de decouverte incrementes a chaque
emission, profondeur minimale conservee, aucun payload de fuzz genere."""
from __future__ import annotations

import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, ClassVar

import pytest

from omega_fuzz.application.services.discovery_orchestrator import run_discovery
from omega_fuzz.domain.auth.auth_context import AuthContext, AuthMode
from omega_fuzz.domain.profiles.limits import Limits
from omega_fuzz.domain.services.url_normalization_service import normalize_url
from omega_fuzz.domain.targets.discovered_url import DiscoveredUrlState
from omega_fuzz.domain.targets.scope import build_scope
from omega_fuzz.domain.targets.scope_mode import ScopeMode
from omega_fuzz.domain.targets.target import Target
from omega_fuzz.domain.targets.target_id import TargetId, build_target_id
from omega_fuzz.infrastructure.configuration.config_session_provider import (
    ConfigSessionProvider,
)
from omega_fuzz.infrastructure.network.bs4_url_discoverer import Bs4UrlDiscoverer
from omega_fuzz.infrastructure.network.httpx_http_client import HttpxHttpClient

_HOME_PAGE = b"""
<html><body>
<a href="/about">About</a>
<a href="https://external.example/">External</a>
<a href="/redirect-internal">Redirect internal</a>
<a href="/redirect-external">Redirect external</a>
<a href="/big.iso">Big ISO</a>
<form action="/search" method="get">
    <input type="text" name="q" value="">
    <input type="hidden" name="category" value="all">
</form>
<form action="/comment" method="post">
    <input type="text" name="body" value="">
</form>
<form action="https://external.example/subscribe" method="get">
    <input type="text" name="email" value="">
</form>
</body></html>
"""
_ABOUT_PAGE = b"""
<html><body>
About page, dead end.
<form action="/search" method="get">
    <input type="text" name="q" value="">
    <input type="hidden" name="category" value="all">
</form>
</body></html>
"""


class _Handler(BaseHTTPRequestHandler):
    requested_paths: ClassVar[list[str]] = []

    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        _Handler.requested_paths.append(self.path)
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(_HOME_PAGE)
        elif self.path == "/about":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(_ABOUT_PAGE)
        elif self.path == "/redirect-internal":
            self.send_response(302)
            self.send_header("Location", "/about")
            self.end_headers()
        elif self.path == "/redirect-external":
            self.send_response(302)
            self.send_header("Location", "https://external.example/")
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


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
    _Handler.requested_paths = []
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
        # https autorise aussi, pour que le lien externe (schema https)
        # soit rejete sur le host (external_redirect), pas sur le schema.
        allowed_schemes=frozenset({"http", "https"}),
        scope_port=port,
        max_depth=2,
    )
    target_id = TargetId(build_target_id(host="127.0.0.1"))
    return Target(target_id=target_id, entry_url=entry_url, scope=scope)


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


async def test_discovery_respects_scope_depth_and_redirects(
    server: ThreadingHTTPServer,
) -> None:
    port = server.server_address[1]
    logger = _FakeLogger()
    result = await run_discovery(
        http_client=HttpxHttpClient(),
        url_discoverer=Bs4UrlDiscoverer(),
        session_provider=ConfigSessionProvider(AuthContext(mode=AuthMode.NONE)),
        target=_target(port),
        limits=_limits(),
        logger=logger,
    )

    by_url = {entry.url: entry for entry in result.discovered_urls}
    home_url = f"http://127.0.0.1:{port}/"
    about_url = f"http://127.0.0.1:{port}/about"
    redirect_internal_url = f"http://127.0.0.1:{port}/redirect-internal"
    redirect_external_url = f"http://127.0.0.1:{port}/redirect-external"
    external_url = "https://external.example/"
    iso_url = f"http://127.0.0.1:{port}/big.iso"

    # Le lien vers le .iso est rejete par le scope (extension binaire bloquee)
    # et n'est donc JAMAIS recupere par une requete HTTP reelle (bug reel :
    # l'appli semblait figee sur un dossier de fichiers .iso).
    assert by_url[iso_url].state is DiscoveredUrlState.REJECTED
    assert "/big.iso" not in _Handler.requested_paths

    # Aucun lien externe n'est suivi.
    assert external_url not in by_url or by_url[external_url].state is not DiscoveredUrlState.ACCEPTED
    assert result.statistics.discovery_requests == result.statistics.total_requests

    # La cible et /about ont bien ete visitees (statut ACCEPTED).
    assert by_url[home_url].state is DiscoveredUrlState.ACCEPTED
    assert by_url[about_url].state is DiscoveredUrlState.ACCEPTED
    assert by_url[about_url].depth == 1  # profondeur minimale connue (lien direct depuis /)

    # /redirect-internal est visitee (chemin interne valide) et sa redirection suivie.
    assert by_url[redirect_internal_url].state is DiscoveredUrlState.ACCEPTED
    assert result.statistics.redirects_followed >= 1

    # /redirect-external est visitee mais sa redirection est journalisee et ignoree.
    assert by_url[redirect_external_url].state is DiscoveredUrlState.ACCEPTED
    assert result.statistics.redirects_external_ignored == 1
    assert any(event == "redirect_external_ignored" for _, event, _ in logger.events)

    # Chaque requete de decouverte incremente discovery_requests et total_requests.
    assert result.statistics.discovery_requests > 0
    assert result.statistics.total_requests == result.statistics.discovery_requests

    # Aucun payload de fuzz genere : uniquement des requetes de decouverte.
    assert result.statistics.test_requests == 0


async def test_discovery_captures_get_forms_filters_post_and_out_of_scope(
    server: ThreadingHTTPServer,
) -> None:
    port = server.server_address[1]
    result = await run_discovery(
        http_client=HttpxHttpClient(),
        url_discoverer=Bs4UrlDiscoverer(),
        session_provider=ConfigSessionProvider(AuthContext(mode=AuthMode.NONE)),
        target=_target(port),
        limits=_limits(),
        logger=_FakeLogger(),
    )

    search_url = f"http://127.0.0.1:{port}/search"
    action_urls = {form.action_url for form in result.discovered_forms}

    # Le formulaire GET in-scope est bien retenu.
    assert search_url in action_urls
    search_form = next(form for form in result.discovered_forms if form.action_url == search_url)
    assert search_form.method.upper() == "GET"
    assert set(search_form.fields) == {"q", "category"}

    # Le formulaire POST est exclu (risque d'ecriture, decision produit).
    assert not any(form.action_url.endswith("/comment") for form in result.discovered_forms)

    # Le formulaire dont l'action pointe hors scope est exclu.
    assert not any("external.example" in form.action_url for form in result.discovered_forms)

    # Le meme formulaire (meme action_url + memes champs), trouve sur / et /about,
    # n'est retenu qu'une seule fois.
    assert sum(1 for form in result.discovered_forms if form.action_url == search_url) == 1
