# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de gestion de session/authentification
(OMEGA-FUZZ_ARBORESCENCE.md §15.3, §45). Fournit/rafraichit l'etat
d'authentification (cookies, tokens, headers additionnels) a injecter
dans une requete de decouverte ou de test authentifiee. Necessaire des
la decouverte authentifiee (Phase 4) et obligatoire avant toute
implementation IDOR/logic_tests (Phase 7c).

Revision Phase 4 : une seule methode `get_session` (fournit ET
rafraichit en interne si besoin) remplace les deux methodes `apply`/
`refresh` de la Phase 0, qui anticipaient a tort la forme exacte du
contrat avant que `domain.auth.Session` existe.

Revision Phase 7c : `get_session` devient `async` — le mode `login_form`
(OMEGA-FUZZ_ARBORESCENCE.md §45.5) necessite une vraie requete HTTP
(POST vers `login_url`), impossible a exprimer avec une methode
synchrone."""
from __future__ import annotations

from typing import Protocol

from omega_fuzz.domain.auth.session import Session


class SessionProvider(Protocol):
    async def get_session(self) -> Session: ...
