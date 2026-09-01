# Copyright (c) 2026 kraynux - Licence MIT
"""Mappe une erreur applicative/domaine vers un message clair (jamais
une trace brute) et le code de sortie associe
(OMEGA-FUZZ_ARBORESCENCE.md §27 : « presenter les erreurs sans
connaitre les adaptateurs concrets »)."""
from __future__ import annotations

from omega_fuzz.core.constants import CLI_EXIT_ERROR
from omega_fuzz.core.errors import OmegaFuzzError
from omega_fuzz.domain.targets.url import UrlNormalizationError


def render_error(error: Exception) -> tuple[str, int]:
    if isinstance(error, (OmegaFuzzError, UrlNormalizationError)):
        return f"Erreur : {error}", CLI_EXIT_ERROR
    raise error
