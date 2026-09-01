# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_fuzz.core.result import Result


def test_success_carries_value() -> None:
    result = Result.success(42)
    assert result.is_success
    assert not result.is_failure
    assert not result.is_partial
    assert result.value == 42
    assert result.reason is None


def test_failure_carries_reason() -> None:
    result: Result[int] = Result.failure("boom")
    assert result.is_failure
    assert result.value is None
    assert result.reason == "boom"


def test_partial_carries_value_and_reason() -> None:
    result = Result.partial(["a"], "truncated")
    assert result.is_partial
    assert result.value == ["a"]
    assert result.reason == "truncated"
