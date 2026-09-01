# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/http_client.py::HttpClient. `httpx` est exclusivement
utilise dans cette couche (contrat import-linter dedie).

`follow_redirects=False` volontaire : la politique de redirection
(scope, interne/externe) est geree explicitement par l'orchestrateur de
decouverte via `redirect_policy.decide_redirect`, jamais implicitement
par la bibliotheque HTTP — sans quoi un lien externe pourrait etre suivi
avant meme d'avoir pu etre evalue contre le scope.

Deux bugs reels critiques corriges suite a un usage reel (scan sur une
arborescence contenant des fichiers volumineux, ISOs de plusieurs Go) :

1. Lecture EN STREAMING, plafonnee a `max_response_body_size` (ou
   `HARD_MAX_RESPONSE_BODY_SIZE` a defaut si aucune limite n'est
   fournie) — `client.request()` (retire) telechargeait l'INTEGRALITE du
   corps de reponse en memoire avant meme de verifier une quelconque
   limite : la consommation memoire du processus grimpait a plusieurs Go
   (jusqu'a saturation, crash de l'application) des qu'une ressource
   distante volumineuse etait rencontree, quelle que soit
   `max_response_body_size` deja configuree — cette limite n'etait
   verifiee qu'APRES coup, jamais pendant le telechargement lui-meme. La
   connexion est desormais fermee des que le plafond est atteint, sans
   jamais lire plus que ce plafond en memoire.

2. `except Exception` (au lieu d'une liste fermee de types httpx) : meme
   categorie de bug que celui deja rencontre et corrige cote omega-fold
   (`infrastructure/network/aiohttp_crawler.py`, ou `yarl` leve parfois
   un simple `ValueError` — pas seulement le type d'exception dedie —
   pour une URL syntaxiquement invalide, ex. un caractere de controle
   non imprimable extrait d'un href HTML casse). httpx a le meme
   comportement (verifie : `InvalidURL`/`UnsupportedProtocol`/
   `ConnectError` selon le point exact ou l'interpretation echoue,
   aucune garantie qu'une liste close de types couvre tous les cas
   presents et futurs). Demande explicite de resilience totale sur toute
   panne PAR REQUETE, jamais sur la configuration de timeout elle-meme
   (qui reste une erreur de programmation, jamais masquee). `Exception`
   exclut deliberement `BaseException` : `asyncio.CancelledError`/
   `KeyboardInterrupt` restent propages normalement — necessaire a
   l'annulation propre d'un scan (voir interfaces/tui/screens/
   scan_progress_screen.py, bouton "Arreter")."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import httpx

from omega_fuzz.core.version import __version__
from omega_fuzz.domain.profiles.hard_caps import HARD_MAX_RESPONSE_BODY_SIZE
from omega_fuzz.infrastructure.network.timeout_policy import DEFAULT_TIMEOUT_SECONDS

_USER_AGENT = f"omega-fuzz-httpx/{__version__}"


@dataclass(frozen=True, slots=True)
class HttpxResponse:
    """Implemente ports/http_client.py::HttpResponse."""

    status_code: int
    headers: Mapping[str, str] = field(default_factory=dict)
    body: bytes = b""
    elapsed_seconds: float = 0.0
    final_url: str = ""
    truncated: bool = False
    fetch_error: str | None = None


class HttpxHttpClient:
    """Implemente ports/http_client.py::HttpClient."""

    async def send(
        self,
        *,
        method: str,
        url: str,
        headers: Mapping[str, str] | None = None,
        body: bytes | None = None,
        timeout: float | None = None,
        verify_tls: bool = True,
        max_response_body_size: int | None = None,
    ) -> HttpxResponse:
        effective_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT_SECONDS
        cap = (
            max_response_body_size
            if max_response_body_size is not None
            else HARD_MAX_RESPONSE_BODY_SIZE
        )
        request_headers = {"User-Agent": _USER_AGENT, **dict(headers or {})}

        try:
            async with (
                httpx.AsyncClient(
                    verify=verify_tls, follow_redirects=False, timeout=effective_timeout
                ) as client,
                client.stream(method, url, headers=request_headers, content=body) as response,
            ):
                chunks = bytearray()
                truncated = False
                async for chunk in response.aiter_bytes():
                    remaining = cap - len(chunks)
                    if remaining <= 0:
                        truncated = True
                        break
                    chunks.extend(chunk[:remaining])
                    if len(chunks) >= cap:
                        truncated = True
                        break
                response_body = bytes(chunks)
                status_code = response.status_code
                response_headers = dict(response.headers)
                final_url = str(response.url)
        except Exception as exc:  # noqa: BLE001 - resilience totale demandee, voir docstring
            return HttpxResponse(
                status_code=0, final_url=url, fetch_error=str(exc) or type(exc).__name__
            )

        return HttpxResponse(
            status_code=status_code,
            headers=response_headers,
            body=response_body,
            elapsed_seconds=response.elapsed.total_seconds(),
            final_url=final_url,
            truncated=truncated,
        )
