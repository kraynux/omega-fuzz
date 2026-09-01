# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/access_control_analyzer.py::AccessControlAnalyzer."""
from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.domain.findings.observation import Observation
from omega_fuzz.domain.services.redaction_service import redact_body_snippet

if TYPE_CHECKING:
    from omega_fuzz.ports.http_client import HttpResponse

_DEFAULT_DENIAL_STATUS_CODES: tuple[int, ...] = (401, 403, 404)


class HttpAccessControlAnalyzer:
    """Implemente ports/access_control_analyzer.py::AccessControlAnalyzer."""

    def check(
        self,
        *,
        response: HttpResponse,
        request_id: str,
        expected_denial_status_codes: Sequence[int] = _DEFAULT_DENIAL_STATUS_CODES,
    ) -> Observation | None:
        if response.fetch_error is not None:
            return None
        if response.status_code in expected_denial_status_codes:
            return None
        return Observation(
            kind="unauthorized_access",
            description=(
                f"Reponse {response.status_code} obtenue alors qu'un refus etait attendu "
                f"({tuple(expected_denial_status_codes)})"
            ),
            confidence=ConfidenceLevel.VERIFIED,
            request_id=request_id,
            evidence_summary=redact_body_snippet(response.body.decode("utf-8", errors="replace")),
        )
