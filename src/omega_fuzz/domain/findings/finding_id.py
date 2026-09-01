# Copyright (c) 2026 kraynux - Licence MIT
"""Identifiant de finding, scan-scope et lisible — meme raisonnement que
`domain.tests.test_id`/`domain.requests.request_id` (pas soumis a D-006,
voir OMEGA-FUZZ_SPECIFICATIONS.md §12.1). Format deterministe : fonction
pure, aucune source d'entropie ni port necessaire."""
from __future__ import annotations


def build_finding_id(*, module: str, target_short: str, sequence: int) -> str:
    """`finding_<module>_<target_short>_<sequence:06d>`."""
    return f"finding_{module}_{target_short}_{sequence:06d}"
