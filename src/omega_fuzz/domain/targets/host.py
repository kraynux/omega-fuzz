# Copyright (c) 2026 kraynux - Licence MIT
"""Normalisation de host : lowercase, support optionnel IDN/punycode
(OMEGA-FUZZ_ARBORESCENCE.md §8, PLAN_DEV Phase 1)."""
from __future__ import annotations


def normalize_host(raw_host: str) -> str:
    """Leve `ValueError` sur un host vide ou non encodable — a capturer
    par l'appelant (`domain.targets.url.normalize_url`) et remonter comme
    `invalid_url`."""
    host = raw_host.strip().lower().rstrip(".")
    if not host:
        raise ValueError("empty host")
    try:
        host.encode("ascii")
    except UnicodeEncodeError:
        try:
            host = host.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise ValueError(f"invalid IDN host: {raw_host!r}") from exc
    return host
