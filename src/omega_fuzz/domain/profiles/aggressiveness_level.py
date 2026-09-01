# Copyright (c) 2026 kraynux - Licence MIT
"""Niveaux d'agressivite (OMEGA-FUZZ_SPECIFICATIONS.md §15)."""
from __future__ import annotations

from enum import Enum


class AggressivenessLevel(str, Enum):
    DOUX = "doux"
    STANDARD = "standard"
    AGRESSIF = "agressif"
    VIOLENT = "violent"
