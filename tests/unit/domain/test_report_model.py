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
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.reports.report_model import (
    build_report_header,
    count_tests_by_type,
    findings_by_severity,
    requests_by_module,
)
from omega_fuzz.domain.services.profile_resolution_service import resolve_preset
from omega_fuzz.domain.services.url_normalization_service import normalize_url
from omega_fuzz.domain.tests.test import Test, TestTarget
from omega_fuzz.domain.tests.test_type import TestType

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _test(*, module: str, type_: TestType, requests_count: int) -> Test:
    return Test(
        test_id=f"test_{module}_example_root_000001",
        type=type_,
        subtype="x",
        module=module,
        target=TestTarget(url="https://example.com/x", method="GET", endpoint="/x"),
        description="d",
        created_at=NOW,
        requests_count=requests_count,
    )


def _finding(severity: Severity) -> Finding:
    return Finding(
        finding_id="finding_1",
        scan_id="scan1",
        title="t",
        type="reflected_xss",
        status=FindingStatus.SUSPECTED,
        severity_auto=severity,
        target=FindingTarget(url="https://example.com", endpoint="/x", method="GET"),
        evidence=Evidence(request_id="req1", test_id="test1", observed_behavior="x", evidence_summary="y"),
        scoring=Scoring(impact=1, exploitability=1, scope=1, raw_score=3),
        metadata=FindingMetadata(module="sigxss", timestamp=NOW, confidence=ConfidenceLevel.INFERRED),
    )


def test_requests_by_module_sums_per_module() -> None:
    tests = [
        _test(module="crawler", type_=TestType.OTHER, requests_count=3),
        _test(module="fuzzhttp", type_=TestType.FUZZ, requests_count=10),
        _test(module="fuzzhttp", type_=TestType.FUZZ, requests_count=5),
    ]
    result = requests_by_module(tests)
    assert result == {"crawler": 3, "fuzzhttp": 15}


def test_count_tests_by_type_counts_occurrences() -> None:
    tests = [
        _test(module="fuzzhttp", type_=TestType.FUZZ, requests_count=1),
        _test(module="sigxss", type_=TestType.SIGNATURE, requests_count=1),
        _test(module="fuzzhttp", type_=TestType.FUZZ, requests_count=1),
    ]
    result = count_tests_by_type(tests)
    assert result == {"fuzz": 2, "signature": 1}


def test_findings_by_severity_includes_all_levels_at_zero() -> None:
    findings = [_finding(Severity.HIGH), _finding(Severity.HIGH), _finding(Severity.LOW)]
    result = findings_by_severity(findings)
    assert result == {"critical": 0, "high": 2, "medium": 0, "low": 1}


def test_build_report_header_derives_preset_name() -> None:
    entry_url = normalize_url("https://example.com/")
    configuration = resolve_preset(PresetName.PROD_SAFE, entry_url=entry_url)

    header = build_report_header(
        scan_id="scan1",
        version="0.1.0",
        target_url="https://example.com/",
        configuration=configuration,
        catalog_versions={"xss": "1.0.0"},
        verify_tls=True,
        now=NOW,
    )

    assert header.preset == "prod-safe"
    assert header.tls_verification_enabled is True


def test_build_report_header_derives_custom_when_no_preset() -> None:
    from omega_fuzz.domain.profiles.aggressiveness_level import AggressivenessLevel
    from omega_fuzz.domain.profiles.scope_profile import ScopeProfileName
    from omega_fuzz.domain.services.profile_resolution_service import resolve_manual

    entry_url = normalize_url("https://example.com/")
    configuration = resolve_manual(
        entry_url=entry_url,
        aggressiveness=AggressivenessLevel.STANDARD,
        scope_profile=ScopeProfileName.STANDARD,
    )

    header = build_report_header(
        scan_id="scan1",
        version="0.1.0",
        target_url="https://example.com/",
        configuration=configuration,
        catalog_versions={},
        verify_tls=False,
        now=NOW,
    )

    assert header.preset == "custom"
    assert header.tls_verification_enabled is False
