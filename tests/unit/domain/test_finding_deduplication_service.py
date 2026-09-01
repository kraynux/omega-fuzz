# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.domain.findings.evidence import Evidence
from omega_fuzz.domain.findings.finding import Finding
from omega_fuzz.domain.findings.finding_metadata import FindingMetadata
from omega_fuzz.domain.findings.finding_status import FindingStatus
from omega_fuzz.domain.findings.finding_target import FindingTarget
from omega_fuzz.domain.findings.scoring import Scoring
from omega_fuzz.domain.findings.severity import Severity
from omega_fuzz.domain.services.finding_deduplication_service import deduplicate_findings

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _finding(
    *,
    finding_id: str,
    type_: str = "reflected_xss",
    endpoint: str = "/search",
    parameter: str | None = "q",
    confidence: ConfidenceLevel = ConfidenceLevel.INFERRED,
    raw_score: int = 9,
) -> Finding:
    return Finding(
        finding_id=finding_id,
        scan_id="scan1",
        title="t",
        type=type_,
        status=FindingStatus.SUSPECTED,
        severity_auto=Severity.MEDIUM,
        target=FindingTarget(url="https://example.com" + endpoint, endpoint=endpoint, method="GET", parameter=parameter),
        evidence=Evidence(request_id="req1", test_id="test1", observed_behavior="x", evidence_summary="y"),
        scoring=Scoring(impact=3, exploitability=4, scope=2, raw_score=raw_score),
        metadata=FindingMetadata(module="sigxss", timestamp=NOW, confidence=confidence),
    )


def test_identical_type_endpoint_parameter_are_merged_keeping_best_confidence() -> None:
    weak = _finding(finding_id="f1", confidence=ConfidenceLevel.INFERRED)
    strong = _finding(finding_id="f2", confidence=ConfidenceLevel.CORROBORATED)

    result = deduplicate_findings([weak, strong])

    assert len(result) == 1
    assert result[0].finding_id == "f2"


def test_tie_break_by_raw_score_when_confidence_equal() -> None:
    lower = _finding(finding_id="f1", confidence=ConfidenceLevel.VERIFIED, raw_score=7)
    higher = _finding(finding_id="f2", confidence=ConfidenceLevel.VERIFIED, raw_score=11)

    result = deduplicate_findings([lower, higher])

    assert len(result) == 1
    assert result[0].finding_id == "f2"


def test_different_endpoint_stays_separate() -> None:
    a = _finding(finding_id="f1", endpoint="/search")
    b = _finding(finding_id="f2", endpoint="/other")

    result = deduplicate_findings([a, b])

    assert len(result) == 2


def test_different_type_stays_separate() -> None:
    a = _finding(finding_id="f1", type_="reflected_xss")
    b = _finding(finding_id="f2", type_="generic_injection")

    result = deduplicate_findings([a, b])

    assert len(result) == 2


def test_different_parameter_stays_separate() -> None:
    a = _finding(finding_id="f1", parameter="q")
    b = _finding(finding_id="f2", parameter="page")

    result = deduplicate_findings([a, b])

    assert len(result) == 2


def test_empty_list_returns_empty() -> None:
    assert deduplicate_findings([]) == ()
