# Copyright (c) 2026 kraynux - Licence MIT
"""Signatures d'injection avec validation prudente
(OMEGA-FUZZ_PLAN_DEV.md Phase 7b point 8 — catalogue `injection.yaml`) :
payloads generiques, pas de fingerprint SQL/NoSQL specifique — repose
sur `infrastructure.analyzers.error_detector` pour la detection
d'erreur en reponse. `module="sigsqli"` reprend le nom d'exemple de
OMEGA-FUZZ_SPECIFICATIONS.md §12.3 (`test_sigsqli_...`) meme si la
detection reste generique, pas specifiquement SQL. Fonction pure, ne
touche jamais `HttpClient`."""
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

_MODULE = "sigsqli"
_SUBTYPE = "generic_injection"


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
        description=f"Signature d'injection generique sur le parametre {parameter_name!r} de {endpoint}",
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
                    purpose="signature_generic_injection",
                    target_id=target_short,
                    depth=0,
                ),
                created_at=now,
                test_id=test.test_id,
                metadata=RequestMetadata(
                    payload_index=index - 1,
                    payload_type="injection",
                    parameter_name=parameter_name,
                    mutation_strategy="substitution",
                    payload_value=entry.value,
                    detection_pattern=entry.detection_pattern,
                ),
            )
        )

    return test, tuple(requests)
