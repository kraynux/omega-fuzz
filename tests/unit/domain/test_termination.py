# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_fuzz.domain.reports.termination import (
    TerminationReason,
    TerminationTrigger,
    describe_termination,
)


def test_manual_stop_has_no_limit_fields() -> None:
    reason = TerminationReason(trigger=TerminationTrigger.MANUAL_STOP)
    assert reason.limit_name is None
    assert reason.configured_value is None
    assert reason.observed_value is None


def test_limit_reached_carries_configured_and_observed_values() -> None:
    reason = TerminationReason(
        trigger=TerminationTrigger.LIMIT_REACHED,
        limit_name="max_total_requests",
        configured_value=1000,
        observed_value=1000,
    )
    assert reason.limit_name == "max_total_requests"
    assert reason.configured_value == reason.observed_value == 1000


def test_describe_termination_covers_every_trigger() -> None:
    for trigger in TerminationTrigger:
        reason = TerminationReason(
            trigger=trigger,
            limit_name="max_total_requests" if trigger is TerminationTrigger.LIMIT_REACHED else None,
            configured_value=1000 if trigger is TerminationTrigger.LIMIT_REACHED else None,
            observed_value=1000 if trigger is TerminationTrigger.LIMIT_REACHED else None,
        )
        sentence = describe_termination(reason)
        assert isinstance(sentence, str)
        assert sentence


def test_describe_termination_limit_reached_mentions_limit_name_and_values() -> None:
    reason = TerminationReason(
        trigger=TerminationTrigger.LIMIT_REACHED,
        limit_name="max_total_requests",
        configured_value=1000,
        observed_value=1000,
    )
    sentence = describe_termination(reason)
    assert "max_total_requests" in sentence
    assert "1000" in sentence
