# Copyright (c) 2026 kraynux - Licence MIT
"""Fuzz des parametres de query string (OMEGA-FUZZ_PLAN_DEV.md Phase 7a
point 1). Fonction pure : ne touche jamais `HttpClient`
(OMEGA-FUZZ_ARBORESCENCE.md §29.1)."""
from __future__ import annotations

from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from omega_fuzz.domain.requests.request_context import RequestContext
from omega_fuzz.domain.requests.request_id import build_request_id
from omega_fuzz.domain.requests.request_metadata import RequestMetadata
from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.domain.requests.scan_request import ScanRequest
from omega_fuzz.domain.tests.test import Test
from omega_fuzz.plugins.fuzzers.common.fuzz_test_factory import build_fuzz_test
from omega_fuzz.plugins.fuzzers.common.mutation_context import GENERIC_MUTATIONS

_MODULE = "fuzzhttp"
_SUBTYPE = "query_parameter"


def build_plan(
    *,
    target_short: str,
    sequence: int,
    url: str,
    parameter_name: str,
    now: datetime,
    mutations: tuple[str, ...] = GENERIC_MUTATIONS,
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
        description=f"Fuzz du parametre de requete {parameter_name!r} sur {endpoint}",
        now=now,
    )

    requests: list[ScanRequest] = []
    for index, mutation in enumerate(mutations, start=1):
        query_pairs = dict(parse_qsl(parts.query, keep_blank_values=True))
        query_pairs[parameter_name] = mutation
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
                    purpose="fuzz_query_parameter",
                    target_id=target_short,
                    depth=0,
                ),
                created_at=now,
                test_id=test.test_id,
                metadata=RequestMetadata(
                    payload_index=index - 1,
                    payload_type="generic",
                    parameter_name=parameter_name,
                    mutation_strategy="substitution",
                ),
            )
        )

    return test, tuple(requests)
