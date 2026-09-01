# Copyright (c) 2026 kraynux - Licence MIT
"""Contexte d'une requete (OMEGA-FUZZ_SPECIFICATIONS.md §11)."""
from __future__ import annotations

from dataclasses import dataclass

from omega_fuzz.domain.requests.request_phase import RequestPhase
from omega_fuzz.domain.requests.request_purpose import RequestPurpose


@dataclass(frozen=True, slots=True)
class RequestContext:
    phase: RequestPhase
    module: str
    purpose: RequestPurpose
    target_id: str
    depth: int
