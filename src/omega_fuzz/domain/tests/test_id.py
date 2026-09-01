# Copyright (c) 2026 kraynux - Licence MIT
"""Identifiant de test, scan-scope et lisible
(OMEGA-FUZZ_SPECIFICATIONS.md §12.3 — `test_<module>_<target_short>_
<sequence>`, pas soumis a D-006, voir domain.scans.scan_id). Format
deterministe : `build_test_id` est une fonction pure, aucune source
d'entropie ni port necessaire."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TestId:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("test_id must not be empty")


def build_test_id(*, module: str, target_short: str, sequence: int) -> str:
    """`test_<module>_<target_short>_<sequence:06d>`
    (OMEGA-FUZZ_SPECIFICATIONS.md §12.3, exemple :
    `test_fuzzhttp_example_root_000001`)."""
    return f"test_{module}_{target_short}_{sequence:06d}"
