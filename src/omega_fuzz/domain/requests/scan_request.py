# Copyright (c) 2026 kraynux - Licence MIT
"""Requete avant emission (OMEGA-FUZZ_SPECIFICATIONS.md §11, modele
`HttpRequest` — nomme `ScanRequest` ici pour suivre le nom de fichier
propre a omega-fuzz, OMEGA-FUZZ_PLAN_DEV.md §3). Une requete `test` doit
avoir un `test_id` non nul ; une requete `discovery` peut en avoir un
(test de decouverte) mais ce n'est pas obligatoire."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

from omega_fuzz.domain.requests.request_context import RequestContext
from omega_fuzz.domain.requests.request_metadata import RequestMetadata
from omega_fuzz.domain.requests.request_phase import RequestPhase


@dataclass(frozen=True, slots=True)
class ScanRequest:
    request_id: str
    method: str
    url: str
    normalized_url: str
    context: RequestContext
    created_at: datetime
    test_id: str | None = None
    headers: Mapping[str, str] = field(default_factory=dict)
    body: str | bytes | None = None
    metadata: RequestMetadata = field(default_factory=RequestMetadata)
    sent_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.context.phase is RequestPhase.TEST and not self.test_id:
            raise ValueError("une requete de phase 'test' doit avoir un test_id non nul")
