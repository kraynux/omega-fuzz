# Copyright (c) 2026 kraynux - Licence MIT
"""Raison de terminaison d'un scan (OMEGA-FUZZ_SPECIFICATIONS.md §14.5,
OMEGA-FUZZ_PLAN_DEV.md Phase 3 : « l'etat final contient la limite
atteinte, la valeur configuree et la valeur observee »). `limit_name`/
`configured_value`/`observed_value` ne sont renseignes que pour
`LIMIT_REACHED` ; `None` pour les autres triggers."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from omega_fuzz.shared.i18n import _


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
        return _("Scan terminé normalement, aucune limite atteinte.")
    if termination.trigger is TerminationTrigger.MANUAL_STOP:
        return _("Arrêt manuel demandé par l'utilisateur.")
    if termination.trigger is TerminationTrigger.LIMIT_REACHED:
        return (
            _("Limite `{limit_name}` atteinte (configurée : {configured_value}, observée : "
              "{observed_value}).").format(limit_name=termination.limit_name, configured_value=termination.configured_value, observed_value=termination.observed_value)
        )
    if termination.trigger is TerminationTrigger.CONFIG_ERROR:
        return _("Arrêt avant obtention de résultats exploitables (erreur de configuration).")
    if termination.trigger is TerminationTrigger.TECHNICAL_FAILURE:
        return _("Erreur technique fatale en cours d'exécution.")
    return termination.trigger.value
