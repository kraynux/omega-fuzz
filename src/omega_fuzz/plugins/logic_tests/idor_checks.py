# Copyright (c) 2026 kraynux - Licence MIT
"""Verification d'IDOR (OMEGA-FUZZ_PLAN_DEV.md Phase 7c point 10,
OMEGA-FUZZ_SPECIFICATIONS.md §9.2 exemple : « Vérification d'IDOR sur
/api/orders/{id} »). `candidate_foreign_values` (valeurs d'ID
presumees appartenir a un autre utilisateur) sont fournies par
l'appelant — cette connaissance est necessairement propre a la cible,
ne peut pas etre generique. Toutes les requetes sont des `GET` en
lecture seule (§32 : « eviter les operations destructrices par
defaut »). L'authentification est appliquee par l'orchestrateur
(`application.services.test_orchestrator.run_logic_test`), pas ici —
fonction pure, ne touche jamais `HttpClient`/`SessionProvider`."""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from omega_fuzz.domain.requests.request_context import RequestContext
from omega_fuzz.domain.requests.request_id import build_request_id
from omega_fuzz.domain.requests.request_metadata import RequestMetadata
from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.domain.requests.scan_request import ScanRequest
from omega_fuzz.domain.tests.test import Test
from omega_fuzz.plugins.fuzzers.common.fuzz_test_factory import build_fuzz_test

_MODULE = "logic"
_SUBTYPE = "idor"


def build_plan(
    *,
    target_short: str,
    sequence: int,
    url: str,
    id_parameter_name: str,
    candidate_foreign_values: Sequence[str],
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
        parameters=(id_parameter_name,),
        description=(
            f"Verifie que la session courante n'accede pas aux ressources d'autrui via "
            f"{id_parameter_name!r} sur {endpoint} — hypothese : les valeurs candidates "
            f"testees appartiennent a un autre utilisateur, tout acces obtenu est suspect"
        ),
        now=now,
    )

    requests: list[ScanRequest] = []
    for index, candidate in enumerate(candidate_foreign_values, start=1):
        query_pairs = dict(parse_qsl(parts.query, keep_blank_values=True))
        query_pairs[id_parameter_name] = candidate
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
                    purpose="logic_idor_check",
                    target_id=target_short,
                    depth=0,
                ),
                created_at=now,
                test_id=test.test_id,
                metadata=RequestMetadata(
                    payload_index=index - 1,
                    payload_type="idor_candidate",
                    parameter_name=id_parameter_name,
                    mutation_strategy="substitution",
                    payload_value=candidate,
                ),
            )
        )

    return test, tuple(requests)
