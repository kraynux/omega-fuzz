# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'analyse de controle d'acces (OMEGA-FUZZ_PLAN_DEV.md
Phase 7c, point 10). Distinct de `ports.response_analyzer.ResponseAnalyzer`
(Phase 7b, oriente reflexion/erreur de payload) — les tests de
`plugins/logic_tests/` n'envoient pas de payload, juste une session
authentifiee ; la question posee est « le code de reponse indique-t-il
un refus attendu, ou un acces obtenu a tort ? »."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from omega_fuzz.domain.findings.observation import Observation
from omega_fuzz.ports.http_client import HttpResponse


class AccessControlAnalyzer(Protocol):
    def check(
        self,
        *,
        response: HttpResponse,
        request_id: str,
        expected_denial_status_codes: Sequence[int] = (401, 403, 404),
    ) -> Observation | None: ...
