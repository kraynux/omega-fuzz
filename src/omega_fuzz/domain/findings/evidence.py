# Copyright (c) 2026 kraynux - Licence MIT
"""Preuve associee a un finding (OMEGA-FUZZ_SPECIFICATIONS.md §28.1).
`evidence_summary` est deja expurge/tronque au moment ou l'`Observation`
source a ete construite (`domain.services.redaction_service`) — jamais
de secret brut ici."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Evidence:
    request_id: str
    test_id: str
    observed_behavior: str
    evidence_summary: str
    truncated: bool = False
