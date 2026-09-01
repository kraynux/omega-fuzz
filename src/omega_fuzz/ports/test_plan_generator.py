# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de generation de plans de test pour une URL decouverte
(Phase 10a — orchestration bout-en-bout). Necessaire car
`application.services.scan_orchestrator` ne peut pas appeler
directement les fuzzers/signatures de `plugins/` (Dependency Rule :
`application` et `plugins` sont des couches SOEURS, meme raisonnement
deja rencontre pour `ResponseAnalyzer`/`AccessControlAnalyzer` aux
Phases 7b/7c) — l'implementation concrete (qui, elle, peut importer
`plugins/fuzzers/`/`plugins/signatures/`) vit dans `plugins/`
elle-meme et est injectee via ce port."""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from omega_fuzz.domain.requests.scan_request import ScanRequest
from omega_fuzz.domain.tests.test import Test
from omega_fuzz.ports.url_discoverer import DiscoveredForm


class TestPlanGenerator(Protocol):
    def generate_for_url(
        self, *, target_short: str, url: str, parameters: Sequence[str], now: datetime
    ) -> Sequence[tuple[Test, Sequence[ScanRequest], str]]:
        """Retourne une sequence de `(Test, requests, kind)` ou `kind`
        vaut `"fuzz"` (a executer via
        `application.services.test_orchestrator.run_test`), `"signature"`
        (via `run_signature_test`, avec l'analyseur de reponses generique
        — jamais l'analyse de headers de securite) ou
        `"signature_headers"` (via `run_signature_test`, mais avec un
        analyseur DEDIE a la verification des headers de securite —
        Phase 10b : ce test est le seul a devoir la declencher, jamais
        les tests XSS/injection qui partagent par ailleurs le meme
        mecanisme d'execution)."""
        ...

    def generate_for_form(
        self, *, target_short: str, form: DiscoveredForm, now: datetime
    ) -> Sequence[tuple[Test, Sequence[ScanRequest], str]]:
        """Meme contrat de retour que `generate_for_url`, pour un
        formulaire `GET` deja decouvert et filtre par
        `application.services.discovery_orchestrator.run_discovery`
        (formulaires `POST`/`PUT`/`DELETE` jamais exposes ici — risque
        d'ecriture non desiree sur la cible, decision produit). `kind`
        vaut toujours `"fuzz"` : pas d'analyse de reponse dediee aux
        formulaires a ce jour."""
        ...
