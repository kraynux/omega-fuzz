# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

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
from omega_fuzz.infrastructure.exporters.html_exporter.html_exporter import HtmlReportExporter

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)

_EXPECTED_SECTION_HEADINGS = (
    "<h1>Rapport OMEGA-FUZZ</h1>",
    "<h2>Resume executif</h2>",
    "<h2>Cible et scan ID</h2>",
    "<h2>Preset, profils et surcharges</h2>",
    "<h2>Scope effectif et exclusions</h2>",
    "<h2>Limites configurees</h2>",
    "<h2>Raison de terminaison</h2>",
    "<h2>Statistiques de requetes</h2>",
    "<h2>Statistiques de tests</h2>",
    "<h2>Findings par severite</h2>",
    "<h2>Detail des findings</h2>",
    "<h2>Annexes techniques</h2>",
)


def _report(*, verify_tls: bool = True, evidence_summary: str = "extrait") -> ReportModel:
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
            request_id="req1", test_id="test1", observed_behavior="reflechi", evidence_summary=evidence_summary
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


def test_all_twelve_sections_present(tmp_path: Path) -> None:
    output_path = tmp_path / "report.html"
    HtmlReportExporter().export(report=_report(), format_name="html", output_path=output_path)

    text = output_path.read_text(encoding="utf-8")
    for heading in _EXPECTED_SECTION_HEADINGS:
        assert heading in text, heading


def test_tls_banner_hidden_when_verification_enabled(tmp_path: Path) -> None:
    output_path = tmp_path / "report.html"
    HtmlReportExporter().export(report=_report(verify_tls=True), format_name="html", output_path=output_path)

    text = output_path.read_text(encoding="utf-8")
    assert "DESACTIVEE" not in text
    assert "ATTENTION" not in text


def test_tls_banner_shown_when_verification_disabled(tmp_path: Path) -> None:
    output_path = tmp_path / "report.html"
    HtmlReportExporter().export(report=_report(verify_tls=False), format_name="html", output_path=output_path)

    text = output_path.read_text(encoding="utf-8")
    assert "DESACTIVEE" in text
    assert "ATTENTION" in text


def test_evidence_summary_is_autoescaped(tmp_path: Path) -> None:
    """Le catalogue XSS de la Phase 7b capture des payloads du type
    <script>...</script> tels quels dans evidence_summary — sans
    echappement automatique, le rapport HTML deviendrait lui-meme
    vulnerable au contenu qu'il documente."""
    output_path = tmp_path / "report.html"
    HtmlReportExporter().export(
        report=_report(evidence_summary="<script>alert('omegafuzz-marker')</script>"),
        format_name="html",
        output_path=output_path,
    )

    text = output_path.read_text(encoding="utf-8")
    assert "<script>alert('omegafuzz-marker')</script>" not in text
    assert "&lt;script&gt;" in text


def test_wrong_format_name_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="markdown"):
        HtmlReportExporter().export(report=_report(), format_name="markdown", output_path=tmp_path / "x.html")
