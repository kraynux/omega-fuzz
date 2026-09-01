# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

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
from omega_fuzz.infrastructure.exporters.markdown_exporter import MarkdownReportExporter

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)

_EXPECTED_SECTION_HEADINGS = (
    "# Rapport OMEGA-FUZZ",
    "## Resume executif",
    "## Cible et scan ID",
    "## Preset, profils et surcharges",
    "## Scope effectif et exclusions",
    "## Limites configurees",
    "## Raison de terminaison",
    "## Statistiques de requetes",
    "## Statistiques de tests",
    "## Findings par severite",
    "## Detail des findings",
    "## Annexes techniques",
)


def _report(*, verify_tls: bool = True, trigger: TerminationTrigger = TerminationTrigger.COMPLETED_NORMALLY) -> ReportModel:
    entry_url = normalize_url("https://example.com/")
    configuration = resolve_preset(PresetName.PROD_SAFE, entry_url=entry_url)
    header = build_report_header(
        scan_id="scan1",
        version="0.1.0",
        target_url="https://example.com/",
        configuration=configuration,
        catalog_versions={"xss": "1.0.0"},
        verify_tls=verify_tls,
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
            request_id="req1", test_id="test1", observed_behavior="reflechi", evidence_summary="extrait"
        ),
        scoring=Scoring(impact=3, exploitability=4, scope=2, raw_score=9),
        metadata=FindingMetadata(module="sigxss", timestamp=NOW, confidence=ConfidenceLevel.CORROBORATED),
    )
    termination = TerminationReason(
        trigger=trigger,
        limit_name="max_total_requests" if trigger is TerminationTrigger.LIMIT_REACHED else None,
        configured_value=1000 if trigger is TerminationTrigger.LIMIT_REACHED else None,
        observed_value=1000 if trigger is TerminationTrigger.LIMIT_REACHED else None,
    )
    return ReportModel(
        header=header,
        configuration=configuration,
        termination=termination,
        statistics=ScanStatistics(total_requests=5),
        tests=(),
        findings=(finding,),
    )


def test_all_twelve_sections_present(tmp_path: Path) -> None:
    output_path = tmp_path / "report.md"
    MarkdownReportExporter().export(report=_report(), format_name="markdown", output_path=output_path)

    text = output_path.read_text(encoding="utf-8")
    for heading in _EXPECTED_SECTION_HEADINGS:
        assert heading in text, heading


def test_tls_banner_hidden_when_verification_enabled(tmp_path: Path) -> None:
    output_path = tmp_path / "report.md"
    MarkdownReportExporter().export(report=_report(verify_tls=True), format_name="markdown", output_path=output_path)

    text = output_path.read_text(encoding="utf-8")
    assert "DESACTIVEE" not in text
    assert "ATTENTION" not in text


def test_tls_banner_shown_when_verification_disabled(tmp_path: Path) -> None:
    output_path = tmp_path / "report.md"
    MarkdownReportExporter().export(report=_report(verify_tls=False), format_name="markdown", output_path=output_path)

    text = output_path.read_text(encoding="utf-8")
    assert "DESACTIVEE" in text
    assert "ATTENTION" in text


def test_termination_reason_is_readable_for_limit_reached(tmp_path: Path) -> None:
    output_path = tmp_path / "report.md"
    MarkdownReportExporter().export(
        report=_report(trigger=TerminationTrigger.LIMIT_REACHED), format_name="markdown", output_path=output_path
    )

    text = output_path.read_text(encoding="utf-8")
    assert "max_total_requests" in text
    assert "1000" in text


def test_finding_detail_includes_id_and_evidence(tmp_path: Path) -> None:
    output_path = tmp_path / "report.md"
    MarkdownReportExporter().export(report=_report(), format_name="markdown", output_path=output_path)

    text = output_path.read_text(encoding="utf-8")
    assert "finding_1" in text
    assert "extrait" in text
