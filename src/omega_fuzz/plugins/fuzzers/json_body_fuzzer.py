# Copyright (c) 2026 kraynux - Licence MIT
"""Fuzz des bodies JSON (OMEGA-FUZZ_PLAN_DEV.md Phase 7a point 3). Prend
un `template` JSON deja identifie par l'appelant — la decouverte
automatique d'endpoints JSON est hors scope (la decouverte HTML/
formulaires de Phase 4 ne couvre pas les APIs JSON). Fonction pure : ne
touche jamais `HttpClient`."""
from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any
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
_SUBTYPE = "json_body"


def build_plan(
    *,
    target_short: str,
    sequence: int,
    url: str,
    template: Mapping[str, Any],
    key_name: str,
    now: datetime,
    mutations: tuple[str, ...] = GENERIC_MUTATIONS,
    module: str = _MODULE,
) -> tuple[Test, tuple[ScanRequest, ...]]:
    endpoint = urlsplit(url).path or "/"
    test = build_fuzz_test(
        module=module,
        subtype=_SUBTYPE,
        target_short=target_short,
        sequence=sequence,
        url=url,
        method="POST",
        endpoint=endpoint,
        parameters=(key_name,),
        description=f"Fuzz de la cle JSON {key_name!r} sur {endpoint}",
        now=now,
    )

    requests: list[ScanRequest] = []
    for index, mutation in enumerate(mutations, start=1):
        mutated_body = dict(template)
        mutated_body[key_name] = mutation
        body = json.dumps(mutated_body).encode("utf-8")
        requests.append(
            ScanRequest(
                request_id=build_request_id(
                    module=module,
                    target_short=target_short,
                    test_sequence=sequence,
                    request_sequence=index,
                ),
                method="POST",
                url=url,
                normalized_url=url,
                context=RequestContext(
                    phase=RequestPhase.TEST,
                    module=module,
                    purpose="fuzz_json_body",
                    target_id=target_short,
                    depth=0,
                ),
                created_at=now,
                test_id=test.test_id,
                headers={"Content-Type": "application/json"},
                body=body,
                metadata=RequestMetadata(
                    payload_index=index - 1,
                    payload_type="generic",
                    parameter_name=key_name,
                    mutation_strategy="substitution",
                ),
            )
        )

    return test, tuple(requests)
