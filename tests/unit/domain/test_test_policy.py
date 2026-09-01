# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import pytest

from omega_fuzz.domain.tests.test_policy import is_valid_transition
from omega_fuzz.domain.tests.test_status import TestStatus


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (TestStatus.PLANNED, TestStatus.RUNNING),
        (TestStatus.PLANNED, TestStatus.ABORTED),
        (TestStatus.RUNNING, TestStatus.COMPLETED),
        (TestStatus.RUNNING, TestStatus.ABORTED),
        (TestStatus.RUNNING, TestStatus.INCONCLUSIVE),
    ],
)
def test_valid_transitions(current: TestStatus, target: TestStatus) -> None:
    assert is_valid_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (TestStatus.PLANNED, TestStatus.COMPLETED),
        (TestStatus.COMPLETED, TestStatus.RUNNING),
        (TestStatus.ABORTED, TestStatus.RUNNING),
    ],
)
def test_invalid_transitions(current: TestStatus, target: TestStatus) -> None:
    assert not is_valid_transition(current, target)
