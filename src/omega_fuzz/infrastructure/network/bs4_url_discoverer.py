# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/url_discoverer.py::UrlDiscoverer via BeautifulSoup4/
lxml (choix technique non impose par les specs FUZZ, deja eprouve sur
omega-fold cette session). `bs4`/`lxml` sont confines a
`infrastructure` par le contrat import-linter dedie."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup


@dataclass(frozen=True, slots=True)
class Bs4DiscoveredForm:
    """Implemente ports/url_discoverer.py::DiscoveredForm."""

    action_url: str
    method: str
    fields: dict[str, str]


class Bs4UrlDiscoverer:
    """Implemente ports/url_discoverer.py::UrlDiscoverer."""

    def discover_urls(self, *, base_url: str, html_body: str) -> Sequence[str]:
        soup = BeautifulSoup(html_body, "lxml")
        urls: list[str] = []
        for anchor in soup.find_all("a", href=True):
            href = str(anchor["href"]).strip()
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue
            urls.append(urljoin(base_url, href))
        return urls

    def discover_forms(self, *, base_url: str, html_body: str) -> Sequence[Bs4DiscoveredForm]:
        soup = BeautifulSoup(html_body, "lxml")
        forms: list[Bs4DiscoveredForm] = []
        for form in soup.find_all("form"):
            action = str(form.get("action") or "").strip()
            method = str(form.get("method") or "GET").strip().upper()
            fields: dict[str, str] = {}
            for field in form.find_all(["input", "textarea", "select"]):
                name = field.get("name")
                if name:
                    fields[str(name)] = str(field.get("value") or "")
            forms.append(
                Bs4DiscoveredForm(
                    action_url=urljoin(base_url, action) if action else base_url,
                    method=method,
                    fields=fields,
                )
            )
        return forms
