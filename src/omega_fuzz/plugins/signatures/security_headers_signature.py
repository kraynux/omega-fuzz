# Copyright (c) 2026 kraynux - Licence MIT
"""Verification des headers de securite (OMEGA-FUZZ_PLAN_DEV.md
Phase 7b point 9 — catalogue `headers.yaml`). Pas de mutation : une
seule requete GET, l'analyse porte sur les headers de la reponse
(`infrastructure.analyzers.header_analyzer`), pas sur un payload
envoye. Fonction pure, ne touche jamais `HttpClient`."""
from __future__ import annotations

from datetime import datetime
from urllib.parse import urlsplit

from omega_fuzz.domain.requests.request_context import RequestContext
from omega_fuzz.domain.requests.request_id import build_request_id
from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.domain.requests.scan_request import ScanRequest
from omega_fuzz.domain.tests.test import Test
from omega_fuzz.plugins.fuzzers.common.fuzz_test_factory import build_fuzz_test

_MODULE = "sigheaders"
_SUBTYPE = "security_headers"


def build_plan(
    *, target_short: str, sequence: int, url: str, now: datetime, module: str = _MODULE
) -> tuple[Test, tuple[ScanRequest, ...]]:
    endpoint = urlsplit(url).path or "/"
    test = build_fuzz_test(
        module=module,
        subtype=_SUBTYPE,
        target_short=target_short,
        sequence=sequence,
        url=url,
        method="GET",
        endpoint=endpoint,
        parameters=(),
        description=f"Verification des headers de securite sur {endpoint}",
        now=now,
    )

    request = ScanRequest(
        request_id=build_request_id(
            module=module, target_short=target_short, test_sequence=sequence, request_sequence=1
        ),
        method="GET",
        url=url,
        normalized_url=url,
        context=RequestContext(
            phase=RequestPhase.TEST,
            module=module,
            purpose="signature_security_headers",
            target_id=target_short,
            depth=0,
        ),
        created_at=now,
        test_id=test.test_id,
    )

    return test, (request,)
