# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/response_analyzer.py::ResponseAnalyzer en combinant
les detecteurs individuels (OMEGA-FUZZ_ARBORESCENCE.md §22 : « les
analyseurs doivent retourner des observations structurees »). L'analyse
de headers de securite est optionnelle (`security_headers_catalog`
absent = pas verifiee) — elle n'a de sens que pour un test qui la cible
explicitement, pas pour chaque requete de fuzzing generique."""
from __future__ import annotations

from collections.abc import Sequence

from omega_fuzz.domain.findings.observation import Observation
from omega_fuzz.domain.findings.payload_catalog import SecurityHeadersCatalog
from omega_fuzz.infrastructure.analyzers.error_detector import detect_error
from omega_fuzz.infrastructure.analyzers.header_analyzer import analyze_headers
from omega_fuzz.infrastructure.analyzers.reflection_detector import detect_reflection
from omega_fuzz.ports.http_client import HttpResponse


class CompositeResponseAnalyzer:
    """Implemente ports/response_analyzer.py::ResponseAnalyzer."""

    def __init__(self, *, security_headers_catalog: SecurityHeadersCatalog | None = None) -> None:
        self._security_headers_catalog = security_headers_catalog

    def analyze(
        self,
        *,
        response: HttpResponse,
        request_id: str,
        payload_value: str | None = None,
        detection_pattern: str | None = None,
    ) -> Sequence[Observation]:
        if response.fetch_error is not None:
            return ()

        body = response.body.decode("utf-8", errors="replace")
        observations: list[Observation] = []

        reflection = detect_reflection(
            response_body=body,
            request_id=request_id,
            payload_value=payload_value,
            detection_pattern=detection_pattern,
        )
        if reflection is not None:
            observations.append(reflection)

        error = detect_error(status_code=response.status_code, response_body=body, request_id=request_id)
        if error is not None:
            observations.append(error)

        if self._security_headers_catalog is not None:
            observations.extend(
                analyze_headers(
                    headers=response.headers,
                    catalog=self._security_headers_catalog,
                    request_id=request_id,
                )
            )

        return tuple(observations)
