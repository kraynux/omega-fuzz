# Copyright (c) 2026 kraynux - Licence MIT
"""Metadonnees d'un finding (OMEGA-FUZZ_SPECIFICATIONS.md §28.1)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from omega_lib.core.confidence import ConfidenceLevel


@dataclass(frozen=True, slots=True)
class FindingMetadata:
    module: str
    timestamp: datetime
    confidence: ConfidenceLevel
