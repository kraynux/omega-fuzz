# Copyright (c) 2026 kraynux - Licence MIT
"""Racine des erreurs metier du domaine (meme motif D-007 que
core/errors.py — voir OMEGA-FUZZ_ARBORESCENCE.md §5.3/§6)."""
from __future__ import annotations

from omega_fuzz.core.errors import OmegaFuzzError


class DomainError(OmegaFuzzError):
    """Racine des erreurs metier (scope, profondeur, limites...)."""
