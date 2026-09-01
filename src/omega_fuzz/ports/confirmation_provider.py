# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'obtention d'une confirmation explicite
(OMEGA-FUZZ_ARBORESCENCE.md §15.3, §35). Couvre la confirmation simple et
la confirmation renforcee (profils violent/lab-extreme, verify_tls=false
— OMEGA-FUZZ_SPECIFICATIONS.md §16.1/§32.4) : `required_phrase` est
`None` pour une confirmation simple (accepte/refuse), ou la chaine exacte
que l'implementation CLI/TUI doit faire saisir a l'identique pour une
confirmation renforcee."""
from __future__ import annotations

from typing import Protocol


class ConfirmationProvider(Protocol):
    def confirm(self, *, message: str, required_phrase: str | None = None) -> bool: ...
