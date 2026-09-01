# Copyright (c) 2026 kraynux - Licence MIT
"""Implemente ports/confirmation_provider.py::ConfirmationProvider pour
la CLI (OMEGA-FUZZ_ARBORESCENCE.md §27, OMEGA-FUZZ_SPECIFICATIONS.md
§16.1) : vit dans `interfaces/cli/` plutot que `infrastructure/` — une
interaction stdin/stdout n'est pas un adaptateur vers un systeme
externe. Deux paliers : `required_phrase` fourni exige une saisie
exacte, sensible a la casse (confirmation renforcee, §16.1) ; sinon un
simple oui/non suffit."""
from __future__ import annotations

_ACCEPTED_SIMPLE_ANSWERS = frozenset({"oui", "o", "yes", "y"})


class CliConfirmationPrompt:
    """Implemente ports/confirmation_provider.py::ConfirmationProvider."""

    def confirm(self, *, message: str, required_phrase: str | None = None) -> bool:
        print(f"\n{message}\n")
        if required_phrase is not None:
            answer = input(f"Tapez exactement : {required_phrase}\n> ")
            return answer == required_phrase
        answer = input("Confirmer le lancement ? [oui/non] > ")
        return answer.strip().lower() in _ACCEPTED_SIMPLE_ANSWERS
