# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/test_plan_generator.py::TestPlanGenerator (Phase 10a)
en combinant les fuzzers (7a) et signatures (7b) pour produire
l'ensemble des tests a executer sur une URL decouverte donnee. Vit dans
`plugins/` (pas `application/`) car il appelle directement les
fonctions pures de `plugins/fuzzers/`/`plugins/signatures/` — la
Dependency Rule interdit a `application` de le faire elle-meme
(couches soeurs, meme raisonnement deja rencontre pour
`ResponseAnalyzer`/`AccessControlAnalyzer` aux Phases 7b/7c, cette
fois du cote de la generation de plans plutot que de leur analyse).

`generate_for_form` (comblement de trou de couverture, post-Phase 10) :
fuzzing de formulaires `GET` uniquement — `application.services.
discovery_orchestrator.run_discovery` filtre deja les formulaires
`POST`/`PUT`/`DELETE` avant meme de les exposer ici (risque d'ecriture
non desiree sur la cible, decision produit) — ce module n'a donc jamais
a re-verifier la methode."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_fuzz.plugins.fuzzers import form_parameter_fuzzer, header_fuzzer, query_parameter_fuzzer
from omega_fuzz.plugins.signatures import (
    injection_signatures,
    security_headers_signature,
    xss_signatures,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from omega_fuzz.domain.findings.payload_catalog import PayloadCatalog, SecurityHeadersCatalog
    from omega_fuzz.domain.requests.scan_request import ScanRequest
    from omega_fuzz.domain.tests.test import Test
    from omega_fuzz.ports.url_discoverer import DiscoveredForm


class CompositeTestPlanGenerator:
    """Implemente ports/test_plan_generator.py::TestPlanGenerator. Les
    compteurs de sequence sont un etat d'instance propre a chaque
    module (`fuzzhttp`/`sigxss`/`sigsqli`/`sigheaders`), incrementes a
    chaque plan genere — une instance est donc dediee a un seul scan."""

    def __init__(
        self,
        *,
        xss_catalog: PayloadCatalog | None = None,
        injection_catalog: PayloadCatalog | None = None,
        security_headers_catalog: SecurityHeadersCatalog | None = None,
    ) -> None:
        self._xss_catalog = xss_catalog
        self._injection_catalog = injection_catalog
        self._security_headers_catalog = security_headers_catalog
        self._sequence_counters: dict[str, int] = {}

    def _next_sequence(self, module: str) -> int:
        self._sequence_counters[module] = self._sequence_counters.get(module, 0) + 1
        return self._sequence_counters[module]

    def generate_for_url(
        self, *, target_short: str, url: str, parameters: Sequence[str], now: datetime
    ) -> Sequence[tuple[Test, Sequence[ScanRequest], str]]:
        plans: list[tuple[Test, Sequence[ScanRequest], str]] = []

        if self._security_headers_catalog is not None:
            test, requests = security_headers_signature.build_plan(
                target_short=target_short, sequence=self._next_sequence("sigheaders"), url=url, now=now
            )
            plans.append((test, requests, "signature_headers"))

        for header_name in header_fuzzer.FUZZABLE_HEADERS:
            test, requests = header_fuzzer.build_plan(
                target_short=target_short,
                sequence=self._next_sequence("fuzzhttp"),
                url=url,
                header_name=header_name,
                now=now,
            )
            plans.append((test, requests, "fuzz"))

        for parameter_name in parameters:
            test, requests = query_parameter_fuzzer.build_plan(
                target_short=target_short,
                sequence=self._next_sequence("fuzzhttp"),
                url=url,
                parameter_name=parameter_name,
                now=now,
            )
            plans.append((test, requests, "fuzz"))

            if self._xss_catalog is not None:
                test, requests = xss_signatures.build_plan(
                    target_short=target_short,
                    sequence=self._next_sequence("sigxss"),
                    url=url,
                    parameter_name=parameter_name,
                    catalog=self._xss_catalog,
                    now=now,
                )
                plans.append((test, requests, "signature"))

            if self._injection_catalog is not None:
                test, requests = injection_signatures.build_plan(
                    target_short=target_short,
                    sequence=self._next_sequence("sigsqli"),
                    url=url,
                    parameter_name=parameter_name,
                    catalog=self._injection_catalog,
                    now=now,
                )
                plans.append((test, requests, "signature"))

        return plans

    def generate_for_form(
        self, *, target_short: str, form: DiscoveredForm, now: datetime
    ) -> Sequence[tuple[Test, Sequence[ScanRequest], str]]:
        plans: list[tuple[Test, Sequence[ScanRequest], str]] = []
        for field_name in form.fields:
            test, requests = form_parameter_fuzzer.build_plan(
                target_short=target_short,
                sequence=self._next_sequence("fuzzhttp"),
                action_url=form.action_url,
                method=form.method,
                fields=form.fields,
                field_name=field_name,
                now=now,
            )
            plans.append((test, requests, "fuzz"))
        return plans
