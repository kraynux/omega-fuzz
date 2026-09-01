# Copyright (c) 2026 kraynux - Licence MIT
"""Fuzz des champs de formulaire (OMEGA-FUZZ_PLAN_DEV.md Phase 7a
point 2). Prend une action/methode/champs deja decouverts
(`ports.url_discoverer.DiscoveredForm`, Phase 4) — ne decouvre rien
lui-meme. Fonction pure : ne touche jamais `HttpClient`.

Un formulaire `GET` serialise ses champs dans la query string de l'URL
(comportement navigateur), jamais dans un body — contrairement a `POST`,
qui encode les champs en `application/x-www-form-urlencoded` dans le
body. Distinction necessaire pour que le fuzzing de formulaires GET,
cable au pipeline automatique (seule methode retenue, voir
`application.services.discovery_orchestrator` : POST/PUT/DELETE exclus,
risque d'ecriture sur la cible), envoie des requetes semantiquement
valides plutot qu'un GET avec un body ignore par la plupart des
serveurs."""
from __future__ import annotations

from collections.abc import Mapping
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
_SUBTYPE = "form_parameter"


def build_plan(
    *,
    target_short: str,
    sequence: int,
    action_url: str,
    method: str,
    fields: Mapping[str, str],
    field_name: str,
    now: datetime,
    mutations: tuple[str, ...] = GENERIC_MUTATIONS,
    module: str = _MODULE,
) -> tuple[Test, tuple[ScanRequest, ...]]:
    http_method = method.upper()
    endpoint = urlsplit(action_url).path or "/"
    test = build_fuzz_test(
        module=module,
        subtype=_SUBTYPE,
        target_short=target_short,
        sequence=sequence,
        url=action_url,
        method=http_method,
        endpoint=endpoint,
        parameters=(field_name,),
        description=f"Fuzz du champ de formulaire {field_name!r} sur {endpoint}",
        now=now,
    )

    parts = urlsplit(action_url)

    requests: list[ScanRequest] = []
    for index, mutation in enumerate(mutations, start=1):
        mutated_fields = dict(fields)
        mutated_fields[field_name] = mutation

        if http_method == "GET":
            query_pairs = dict(parse_qsl(parts.query, keep_blank_values=True))
            query_pairs.update(mutated_fields)
            request_url = urlunsplit(
                (parts.scheme, parts.netloc, parts.path, urlencode(query_pairs), "")
            )
            request_headers: dict[str, str] = {}
            request_body: bytes | None = None
        else:
            request_url = action_url
            request_headers = {"Content-Type": "application/x-www-form-urlencoded"}
            request_body = urlencode(mutated_fields).encode("utf-8")

        requests.append(
            ScanRequest(
                request_id=build_request_id(
                    module=module,
                    target_short=target_short,
                    test_sequence=sequence,
                    request_sequence=index,
                ),
                method=http_method,
                url=request_url,
                normalized_url=request_url,
                context=RequestContext(
                    phase=RequestPhase.TEST,
                    module=module,
                    purpose="fuzz_form_parameter",
                    target_id=target_short,
                    depth=0,
                ),
                created_at=now,
                test_id=test.test_id,
                headers=request_headers,
                body=request_body,
                metadata=RequestMetadata(
                    payload_index=index - 1,
                    payload_type="generic",
                    parameter_name=field_name,
                    mutation_strategy="substitution",
                ),
            )
        )

    return test, tuple(requests)
