# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : retirer une cible favorite (ecran Cibles, Phase 10j)."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omega_fuzz.ports.target_repository import TargetRepository


def unpin_target(*, target_repository: TargetRepository, url: str) -> None:
    target_repository.remove(url)
