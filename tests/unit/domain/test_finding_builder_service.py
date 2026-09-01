# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.domain.findings.observation import Observation
from omega_fuzz.domain.findings.severity import Severity
from omega_fuzz.domain.services.finding_builder_service import (
    build_finding,
    build_findings_from_observations,
)
from omega_fuzz.domain.services.severity_service import (
    map_score_to_severity,
    score_for_observation_kind,
)
from omega_fuzz.domain.tests.test import Test, TestTarget
from omega_fuzz.domain.tests.test_type import TestType

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)

_TEST = Test(
    test_id="test_sigxss_example_root_000001",
    type=TestType.SIGNATURE,
    subtype="reflected_xss",
    module="sigxss",
    target=TestTarget(url="https://example.com/search?q=x", method="GET", endpoint="/search", parameters=("q",)),
    description="Signature XSS reflechie sur q",
    created_at=NOW,
)


def _observation(*, request_id: str = "req_sigxss_example_root_000001_0001") -> Observation:
    return Observation(
        kind="reflection",
        description="Payload reflete",
        confidence=ConfidenceLevel.CORROBORATED,
        request_id=request_id,
        evidence_summary="<script>alert('m')</script>",
    )


def test_finding_id_is_scan_scoped_and_readable() -> None:
    finding = build_finding(
        scan_id="scan1", test=_TEST, observation=_observation(), target_short="example_root", sequence=1, now=NOW
    )
    assert finding.finding_id == "finding_sigxss_example_root_000001"


def test_finding_links_test_id_and_request_id() -> None:
    finding = build_finding(
        scan_id="scan1", test=_TEST, observation=_observation(), target_short="example_root", sequence=1, now=NOW
    )
    assert finding.evidence.test_id == _TEST.test_id
    assert finding.evidence.request_id == "req_sigxss_example_root_000001_0001"


def test_severity_auto_is_reproducible_and_matches_severity_service() -> None:
    finding = build_finding(
        scan_id="scan1", test=_TEST, observation=_observation(), target_short="example_root", sequence=1, now=NOW
    )
    scoring = score_for_observation_kind("reflection")
    assert finding.scoring == scoring
    assert finding.severity_auto is map_score_to_severity(scoring.raw_score)
    assert finding.severity_auto is Severity.MEDIUM


def test_status_defaults_to_suspected() -> None:
    finding = build_finding(
        scan_id="scan1", test=_TEST, observation=_observation(), target_short="example_root", sequence=1, now=NOW
    )
    assert finding.status.value == "suspected"


def test_build_findings_from_observations_deduplicates() -> None:
    observations = [
        _observation(request_id="req_sigxss_example_root_000001_0001"),
        _observation(request_id="req_sigxss_example_root_000001_0002"),
    ]
    findings = build_findings_from_observations(
        scan_id="scan1", test=_TEST, observations=observations, target_short="example_root", now=NOW
    )
    # meme type/endpoint/parametre pour les 2 observations -> dedupliquees en 1
    assert len(findings) == 1
