# Copyright (c) 2026 kraynux - Licence MIT
"""Identifiant de requete, scan-scope et lisible
(OMEGA-FUZZ_SPECIFICATIONS.md §12.4 — `req_<module>_<target_short>_
<test_sequence>_<request_sequence>`, pas soumis a D-006, voir
domain.scans.scan_id). Format deterministe : `build_request_id` est une
fonction pure, aucune source d'entropie ni port necessaire."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RequestId:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("request_id must not be empty")


def build_request_id(
    *, module: str, target_short: str, test_sequence: int, request_sequence: int
) -> str:
    """`req_<module>_<target_short>_<test_sequence:06d>_
    <request_sequence:04d>` (OMEGA-FUZZ_SPECIFICATIONS.md §12.4, exemple :
    `req_fuzzhttp_example_root_000001_0001`)."""
    return f"req_{module}_{target_short}_{test_sequence:06d}_{request_sequence:04d}"
