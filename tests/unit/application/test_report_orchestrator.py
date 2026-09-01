# Copyright (c) 2026 kraynux - Licence MIT
"""`build_scan_report` (Phase 10a) est un assemblage fin : verifie que
le `ReportModel` produit reprend fidelement chaque entree fournie,
sans recalcul ni perte d'information."""
from __future__ import annotations

from datetime import datetime, timezone

from omega_fuzz.application.services.report_orchestrator import build_scan_report
from omega_fuzz.domain.profiles.preset import PresetName
from omega_fuzz.domain.reports.scan_statistics import ScanStatistics
from omega_fuzz.domain.reports.termination import TerminationReason, TerminationTrigger
from omega_fuzz.domain.scans.scan import Scan
from omega_fuzz.domain.scans.scan_id import ScanId
from omega_fuzz.domain.scans.scan_status import ScanStatus
from omega_fuzz.domain.services.profile_resolution_service import resolve_preset
from omega_fuzz.domain.services.url_normalization_service import normalize_url

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_build_scan_report_assembles_report_model() -> None:
    entry_url = normalize_url("https://example.com/")
    configuration = resolve_preset(PresetName.PROD_SAFE, entry_url=entry_url)
    scan = Scan(
        scan_id=ScanId("scan-report-test"),
        target_id="example_root",
        status=ScanStatus.COMPLETED,
        created_at=NOW,
        started_at=NOW,
        completed_at=NOW,
    )
    termination = TerminationReason(trigger=TerminationTrigger.COMPLETED_NORMALLY)
    statistics = ScanStatistics(total_requests=7)

    report = build_scan_report(
        scan=scan,
        target_url="https://example.com/",
        version="0.1.0",
        configuration=configuration,
        termination=termination,
        tests=(),
        findings=(),
        statistics=statistics,
        catalog_versions={"xss": "1.0.0"},
        verify_tls=True,
        now=NOW,
    )

    assert report.header.scan_id == "scan-report-test"
    assert report.header.target_url == "https://example.com/"
    assert report.header.preset == "prod-safe"
    assert report.header.catalog_versions == {"xss": "1.0.0"}
    assert report.configuration is configuration
    assert report.termination is termination
    assert report.statistics is statistics
