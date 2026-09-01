# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'emission HTTP (OMEGA-FUZZ_ARBORESCENCE.md §15.3, §19).
Implementation de production confinee a `infrastructure.network`
(`httpx`, voir le contrat import-linter dedie).

Revision Phase 4 : `fetch_error` ajoute — lecon directement tiree de
omega-fold cette session (`ports/distant_crawler.py::CrawledPage`) : un
client HTTP qui leve sur la moindre erreur reseau individuelle casse
tout le crawl. L'implementation concrete doit toujours retourner une
`HttpResponse` avec `fetch_error` renseigne plutot que lever, pour une
erreur reseau individuelle (timeout, connexion refusee, DNS...).

Revision Phase 10b : attributs exposes en proprietes en lecture seule
(pas en attributs simples). Un attribut Protocol simple est considere
lecture-ecriture par mypy (verification invariante) — incompatible avec
une dataclass `frozen=True` (`HttpxResponse`, Phase 4), qui expose ses
champs en lecture seule uniquement. `HttpResponse` n'a jamais ete
modifie apres construction nulle part dans le code : la lecture seule
reflete l'usage reel, pas seulement un contournement de mypy."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol


class HttpResponse(Protocol):
    @property
    def status_code(self) -> int: ...
    @property
    def headers(self) -> Mapping[str, str]: ...
    @property
    def body(self) -> bytes: ...
    @property
    def elapsed_seconds(self) -> float: ...
    @property
    def final_url(self) -> str: ...
    @property
    def truncated(self) -> bool: ...
    @property
    def fetch_error(self) -> str | None: ...


class HttpClient(Protocol):
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
    ) -> HttpResponse: ...
