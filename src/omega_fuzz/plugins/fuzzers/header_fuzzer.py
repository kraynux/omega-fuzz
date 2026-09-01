# Copyright (c) 2026 kraynux - Licence MIT
"""Mutation controlee de headers (OMEGA-FUZZ_PLAN_DEV.md Phase 7a
point 4). Liste fixe de headers couramment fuzzes ; un `Test` par
header (meme convention que les autres fuzzers). Fonction pure : ne
touche jamais `HttpClient`."""
from __future__ import annotations

from datetime import datetime
from urllib.parse import urlsplit

from omega_fuzz.domain.requests.request_context import RequestContext
from omega_fuzz.domain.requests.request_id import build_request_id
from omega_fuzz.domain.requests.request_metadata import RequestMetadata
from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.domain.requests.scan_request import ScanRequest
from omega_fuzz.domain.tests.test import Test
from omega_fuzz.plugins.fuzzers.common.fuzz_test_factory import build_fuzz_test
from omega_fuzz.plugins.fuzzers.common.mutation_context import GENERIC_MUTATIONS

_MODULE = "fuzzhttp"
_SUBTYPE = "header"

FUZZABLE_HEADERS: tuple[str, ...] = ("User-Agent", "Referer", "X-Forwarded-For", "Accept-Language")


def build_plan(
    *,
    target_short: str,
    sequence: int,
    url: str,
    header_name: str,
    now: datetime,
    mutations: tuple[str, ...] = GENERIC_MUTATIONS,
    module: str = _MODULE,
) -> tuple[Test, tuple[ScanRequest, ...]]:
    if header_name not in FUZZABLE_HEADERS:
        raise ValueError(f"header non fuzzable : {header_name!r} (attendu {FUZZABLE_HEADERS})")

    endpoint = urlsplit(url).path or "/"
    test = build_fuzz_test(
        module=module,
        subtype=_SUBTYPE,
        target_short=target_short,
        sequence=sequence,
        url=url,
        method="GET",
        endpoint=endpoint,
        parameters=(header_name,),
        description=f"Fuzz du header {header_name!r} sur {endpoint}",
        now=now,
    )

    requests: list[ScanRequest] = []
    for index, mutation in enumerate(mutations, start=1):
        requests.append(
            ScanRequest(
                request_id=build_request_id(
                    module=module,
                    target_short=target_short,
                    test_sequence=sequence,
                    request_sequence=index,
                ),
                method="GET",
                url=url,
                normalized_url=url,
                context=RequestContext(
                    phase=RequestPhase.TEST,
                    module=module,
                    purpose="fuzz_header",
                    target_id=target_short,
                    depth=0,
                ),
                created_at=now,
                test_id=test.test_id,
                headers={header_name: mutation},
                metadata=RequestMetadata(
                    payload_index=index - 1,
                    payload_type="generic",
                    parameter_name=header_name,
                    mutation_strategy="substitution",
                ),
            )
        )

    return test, tuple(requests)
