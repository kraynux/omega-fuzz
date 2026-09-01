# Copyright (c) 2026 kraynux - Licence MIT
"""Transitions legales de `TestStatus` (OMEGA-FUZZ_SPECIFICATIONS.md
§10.1)."""
from __future__ import annotations

from omega_fuzz.domain.tests.test_status import TestStatus

_TRANSITIONS: dict[TestStatus, frozenset[TestStatus]] = {
    TestStatus.PLANNED: frozenset({TestStatus.RUNNING, TestStatus.ABORTED}),
    TestStatus.RUNNING: frozenset(
        {TestStatus.COMPLETED, TestStatus.ABORTED, TestStatus.INCONCLUSIVE}
    ),
    TestStatus.COMPLETED: frozenset(),
    TestStatus.ABORTED: frozenset(),
    TestStatus.INCONCLUSIVE: frozenset(),
}


def is_valid_transition(current: TestStatus, target: TestStatus) -> bool:
    return target in _TRANSITIONS[current]
