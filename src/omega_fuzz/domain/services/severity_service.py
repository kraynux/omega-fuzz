# Copyright (c) 2026 kraynux - Licence MIT
"""Calcul de score et mapping vers la severite
(OMEGA-FUZZ_SPECIFICATIONS.md §30). `score_for_observation_kind`
implemente un mapping deliberement CONSERVATEUR (bas de fourchette du
tableau §31, "points de depart a ajuster") — aucune confirmation
humaine n'a eu lieu a ce stade automatique ; `severity_override` reste
le mecanisme pour un ajustement documente et justifie."""
from __future__ import annotations

from omega_fuzz.core.errors import ValidationError
from omega_fuzz.domain.findings.scoring import Scoring
from omega_fuzz.domain.findings.severity import Severity

# (impact, exploitability, scope) par Observation.kind — voir le plan
# Phase 8 pour la justification de chaque choix (ancrage sur les lignes
# les plus prudentes de OMEGA-FUZZ_SPECIFICATIONS.md §31).
_SCORE_BY_OBSERVATION_KIND: dict[str, tuple[int, int, int]] = {
    "reflection": (3, 4, 2),
    "error_disclosure": (2, 2, 3),
    "http_error": (2, 2, 3),
    "missing_security_header": (2, 2, 3),
    "misconfigured_security_header": (2, 2, 3),
    "unauthorized_access": (4, 4, 4),
}

_DEFAULT_SCORE: tuple[int, int, int] = (1, 1, 1)  # kind inconnu : le plus prudent possible


def compute_raw_score(*, impact: int, exploitability: int, scope: int) -> int:
    return impact + exploitability + scope


def map_score_to_severity(raw_score: int) -> Severity:
    if raw_score >= 13:
        return Severity.CRITICAL
    if raw_score >= 10:
        return Severity.HIGH
    if raw_score >= 7:
        return Severity.MEDIUM
    return Severity.LOW


def score_for_observation_kind(kind: str) -> Scoring:
    impact, exploitability, scope = _SCORE_BY_OBSERVATION_KIND.get(kind, _DEFAULT_SCORE)
    raw_score = compute_raw_score(impact=impact, exploitability=exploitability, scope=scope)
    return Scoring(impact=impact, exploitability=exploitability, scope=scope, raw_score=raw_score)


def apply_severity_override(
    finding_severity_override: Severity | None, reason: str | None
) -> None:
    """Valide la contrainte « tout override de severite possede une
    justification » — leve si un override est fourni sans raison.
    Utilise en amont de la construction du `Finding` (dont
    `__post_init__` applique la meme regle defensivement)."""
    if finding_severity_override is not None and not reason:
        raise ValidationError("severity_override necessite une severity_override_reason justifiee")
