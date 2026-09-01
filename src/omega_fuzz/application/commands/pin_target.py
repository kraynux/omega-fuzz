# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : enregistrer une cible favorite (ecran Cibles, Phase 10j).
Normalise via `normalize_url` avant stockage (memes erreurs que
`prepare_scan` sur une URL invalide) — jamais l'URL brute telle que
tapee, pour eviter des doublons "http://x.com" / "http://x.com/"."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_fuzz.domain.services.url_normalization_service import normalize_url

if TYPE_CHECKING:
    from omega_fuzz.ports.target_repository import TargetRepository


def pin_target(*, target_repository: TargetRepository, raw_url: str) -> str:
    normalized = normalize_url(raw_url)
    url = normalized.to_str()
    target_repository.add(url)
    return url
