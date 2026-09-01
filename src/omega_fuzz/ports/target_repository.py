# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de persistance des cibles favorites (Phase 10j, ecran Cibles).
Concept absent des documents OMEGA-FUZZ_* d'origine (herite du menu de
reference CHECK/omega-scan, adapte : des URLs completes, pas des
IP/hosts nus)."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class TargetRepository(Protocol):
    def add(self, url: str) -> None: ...

    def remove(self, url: str) -> None: ...

    def list_all(self) -> Sequence[str]: ...
