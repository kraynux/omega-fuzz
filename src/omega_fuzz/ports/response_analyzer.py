# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'analyse de reponses/anomalies (OMEGA-FUZZ_ARBORESCENCE.md
§15.3, §22). Revision Phase 7b : retourne des `Observation` structurees
(le type `Sequence[str]` de la Phase 0 etait un placeholder avant que
`domain.findings.Observation` existe) ; `payload_value`/
`detection_pattern` permettent a l'implementation de savoir quoi
chercher dans la reponse. `baseline` retire (n'etait utilise par aucune
implementation — le seul consommateur envisage etait un analyseur de
timing, differe, voir le plan Phase 7b ; sera reintroduit si un besoin
reel se presente)."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from omega_fuzz.domain.findings.observation import Observation
from omega_fuzz.ports.http_client import HttpResponse


class ResponseAnalyzer(Protocol):
    def analyze(
        self,
        *,
        response: HttpResponse,
        request_id: str,
        payload_value: str | None = None,
        detection_pattern: str | None = None,
    ) -> Sequence[Observation]: ...
