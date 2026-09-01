# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'extraction d'URLs/formulaires/parametres depuis une reponse
HTML (OMEGA-FUZZ_ARBORESCENCE.md §15.3). Signature minimale Phase 0, a
enrichir en Phase 4 (decouverte).

Revision Phase 10b : attributs de `DiscoveredForm` exposes en proprietes
en lecture seule, meme raison que `ports/http_client.py::HttpResponse`
(compatibilite mypy avec les dataclasses `frozen=True` qui
l'implementent, ex. `Bs4DiscoveredForm`)."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol


class DiscoveredForm(Protocol):
    @property
    def action_url(self) -> str: ...
    @property
    def method(self) -> str: ...
    @property
    def fields(self) -> Mapping[str, str]: ...


class UrlDiscoverer(Protocol):
    def discover_urls(self, *, base_url: str, html_body: str) -> Sequence[str]: ...

    def discover_forms(self, *, base_url: str, html_body: str) -> Sequence[DiscoveredForm]: ...
