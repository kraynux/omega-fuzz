# Copyright (c) 2026 kraynux - Licence MIT
"""Identifiant de cible, scan-scope et lisible (OMEGA-FUZZ_ARBORESCENCE.md
§8, PLAN_DEV §2.2, OMEGA-FUZZ_SPECIFICATIONS.md §12.2 —
`<host_short>_<context>`, pas soumis a D-006). Format deterministe :
`build_target_id` est une fonction pure, aucune source d'entropie ni
port necessaire (contrairement a `scan_id`, voir `domain.scans.scan_id`)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TargetId:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("target_id must not be empty")


def build_target_id(*, host: str, context: str = "root") -> str:
    """`<host_short>_<context>` (OMEGA-FUZZ_SPECIFICATIONS.md §12.2,
    exemples : `example_root`, `intranet_root`). `host_short` est le
    premier label du host (avant le premier point), ou le host entier
    s'il n'en contient pas."""
    host_short = host.split(".", 1)[0]
    return f"{host_short}_{context}"
