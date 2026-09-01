# Copyright (c) 2026 kraynux - Licence MIT
"""Normalisation d'URL brute vers `NormalizedUrl`
(OMEGA-FUZZ_ARBORESCENCE.md §14, PLAN_DEV Phase 1). Pure, sans reseau."""
from __future__ import annotations

from urllib.parse import urlsplit

from omega_fuzz.domain.targets.exclusions import ExclusionReason
from omega_fuzz.domain.targets.host import normalize_host
from omega_fuzz.domain.targets.port import normalize_port
from omega_fuzz.domain.targets.scheme import AllowedScheme
from omega_fuzz.domain.targets.url import NormalizedUrl, UrlNormalizationError


def normalize_url(raw_url: str) -> NormalizedUrl:
    """Leve `UrlNormalizationError(reason=INVALID_URL)` si l'URL ne peut
    pas etre analysee ou n'a pas de host, ou
    `UrlNormalizationError(reason=UNSUPPORTED_SCHEME)` si le schema n'est
    ni http ni https. Le fragment est toujours supprime (pas de sens
    cote serveur)."""
    try:
        parts = urlsplit(raw_url.strip())
    except ValueError as exc:
        raise UrlNormalizationError(ExclusionReason.INVALID_URL, str(exc)) from exc

    scheme = parts.scheme.lower()
    if not scheme:
        raise UrlNormalizationError(
            ExclusionReason.INVALID_URL,
            "URL sans schema (ajoutez http:// ou https:// devant l'adresse)",
        )
    if scheme not in {AllowedScheme.HTTP.value, AllowedScheme.HTTPS.value}:
        raise UrlNormalizationError(
            ExclusionReason.UNSUPPORTED_SCHEME, f"schema non supporte : {scheme!r}"
        )

    try:
        hostname = parts.hostname
        explicit_port = parts.port
    except ValueError as exc:
        # `parts.port` leve ValueError si le port n'est pas un entier valide.
        raise UrlNormalizationError(ExclusionReason.INVALID_URL, str(exc)) from exc

    if not hostname:
        raise UrlNormalizationError(ExclusionReason.INVALID_URL, "URL sans host")

    try:
        host = normalize_host(hostname)
    except ValueError as exc:
        raise UrlNormalizationError(ExclusionReason.INVALID_URL, str(exc)) from exc

    port = normalize_port(scheme=scheme, explicit_port=explicit_port)
    path = parts.path or "/"

    return NormalizedUrl(scheme=scheme, host=host, port=port, path=path, query=parts.query)
