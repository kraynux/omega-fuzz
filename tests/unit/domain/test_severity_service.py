# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import pytest

from omega_fuzz.core.errors import ValidationError
from omega_fuzz.domain.findings.severity import Severity
from omega_fuzz.domain.services.severity_service import (
    apply_severity_override,
    compute_raw_score,
    map_score_to_severity,
    score_for_observation_kind,
)


def test_compute_raw_score() -> None:
    assert compute_raw_score(impact=3, exploitability=4, scope=2) == 9


@pytest.mark.parametrize(
    ("raw_score", "expected"),
    [
        (15, Severity.CRITICAL),
        (13, Severity.CRITICAL),
        (12, Severity.HIGH),
        (10, Severity.HIGH),
        (9, Severity.MEDIUM),
        (7, Severity.MEDIUM),
        (6, Severity.LOW),
        (3, Severity.LOW),
    ],
)
def test_map_score_to_severity_boundaries(raw_score: int, expected: Severity) -> None:
    assert map_score_to_severity(raw_score) is expected


@pytest.mark.parametrize(
    "kind",
    [
        "reflection",
        "error_disclosure",
        "http_error",
        "missing_security_header",
        "misconfigured_security_header",
        "unauthorized_access",
    ],
)
def test_score_for_known_observation_kinds_is_within_valid_bounds(kind: str) -> None:
    scoring = score_for_observation_kind(kind)
    assert 1 <= scoring.impact <= 5
    assert 1 <= scoring.exploitability <= 5
    assert 1 <= scoring.scope <= 5
    assert scoring.raw_score == scoring.impact + scoring.exploitability + scoring.scope


def test_unauthorized_access_scores_high() -> None:
    scoring = score_for_observation_kind("unauthorized_access")
    assert map_score_to_severity(scoring.raw_score) is Severity.HIGH


def test_unknown_kind_gets_most_conservative_score() -> None:
    scoring = score_for_observation_kind("something_never_seen")
    assert scoring.raw_score == 3
    assert map_score_to_severity(scoring.raw_score) is Severity.LOW


def test_apply_severity_override_requires_reason() -> None:
    with pytest.raises(ValidationError):
        apply_severity_override(Severity.HIGH, None)
    with pytest.raises(ValidationError):
        apply_severity_override(Severity.HIGH, "")


def test_apply_severity_override_accepts_justified_override() -> None:
    apply_severity_override(Severity.HIGH, "confirme manuellement apres revue")
    apply_severity_override(None, None)  # pas d'override : toujours valide
