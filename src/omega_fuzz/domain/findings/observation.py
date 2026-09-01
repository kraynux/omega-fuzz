# Copyright (c) 2026 kraynux - Licence MIT
"""Observation structuree produite par un analyseur de reponse
(OMEGA-FUZZ_ARBORESCENCE.md §22 : « les analyseurs doivent retourner
des observations structurees »). Ouvrait `domain/findings/` a minima en
Phase 7b — le modele `Finding` complet (scoring CWE/OWASP,
deduplication) est construit en Phase 8 a partir de ces observations.

`confidence` reutilise `omega_lib.core.confidence.ConfidenceLevel`
(D-005) — sa semantique (VERIFIED/DECLARED/CORROBORATED/INFERRED/
UNKNOWN, « nature de la preuve », pas juste son degre) correspond bien
a la distinction entre un fait directement observe (ex. code HTTP 5xx,
header absent) et une simple heuristique (ex. reflexion par simple
sous-chaine).

`evidence_summary` (Phase 8) : extrait de reponse deja expurge/tronque
(`domain.services.redaction_service`), peuple par l'analyseur qui a
construit l'observation — lui seul a acces a la reponse HTTP brute.
Champ additif (defaut vide), aucune rupture des tests Phase 7b/7c
existants."""
from __future__ import annotations

from dataclasses import dataclass

from omega_lib.core.confidence import ConfidenceLevel


@dataclass(frozen=True, slots=True)
class Observation:
    kind: str
    description: str
    confidence: ConfidenceLevel
    request_id: str
    evidence_summary: str = ""
