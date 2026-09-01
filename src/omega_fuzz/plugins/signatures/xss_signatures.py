# Copyright (c) 2026 kraynux - Licence MIT
"""Signatures XSS reflechies non destructives (OMEGA-FUZZ_PLAN_DEV.md
Phase 7b point 7 — catalogue `xss.yaml`). Fonction pure, meme patron que
les fuzzers de Phase 7a : ne touche jamais `HttpClient`
(OMEGA-FUZZ_ARBORESCENCE.md §29.1). Le catalogue est fourni par
l'appelant (deja charge par `infrastructure.payloads.payload_loader`) —
ce module ne fait aucune I/O."""
from __future__ import annotations

from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from omega_fuzz.domain.findings.payload_catalog import PayloadCatalog
from omega_fuzz.domain.requests.request_context import RequestContext
from omega_fuzz.domain.requests.request_id import build_request_id
from omega_fuzz.domain.requests.request_metadata import RequestMetadata
from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.domain.requests.scan_request import ScanRequest
from omega_fuzz.domain.tests.test import Test
from omega_fuzz.plugins.fuzzers.common.fuzz_test_factory import build_fuzz_test

_MODULE = "sigxss"
_SUBTYPE = "reflected_xss"


def build_plan(
    *,
    target_short: str,
    sequence: int,
    url: str,
    parameter_name: str,
    catalog: PayloadCatalog,
    now: datetime,
    module: str = _MODULE,
) -> tuple[Test, tuple[ScanRequest, ...]]:
    parts = urlsplit(url)
    endpoint = parts.path or "/"
    test = build_fuzz_test(
        module=module,
        subtype=_SUBTYPE,
        target_short=target_short,
        sequence=sequence,
        url=url,
        method="GET",
        endpoint=endpoint,
        parameters=(parameter_name,),
        description=f"Signature XSS reflechie sur le parametre {parameter_name!r} de {endpoint}",
        now=now,
    )

    requests: list[ScanRequest] = []
    for index, entry in enumerate(catalog.payloads, start=1):
        query_pairs = dict(parse_qsl(parts.query, keep_blank_values=True))
        query_pairs[parameter_name] = entry.value
        mutated_url = urlunsplit(
            (parts.scheme, parts.netloc, parts.path, urlencode(query_pairs), "")
        )
        requests.append(
            ScanRequest(
                request_id=build_request_id(
                    module=module,
                    target_short=target_short,
                    test_sequence=sequence,
                    request_sequence=index,
                ),
                method="GET",
                url=mutated_url,
                normalized_url=mutated_url,
                context=RequestContext(
                    phase=RequestPhase.TEST,
                    module=module,
                    purpose="signature_xss_reflected",
                    target_id=target_short,
                    depth=0,
                ),
                created_at=now,
                test_id=test.test_id,
                metadata=RequestMetadata(
                    payload_index=index - 1,
                    payload_type="xss",
                    parameter_name=parameter_name,
                    mutation_strategy="substitution",
                    payload_value=entry.value,
                    detection_pattern=entry.detection_pattern,
                ),
            )
        )

    return test, tuple(requests)
