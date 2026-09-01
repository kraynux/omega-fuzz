# Copyright (c) 2026 kraynux - Licence MIT
"""Test de logique metier explicitement active
(OMEGA-FUZZ_PLAN_DEV.md Phase 7c point 11) : verifie qu'un acces direct
a une etape avancee d'un processus metier (`skip_to_url`), sans passer
par les etapes prealables, est refuse. Requete unique en lecture seule
(`GET`). Fonction pure, ne touche jamais `HttpClient`/`SessionProvider`."""
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
_SUBTYPE = "workflow"


def build_plan(
    *, target_short: str, sequence: int, skip_to_url: str, now: datetime, module: str = _MODULE
) -> tuple[Test, tuple[ScanRequest, ...]]:
    endpoint = urlsplit(skip_to_url).path or "/"
    test = build_fuzz_test(
        module=module,
        subtype=_SUBTYPE,
        target_short=target_short,
        sequence=sequence,
        url=skip_to_url,
        method="GET",
        endpoint=endpoint,
        parameters=(),
        description=(
            f"Verifie qu'un acces direct a {endpoint} sans passer par les etapes "
            f"prealables du processus metier est refuse — hypothese : cette etape "
            f"necessite un etat prealable que la session testee n'a pas atteint"
        ),
        now=now,
    )

    request = ScanRequest(
        request_id=build_request_id(
            module=module, target_short=target_short, test_sequence=sequence, request_sequence=1
        ),
        method="GET",
        url=skip_to_url,
        normalized_url=skip_to_url,
        context=RequestContext(
            phase=RequestPhase.TEST,
            module=module,
            purpose="logic_workflow_check",
            target_id=target_short,
            depth=0,
        ),
        created_at=now,
        test_id=test.test_id,
    )

    return test, (request,)
