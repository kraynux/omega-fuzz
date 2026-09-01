# Copyright (c) 2026 kraynux - Licence MIT
"""Alias et types transverses partages (OMEGA-FUZZ_ARBORESCENCE.md
§5.3). Les alias generiques deja mutualises dans `omega_lib` (horloge,
generation d'identifiants, `ConfidenceLevel`) sont importes depuis
`omega_lib.shared.typing`/`omega_lib.core.confidence` la ou ils sont
consommes, pas re-declares ici."""
from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

Predicate = Callable[[T], bool]
