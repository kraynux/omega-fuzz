# Copyright (c) 2026 kraynux - Licence MIT
"""Verification des headers de securite (OMEGA-FUZZ_PLAN_DEV.md
Phase 7b point 9). Un header absent est un fait directement observe
(`VERIFIED`) ; une valeur inattendue est declaree par la cible elle-meme
dans un champ qu'elle controle (`DECLARED`, plausible mais falsifiable
— meme semantique que `omega_lib.core.confidence`)."""
from __future__ import annotations

from collections.abc import Mapping

from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.domain.findings.observation import Observation
from omega_fuzz.domain.findings.payload_catalog import SecurityHeadersCatalog
from omega_fuzz.domain.services.redaction_service import redact_headers


def analyze_headers(
    *, headers: Mapping[str, str], catalog: SecurityHeadersCatalog, request_id: str
) -> tuple[Observation, ...]:
    lowered_headers = {name.lower(): value for name, value in headers.items()}
    evidence_summary = ", ".join(
        f"{name}: {value}" for name, value in redact_headers(headers).items()
    )
    observations: list[Observation] = []

    for required in catalog.required_headers:
        key = required.name.lower()
        if key not in lowered_headers:
            observations.append(
                Observation(
                    kind="missing_security_header",
                    description=f"Header de securite absent : {required.name}",
                    confidence=ConfidenceLevel.VERIFIED,
                    request_id=request_id,
                    evidence_summary=evidence_summary,
                )
            )
        elif (
            required.expected_value is not None
            and lowered_headers[key].lower() != required.expected_value.lower()
        ):
            observations.append(
                Observation(
                    kind="misconfigured_security_header",
                    description=(
                        f"Header {required.name} : valeur inattendue "
                        f"({lowered_headers[key]!r}, attendu {required.expected_value!r})"
                    ),
                    confidence=ConfidenceLevel.DECLARED,
                    request_id=request_id,
                    evidence_summary=evidence_summary,
                )
            )

    return tuple(observations)
