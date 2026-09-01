# Copyright (c) 2026 kraynux - Licence MIT
"""Detection de codes HTTP anormaux et de messages d'erreur techniques
(OMEGA-FUZZ_PLAN_DEV.md Phase 7b point 6). Un code 5xx est un fait
directement observe (`VERIFIED`) ; une signature d'erreur dans le corps
est une heuristique (`INFERRED`) — liste generique, pas de fingerprint
SQL/NoSQL specifique (coherent avec « validation prudente »)."""
from __future__ import annotations

from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.domain.findings.observation import Observation
from omega_fuzz.domain.services.redaction_service import redact_body_snippet

_ERROR_SIGNATURES: tuple[str, ...] = (
    "sql syntax",
    "ora-",
    "sqlite error",
    "unclosed quotation mark",
    "you have an error in your sql syntax",
    "warning: mysql",
    "stack trace",
    "traceback (most recent call last)",
    "internal server error",
)


def detect_error(*, status_code: int, response_body: str, request_id: str) -> Observation | None:
    if status_code >= 500:
        return Observation(
            kind="http_error",
            description=f"Code HTTP anormal observe ({status_code})",
            confidence=ConfidenceLevel.VERIFIED,
            request_id=request_id,
            evidence_summary=redact_body_snippet(response_body),
        )

    lowered = response_body.lower()
    for signature in _ERROR_SIGNATURES:
        if signature in lowered:
            return Observation(
                kind="error_disclosure",
                description=f"Message d'erreur technique detecte dans la reponse ({signature!r})",
                confidence=ConfidenceLevel.INFERRED,
                request_id=request_id,
                evidence_summary=redact_body_snippet(response_body),
            )
    return None
