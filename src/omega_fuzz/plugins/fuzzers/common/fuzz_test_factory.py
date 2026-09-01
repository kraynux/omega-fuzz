# Copyright (c) 2026 kraynux - Licence MIT
"""Construction du `Test` partagee par les 4 fuzzers de Phase 7a
(OMEGA-FUZZ_ARBORESCENCE.md §30). Fonction pure : prend des types
domaine, retourne un type domaine — aucune dependance a un port ou a
`application`."""
from __future__ import annotations

from datetime import datetime

from omega_fuzz.domain.tests.test import Test, TestTarget
from omega_fuzz.domain.tests.test_id import build_test_id
from omega_fuzz.domain.tests.test_type import TestType


def build_fuzz_test(
    *,
    module: str,
    subtype: str,
    target_short: str,
    sequence: int,
    url: str,
    method: str,
    endpoint: str,
    parameters: tuple[str, ...],
    description: str,
    now: datetime,
) -> Test:
    test_id = build_test_id(module=module, target_short=target_short, sequence=sequence)
    return Test(
        test_id=test_id,
        type=TestType.FUZZ,
        subtype=subtype,
        module=module,
        target=TestTarget(url=url, method=method, endpoint=endpoint, parameters=parameters),
        description=description,
        created_at=now,
    )
