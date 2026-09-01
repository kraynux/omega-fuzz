# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de fourniture de payloads/mutations de fuzzing
(OMEGA-FUZZ_ARBORESCENCE.md §15.3, §21). Les implementations concrètes
chargent des catalogues YAML strictement declaratifs (payloads + regles
de detection, jamais de code executable, `yaml.safe_load` — voir
OMEGA-FUZZ_SPECIFICATIONS.md §25.1) confines a `infrastructure.payloads`."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class PayloadProvider(Protocol):
    def payloads_for(self, *, category: str) -> Sequence[str]: ...

    def catalog_version(self, *, category: str) -> str: ...
