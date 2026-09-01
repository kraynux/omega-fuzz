# Copyright (c) 2026 kraynux - Licence MIT
"""Conversions pures entre modeles domaine et lignes SQLite
(OMEGA-FUZZ_ARBORESCENCE.md §20). Les value objects imbriques
(`Finding.target`/`evidence`/`scoring`/`metadata`) sont serialises en
JSON — voir la decision de schema simplifie dans `schema.py`."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any

from omega_lib.core.confidence import ConfidenceLevel

from omega_fuzz.domain.findings.evidence import Evidence
from omega_fuzz.domain.findings.finding import Finding
from omega_fuzz.domain.findings.finding_metadata import FindingMetadata
from omega_fuzz.domain.findings.finding_status import FindingStatus
from omega_fuzz.domain.findings.finding_target import FindingTarget
from omega_fuzz.domain.findings.scoring import Scoring
from omega_fuzz.domain.findings.severity import Severity
from omega_fuzz.domain.reports.termination import TerminationReason, TerminationTrigger
from omega_fuzz.domain.scans.scan import Scan
from omega_fuzz.domain.scans.scan_id import ScanId
from omega_fuzz.domain.scans.scan_state import ScanState
from omega_fuzz.domain.scans.scan_status import ScanStatus


def _isoformat_or_none(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _from_isoformat_or_none(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value is not None else None


def scan_to_row(scan: Scan) -> dict[str, Any]:
    termination = scan.termination_reason
    return {
        "scan_id": scan.scan_id.value,
        "target_id": scan.target_id,
        "status": scan.status.value,
        "created_at": scan.created_at.isoformat(),
        "started_at": _isoformat_or_none(scan.started_at),
        "completed_at": _isoformat_or_none(scan.completed_at),
        "termination_trigger": termination.trigger.value if termination is not None else None,
        "termination_limit_name": termination.limit_name if termination is not None else None,
        "termination_configured_value": termination.configured_value if termination is not None else None,
        "termination_observed_value": termination.observed_value if termination is not None else None,
    }


def row_to_scan(row: sqlite3.Row) -> Scan:
    termination_reason: TerminationReason | None = None
    if row["termination_trigger"] is not None:
        termination_reason = TerminationReason(
            trigger=TerminationTrigger(row["termination_trigger"]),
            limit_name=row["termination_limit_name"],
            configured_value=row["termination_configured_value"],
            observed_value=row["termination_observed_value"],
        )
    return Scan(
        scan_id=ScanId(row["scan_id"]),
        target_id=row["target_id"],
        status=ScanStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        started_at=_from_isoformat_or_none(row["started_at"]),
        completed_at=_from_isoformat_or_none(row["completed_at"]),
        termination_reason=termination_reason,
    )


def scan_state_to_row(state: ScanState) -> dict[str, Any]:
    return {
        "scan_id": state.scan_id,
        "status": state.status.value,
        "pending_discovery_urls": json.dumps(list(state.pending_discovery_urls)),
        "completed_test_ids": json.dumps(sorted(state.completed_test_ids)),
    }


def row_to_scan_state(row: sqlite3.Row) -> ScanState:
    return ScanState(
        scan_id=row["scan_id"],
        status=ScanStatus(row["status"]),
        pending_discovery_urls=tuple(json.loads(row["pending_discovery_urls"])),
        completed_test_ids=frozenset(json.loads(row["completed_test_ids"])),
    )


def finding_to_row(finding: Finding) -> dict[str, Any]:
    target_json = json.dumps(
        {
            "url": finding.target.url,
            "endpoint": finding.target.endpoint,
            "method": finding.target.method,
            "parameter": finding.target.parameter,
        }
    )
    evidence_json = json.dumps(
        {
            "request_id": finding.evidence.request_id,
            "test_id": finding.evidence.test_id,
            "observed_behavior": finding.evidence.observed_behavior,
            "evidence_summary": finding.evidence.evidence_summary,
            "truncated": finding.evidence.truncated,
        }
    )
    scoring_json = json.dumps(
        {
            "impact": finding.scoring.impact,
            "exploitability": finding.scoring.exploitability,
            "scope": finding.scoring.scope,
            "raw_score": finding.scoring.raw_score,
        }
    )
    metadata_json = json.dumps(
        {
            "module": finding.metadata.module,
            "timestamp": finding.metadata.timestamp.isoformat(),
            "confidence": finding.metadata.confidence.value,
        }
    )
    return {
        "finding_id": finding.finding_id,
        "scan_id": finding.scan_id,
        "title": finding.title,
        "type": finding.type,
        "status": finding.status.value,
        "severity_auto": finding.severity_auto.value,
        "severity_override": finding.severity_override.value if finding.severity_override is not None else None,
        "severity_override_reason": finding.severity_override_reason,
        "description": finding.description,
        "impact": finding.impact,
        "recommendations": json.dumps(list(finding.recommendations)),
        "references_json": json.dumps(list(finding.references)),
        "cwe": finding.cwe,
        "owasp_category": finding.owasp_category,
        "target_json": target_json,
        "evidence_json": evidence_json,
        "scoring_json": scoring_json,
        "metadata_json": metadata_json,
    }


def row_to_finding(row: sqlite3.Row) -> Finding:
    target = json.loads(row["target_json"])
    evidence = json.loads(row["evidence_json"])
    scoring = json.loads(row["scoring_json"])
    metadata = json.loads(row["metadata_json"])

    return Finding(
        finding_id=row["finding_id"],
        scan_id=row["scan_id"],
        title=row["title"],
        type=row["type"],
        status=FindingStatus(row["status"]),
        severity_auto=Severity(row["severity_auto"]),
        target=FindingTarget(**target),
        evidence=Evidence(**evidence),
        scoring=Scoring(**scoring),
        metadata=FindingMetadata(
            module=metadata["module"],
            timestamp=datetime.fromisoformat(metadata["timestamp"]),
            confidence=ConfidenceLevel(metadata["confidence"]),
        ),
        description=row["description"] or "",
        impact=row["impact"] or "",
        recommendations=tuple(json.loads(row["recommendations"])),
        references=tuple(json.loads(row["references_json"])),
        cwe=row["cwe"],
        owasp_category=row["owasp_category"],
        severity_override=Severity(row["severity_override"]) if row["severity_override"] is not None else None,
        severity_override_reason=row["severity_override_reason"],
    )
