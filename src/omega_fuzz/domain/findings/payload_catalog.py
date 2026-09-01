# Copyright (c) 2026 kraynux - Licence MIT
"""Modeles de catalogue de payloads (OMEGA-FUZZ_ARBORESCENCE.md §21).
Places en `domain.findings` plutot que `infrastructure.payloads`
(deviation par rapport au plan Phase 7b) : ce sont de simples types de
valeur (aucune dependance YAML/IO), et `plugins/signatures/` en a
besoin — `plugins` et `infrastructure` sont des couches SOEURS
(Dependency Rule : `app -> infrastructure|interfaces|plugins ->
application -> ...`, groupes separes par `|` mutuellement independants,
memes contraintes que "interfaces ne depend jamais de infrastructure").
`infrastructure.payloads.payload_loader`/`payload_catalog_provider`
importent ces types depuis ici — meme discipline que la correction
Phase 4 sur `redirect_policy`/`rate_limit_backoff_service`."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PayloadEntry:
    value: str
    detection_pattern: str | None = None


@dataclass(frozen=True, slots=True)
class PayloadCatalog:
    category: str
    version: str
    payloads: tuple[PayloadEntry, ...]


@dataclass(frozen=True, slots=True)
class RequiredHeader:
    name: str
    expected_value: str | None = None


@dataclass(frozen=True, slots=True)
class SecurityHeadersCatalog:
    version: str
    required_headers: tuple[RequiredHeader, ...]
