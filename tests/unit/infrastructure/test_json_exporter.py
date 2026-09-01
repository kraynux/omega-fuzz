# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.domain.findings.evidence import Evidence
from omega_fuzz.domain.findings.finding import Finding
from omega_fuzz.domain.findings.finding_metadata import FindingMetadata
from omega_fuzz.domain.findings.finding_status import FindingStatus
from omega_fuzz.domain.findings.finding_target import FindingTarget
from omega_fuzz.domain.findings.scoring import Scoring
from omega_fuzz.domain.findings.severity import Severity
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.reports.report_model import ReportModel, build_report_header
from omega_fuzz.domain.reports.scan_statistics import ScanStatistics
from omega_fuzz.domain.reports.termination import TerminationReason, TerminationTrigger
from omega_fuzz.domain.services.profile_resolution_service import resolve_preset
from omega_fuzz.domain.services.url_normalization_service import normalize_url
from omega_fuzz.infrastructure.exporters.json_exporter import JsonReportExporter

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _report() -> ReportModel:
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
    finding = Finding(
        finding_id="finding_1",
        scan_id="scan1",
        title="Reflection sur /search",
        type="reflected_xss",
        status=FindingStatus.SUSPECTED,
        severity_auto=Severity.MEDIUM,
        target=FindingTarget(url="https://example.com/search", endpoint="/search", method="GET", parameter="q"),
        evidence=Evidence(
            request_id="req1",
            test_id="test1",
            observed_behavior="reflechi",
            evidence_summary="<script>alert('m')</script>",
        ),
        scoring=Scoring(impact=3, exploitability=4, scope=2, raw_score=9),
        metadata=FindingMetadata(module="sigxss", timestamp=NOW, confidence=ConfidenceLevel.CORROBORATED),
    )
    return ReportModel(
        header=header,
        configuration=configuration,
        termination=TerminationReason(trigger=TerminationTrigger.COMPLETED_NORMALLY),
        statistics=ScanStatistics(total_requests=5),
        tests=(),
        findings=(finding,),
    )


def test_export_produces_valid_json(tmp_path: Path) -> None:
    output_path = tmp_path / "report.json"
    JsonReportExporter().export(report=_report(), format_name="json", output_path=output_path)

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["header"]["scan_id"] == "scan1"
    assert data["header"]["preset"] == "prod-safe"


def test_finding_severity_is_exposed_directly(tmp_path: Path) -> None:
    output_path = tmp_path / "report.json"
    JsonReportExporter().export(report=_report(), format_name="json", output_path=output_path)

    data = json.loads(output_path.read_text(encoding="utf-8"))
    finding_data = data["findings"][0]
    assert finding_data["severity"] == "medium"
    assert finding_data["severity_auto"] == "medium"


def test_computed_sections_are_present(tmp_path: Path) -> None:
    output_path = tmp_path / "report.json"
    JsonReportExporter().export(report=_report(), format_name="json", output_path=output_path)

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["findings_by_severity"] == {"critical": 0, "high": 0, "medium": 1, "low": 0}
    assert "requests_by_module" in data
    assert "tests_by_type" in data


def test_wrong_format_name_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="markdown"):
        JsonReportExporter().export(report=_report(), format_name="markdown", output_path=tmp_path / "x.json")


def test_evidence_summary_stays_redacted_in_export(tmp_path: Path) -> None:
    output_path = tmp_path / "report.json"
    JsonReportExporter().export(report=_report(), format_name="json", output_path=output_path)

    raw_text = output_path.read_text(encoding="utf-8")
    # le finding de test ne contient pas de secret brut par construction ;
    # verifie simplement que l'extrait deja expurge est bien celui exporte tel quel.
    assert "<script>alert('m')</script>" in raw_text


def test_compiled_regex_patterns_in_scope_are_serializable(tmp_path: Path) -> None:
    """Le profil de scope "standard" (preset staging-full) porte un
    `blocked_url_patterns` non vide — des `re.Pattern` compiles par
    `domain.targets.scope.build_scope` (Phase 1), pas serialisables par
    `json.dumps` sans traitement dedie."""
    entry_url = normalize_url("https://example.com/")
    configuration = resolve_preset(PresetName.STAGING_FULL, entry_url=entry_url)
    assert configuration.scope.blocked_url_patterns  # sanity : le cas est bien exerce
    header = build_report_header(
        scan_id="scan2",
        version="0.1.0",
        target_url="https://example.com/",
        configuration=configuration,
        catalog_versions={},
        verify_tls=True,
        now=NOW,
    )
    report = ReportModel(
        header=header,
        configuration=configuration,
        termination=TerminationReason(trigger=TerminationTrigger.COMPLETED_NORMALLY),
        statistics=ScanStatistics(),
    )

    output_path = tmp_path / "report2.json"
    JsonReportExporter().export(report=report, format_name="json", output_path=output_path)

    data = json.loads(output_path.read_text(encoding="utf-8"))
    patterns = data["configuration"]["scope"]["blocked_url_patterns"]
    assert patterns
    assert all(isinstance(pattern, str) for pattern in patterns)
