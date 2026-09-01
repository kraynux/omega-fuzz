# Copyright (c) 2026 kraynux - Licence MIT
"""Detection de reflexion de payload (OMEGA-FUZZ_PLAN_DEV.md Phase 7b
point 5). Un `detection_pattern` (regex, fourni par le catalogue de
signatures) est prefere a une simple sous-chaine : plus specifique,
donc plus fiable — `CORROBORATED`. Sans pattern, un simple test de
sous-chaine reste possible mais moins fiable — `INFERRED`."""
from __future__ import annotations

import re

from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.domain.findings.observation import Observation
from omega_fuzz.domain.services.redaction_service import redact_body_snippet


def detect_reflection(
    *,
    response_body: str,
    request_id: str,
    payload_value: str | None,
    detection_pattern: str | None = None,
) -> Observation | None:
    if detection_pattern is not None:
        if re.search(detection_pattern, response_body):
            return Observation(
                kind="reflection",
                description="Payload reflete dans la reponse (motif de detection confirme)",
                confidence=ConfidenceLevel.CORROBORATED,
                request_id=request_id,
                evidence_summary=redact_body_snippet(response_body),
            )
        return None

    if payload_value and payload_value in response_body:
        return Observation(
            kind="reflection",
            description="Payload reflete tel quel dans la reponse (sous-chaine)",
            confidence=ConfidenceLevel.INFERRED,
            request_id=request_id,
            evidence_summary=redact_body_snippet(response_body),
        )
    return None
