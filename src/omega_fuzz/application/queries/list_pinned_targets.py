# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : lister les cibles favorites (ecran Cibles, Phase 10j)."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from omega_fuzz.ports.target_repository import TargetRepository


def list_pinned_targets(*, target_repository: TargetRepository) -> Sequence[str]:
    return target_repository.list_all()
