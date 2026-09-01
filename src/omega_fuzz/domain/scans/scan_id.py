# Copyright (c) 2026 kraynux - Licence MIT
"""Identifiant racine d'agregat, conforme D-006
(OMEGA-FUZZ_SPECIFICATIONS.md §12.1) : UUID string genere en production
via `omega_lib.shared.ids.new_id()` (`ports.id_generator.IdGenerator`).
Jamais reconstruit depuis la cible ou la date."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScanId:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("scan_id must not be empty")
