# Copyright (c) 2026 kraynux - Licence MIT
"""Test de controle d'acces explicitement autorise
(OMEGA-FUZZ_PLAN_DEV.md Phase 7c point 10) : verifie qu'une ressource
supposee protegee (`protected_url`) n'est pas accessible avec la
session courante — session presumee insuffisamment privilegiee, fournie
et appliquee par l'appelant/orchestrateur, pas par ce module. Requete
unique en lecture seule (`GET`). Fonction pure, ne touche jamais
`HttpClient`/`SessionProvider`."""
from __future__ import annotations

from datetime import datetime
from urllib.parse import urlsplit

from omega_fuzz.domain.requests.request_context import RequestContext
from omega_fuzz.domain.requests.request_id import build_request_id
from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.domain.requests.scan_request import ScanRequest
from omega_fuzz.domain.tests.test import Test
from omega_fuzz.plugins.fuzzers.common.fuzz_test_factory import build_fuzz_test

_MODULE = "logic"
_SUBTYPE = "authorization"


def build_plan(
    *, target_short: str, sequence: int, protected_url: str, now: datetime, module: str = _MODULE
) -> tuple[Test, tuple[ScanRequest, ...]]:
    endpoint = urlsplit(protected_url).path or "/"
    test = build_fuzz_test(
        module=module,
        subtype=_SUBTYPE,
        target_short=target_short,
        sequence=sequence,
        url=protected_url,
        method="GET",
        endpoint=endpoint,
        parameters=(),
        description=(
            f"Verifie que {endpoint} refuse la session courante — hypothese : cette "
            f"ressource necessite un niveau de privilege que la session testee n'a pas"
        ),
        now=now,
    )

    request = ScanRequest(
        request_id=build_request_id(
            module=module, target_short=target_short, test_sequence=sequence, request_sequence=1
        ),
        method="GET",
        url=protected_url,
        normalized_url=protected_url,
        context=RequestContext(
            phase=RequestPhase.TEST,
            module=module,
            purpose="logic_authorization_check",
            target_id=target_short,
            depth=0,
        ),
        created_at=now,
        test_id=test.test_id,
    )

    return test, (request,)
