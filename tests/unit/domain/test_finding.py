# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.core.errors import ValidationError
from omega_fuzz.domain.findings.evidence import Evidence
from omega_fuzz.domain.findings.finding import Finding
from omega_fuzz.domain.findings.finding_metadata import FindingMetadata
from omega_fuzz.domain.findings.finding_status import FindingStatus
from omega_fuzz.domain.findings.finding_target import FindingTarget
from omega_fuzz.domain.findings.scoring import Scoring
from omega_fuzz.domain.findings.severity import Severity

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _finding(**overrides: object) -> Finding:
    defaults: dict[str, object] = {
        "finding_id": "finding_sigxss_example_root_000001",
        "scan_id": "a1b2c3d4e5f64a7b8c9d0e1f2a3b4c5d",
        "title": "Reflection sur /search",
        "type": "reflected_xss",
        "status": FindingStatus.SUSPECTED,
        "severity_auto": Severity.MEDIUM,
        "target": FindingTarget(
            url="https://example.com/search", endpoint="/search", method="GET", parameter="q"
        ),
        "evidence": Evidence(
            request_id="req_sigxss_example_root_000001_0001",
            test_id="test_sigxss_example_root_000001",
            observed_behavior="reflechi",
            evidence_summary="<script>alert('m')</script>",
        ),
        "scoring": Scoring(impact=3, exploitability=4, scope=2, raw_score=9),
        "metadata": FindingMetadata(
            module="sigxss", timestamp=NOW, confidence=ConfidenceLevel.CORROBORATED
        ),
    }
    defaults.update(overrides)
    return Finding(**defaults)  # type: ignore[arg-type]


def test_severity_defaults_to_auto_without_override() -> None:
    finding = _finding()
    assert finding.severity is Severity.MEDIUM


def test_severity_override_without_reason_raises() -> None:
    with pytest.raises(ValidationError):
        _finding(severity_override=Severity.HIGH)


def test_severity_override_with_reason_is_reflected() -> None:
    finding = _finding(severity_override=Severity.HIGH, severity_override_reason="confirme manuellement")
    assert finding.severity is Severity.HIGH
    assert finding.severity_auto is Severity.MEDIUM  # conserve pour tracabilite
