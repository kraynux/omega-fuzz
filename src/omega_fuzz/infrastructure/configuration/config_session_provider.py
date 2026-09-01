# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/session_provider.py::SessionProvider pour les 4
modes (OMEGA-FUZZ_ARBORESCENCE.md §45.5). Renomme depuis
`static_session_provider.py` (Phase 4) : "static" n'etait plus exact des
que `login_form` effectue une vraie requete HTTP.

`login_form` : POST `application/x-www-form-urlencoded` vers `login_url`
avec `username_field`/`password_field`, extrait le **premier**
`Set-Cookie` de la reponse (limitation documentee : un seul cookie de
session capture, cas d'usage le plus courant — extraction multi-cookies
differee). Le resultat est mis en cache : un seul login par instance,
jamais rejoue (§45.5 : « resultat mis en cache »)."""
from __future__ import annotations

from urllib.parse import urlencode

from omega_fuzz.core.errors import DependencyError
from omega_fuzz.domain.auth.auth_context import AuthContext, AuthMode
from omega_fuzz.domain.auth.session import Session
from omega_fuzz.ports.http_client import HttpClient


def _parse_first_cookie(set_cookie_header: str) -> tuple[str, str] | None:
    first_pair = set_cookie_header.split(";", 1)[0].strip()
    if "=" not in first_pair:
        return None
    name, _, value = first_pair.partition("=")
    return name.strip(), value.strip()


class ConfigSessionProvider:
    def __init__(self, auth_context: AuthContext, *, http_client: HttpClient | None = None) -> None:
        self._auth_context = auth_context
        self._http_client = http_client
        self._cached_session: Session | None = None

    async def get_session(self) -> Session:
        mode = self._auth_context.mode
        if mode is AuthMode.NONE:
            return Session()
        if mode is AuthMode.COOKIE:
            cookie = self._auth_context.cookie or ""
            return Session(cookies={"session": cookie})
        if mode is AuthMode.BEARER_TOKEN:
            token = self._auth_context.bearer_token or ""
            return Session(headers={"Authorization": f"Bearer {token}"})

        if self._cached_session is not None:
            return self._cached_session
        self._cached_session = await self._perform_login()
        return self._cached_session

    async def _perform_login(self) -> Session:
        if self._http_client is None:
            raise DependencyError(
                "SessionProvider mode=login_form necessite un HttpClient pour effectuer "
                "la requete de connexion"
            )
        ctx = self._auth_context
        body = urlencode(
            {
                ctx.username_field or "username": ctx.username or "",
                ctx.password_field or "password": ctx.password or "",
            }
        ).encode("utf-8")

        response = await self._http_client.send(
            method="POST",
            url=ctx.login_url or "",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=body,
        )
        if response.fetch_error is not None:
            raise DependencyError(f"echec de la requete de connexion : {response.fetch_error}")
        if response.status_code >= 400:
            raise DependencyError(
                f"echec de la connexion (code HTTP {response.status_code})"
            )

        set_cookie = response.headers.get("set-cookie") or response.headers.get("Set-Cookie")
        if not set_cookie:
            return Session()
        parsed = _parse_first_cookie(set_cookie)
        if parsed is None:
            return Session()
        name, value = parsed
        return Session(cookies={name: value})
