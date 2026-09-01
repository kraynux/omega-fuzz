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
from omega_fuzz.domain.scans.scan import Scan
from omega_fuzz.domain.scans.scan_id import ScanId
from omega_fuzz.domain.scans.scan_status import ScanStatus
from omega_fuzz.infrastructure.storage.sqlite.connection import open_connection
from omega_fuzz.infrastructure.storage.sqlite.finding_repository import SqliteFindingRepository
from omega_fuzz.infrastructure.storage.sqlite.scan_repository import SqliteScanRepository

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _repositories(tmp_path: Path) -> tuple[SqliteScanRepository, SqliteFindingRepository]:
    connection = open_connection(tmp_path / "test.db")
    return SqliteScanRepository(connection), SqliteFindingRepository(connection)


def _finding(*, finding_id: str, scan_id: str, severity_override: Severity | None = None) -> Finding:
    return Finding(
        finding_id=finding_id,
        scan_id=scan_id,
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
        cwe="CWE-79",
        recommendations=("Echapper la sortie",),
        severity_override=severity_override,
        severity_override_reason="confirme manuellement" if severity_override else None,
    )


def _seed_scan(scan_repo: SqliteScanRepository, scan_id: str) -> None:
    scan_repo.save(
        Scan(scan_id=ScanId(scan_id), target_id="example_root", status=ScanStatus.RUNNING, created_at=NOW)
    )


def test_save_and_list_for_scan_round_trip(tmp_path: Path) -> None:
    scan_repo, finding_repo = _repositories(tmp_path)
    scan_id = "a1b2c3d4e5f64a7b8c9d0e1f2a3b4c5d"
    _seed_scan(scan_repo, scan_id)
    finding = _finding(finding_id="finding_1", scan_id=scan_id)
    finding_repo.save(finding)

    loaded = finding_repo.list_for_scan(scan_id)
    assert len(loaded) == 1
    result = loaded[0]
    assert result.finding_id == "finding_1"
    assert result.target == finding.target
    assert result.evidence == finding.evidence
    assert result.scoring == finding.scoring
    assert result.metadata.module == "sigxss"
    assert result.metadata.confidence is ConfidenceLevel.CORROBORATED
    assert result.cwe == "CWE-79"
    assert result.recommendations == ("Echapper la sortie",)
    assert result.severity is Severity.MEDIUM


def test_severity_override_round_trips(tmp_path: Path) -> None:
    scan_repo, finding_repo = _repositories(tmp_path)
    scan_id = "b1b2c3d4e5f64a7b8c9d0e1f2a3b4c5d"
    _seed_scan(scan_repo, scan_id)
    finding = _finding(finding_id="finding_1", scan_id=scan_id, severity_override=Severity.HIGH)
    finding_repo.save(finding)

    loaded = finding_repo.list_for_scan(scan_id)[0]
    assert loaded.severity_override is Severity.HIGH
    assert loaded.severity_override_reason == "confirme manuellement"
    assert loaded.severity is Severity.HIGH


def test_clear_for_scan_only_removes_that_scan(tmp_path: Path) -> None:
    scan_repo, finding_repo = _repositories(tmp_path)
    scan_a, scan_b = "c1b2c3d4e5f64a7b8c9d0e1f2a3b4c5d", "d1b2c3d4e5f64a7b8c9d0e1f2a3b4c5d"
    _seed_scan(scan_repo, scan_a)
    _seed_scan(scan_repo, scan_b)
    finding_repo.save(_finding(finding_id="finding_a", scan_id=scan_a))
    finding_repo.save(_finding(finding_id="finding_b", scan_id=scan_b))

    finding_repo.clear_for_scan(scan_a)

    assert finding_repo.list_for_scan(scan_a) == []
    assert len(finding_repo.list_for_scan(scan_b)) == 1


def test_list_for_scan_empty_when_no_findings(tmp_path: Path) -> None:
    scan_repo, finding_repo = _repositories(tmp_path)
    scan_id = "e1b2c3d4e5f64a7b8c9d0e1f2a3b4c5d"
    _seed_scan(scan_repo, scan_id)
    assert finding_repo.list_for_scan(scan_id) == []
