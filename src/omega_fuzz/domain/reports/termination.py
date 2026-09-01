# Copyright (c) 2026 kraynux - Licence MIT
"""Raison de terminaison d'un scan (OMEGA-FUZZ_SPECIFICATIONS.md §14.5,
OMEGA-FUZZ_PLAN_DEV.md Phase 3 : « l'etat final contient la limite
atteinte, la valeur configuree et la valeur observee »). `limit_name`/
`configured_value`/`observed_value` ne sont renseignes que pour
`LIMIT_REACHED` ; `None` pour les autres triggers."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TerminationTrigger(str, Enum):
    COMPLETED_NORMALLY = "completed_normally"
    LIMIT_REACHED = "limit_reached"
    MANUAL_STOP = "manual_stop"
    CONFIG_ERROR = "config_error"
    TECHNICAL_FAILURE = "technical_failure"


@dataclass(frozen=True, slots=True)
class TerminationReason:
    trigger: TerminationTrigger
    limit_name: str | None = None
    configured_value: int | None = None
    observed_value: int | None = None


def describe_termination(termination: TerminationReason) -> str:
    """Phrase lisible pour les rapports (Markdown/HTML, Phase 9) —
    colocalisee avec `TerminationReason` pour eviter de dupliquer cette
    logique de formatage entre exporters."""
    if termination.trigger is TerminationTrigger.COMPLETED_NORMALLY:
        return "Scan termine normalement, aucune limite atteinte."
    if termination.trigger is TerminationTrigger.MANUAL_STOP:
        return "Arret manuel demande par l'utilisateur."
    if termination.trigger is TerminationTrigger.LIMIT_REACHED:
        return (
            f"Limite `{termination.limit_name}` atteinte (configuree : "
            f"{termination.configured_value}, observee : {termination.observed_value})."
        )
    if termination.trigger is TerminationTrigger.CONFIG_ERROR:
        return "Arret avant obtention de resultats exploitables (erreur de configuration)."
    if termination.trigger is TerminationTrigger.TECHNICAL_FAILURE:
        return "Erreur technique fatale en cours d'execution."
    return termination.trigger.value
